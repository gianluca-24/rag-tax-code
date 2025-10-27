from io import TextIOWrapper
import json
import os
import zipfile
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
from config_backend import EMBED_MODEL, CHAT_MODEL, N_RESULTS

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client_ai = OpenAI(api_key=OPENAI_KEY)
# create a new conversation
sessions = {}

# Open persistent Chroma DB
client_db = chromadb.PersistentClient(path="../data/db")
collection = client_db.get_collection("db_taxcode")


def get_query_embedding(text: str):
    text = text.replace("\n", " ")
    return client_ai.embeddings.create(
        input=[text],
        model=EMBED_MODEL
    ).data[0].embedding


def semantic_search(query: str, n_results: int = 3):
    query_emb = get_query_embedding(query)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=n_results
    )
    docs = []
    for doc, meta, score in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
        docs.append({
            "text": doc,
            "metadata": meta,
            "similarity": score
        })
    return docs


# def generate_prompt(query: str, docs: list):
#     prompt = f"Sei un esperto del sistema fiscale italiano. In base ai seguenti documenti, genera una risposta:\n '{query}'\n\n"
#     for i, doc in enumerate(docs):
#         meta = doc['metadata']
#         print(meta)

#         prompt += f"{doc['metadata']} (Similarity: {doc['similarity']:.4f}):\n{doc['text']}\n\n"
#     prompt += "Fornisci una risposta citando la sezione, eventuale quadro di riferimento, ed il fascicolo. Non fornire altre informazioni o domande."
#     return prompt


# Generate chat messages with system role, few-shot examples, and user query
def generate_chat_messages(query: str, docs: list, examples: list = None):
    messages = []
    #System role: set context + formatting expectations
    messages.append({
        "role": "developer",
        "content": (
            "Sei un esperto del sistema fiscale italiano. "
            "Usa SOLO i documenti forniti per rispondere alle domande. "
            "Cita sempre le fonti (sezione, quadro, fascicolo, pagina) per ogni informazione fornita. "
        )
    })
    #Few-shot examples (as assistant + user pairs)
    if examples:
        for ex in examples:
            messages.append({
                "role": "user",
                "content": f"Domanda: {ex['question']}"
            })
            messages.append({
                "role": "assistant",
                "content": json.dumps(ex["answer"], ensure_ascii=False, indent=2)
            })

    #Add retrieved documents as context
    context_text = "Documenti rilevanti:\n\n"
    for i, doc in enumerate(docs):
        context_text += f"(similarità {doc['similarity']:.4f}):\n{doc['text']}\n metadati: {doc['metadata']}\n\n"

    #User question (final)
    messages.append({
        "role": "developer",
        "content": f"{context_text}\n"
    })
    messages.append({
        "role": "user",
        "content": f"Domanda: '{query}' Usa i riferimenti ai documenti forniti."
    })

    return messages


def answer_question(query, docs, examples=None, session_id=None):
    if session_id not in sessions:
        print("Creating new conversation for session:", session_id)
        sessions[session_id] = client_ai.conversations.create()
    conversation = sessions[session_id]
    
    prompt_text = generate_chat_messages(query, docs, examples)
    response = client_ai.responses.create(
        model=CHAT_MODEL,
        conversation=conversation.id,
        input=prompt_text,
        instructions="Rispondi citando le fonti e non aggiungere suggerimenti o richieste extra."
    )
    return response.output_text

def process_zip_transactions(zip_file) -> pd.DataFrame:
    """
    Reads all CSV/TXT files from a ZIP, concatenates them, fills NaNs, 
    parses datetime, sorts, and returns a clean DataFrame.
    """
    all_dfs = []
    with zipfile.ZipFile(zip_file, "r") as z:
        for name in z.namelist():
            if name.endswith(".csv") or name.endswith(".txt"):
                with z.open(name) as f:
                    df = pd.read_csv(TextIOWrapper(f, encoding="latin1"))
                    all_dfs.append(df)

    if not all_dfs:
        raise ValueError("Nessun file CSV trovato nello zip.")

    # Concatenate, clean, and sort
    full_df = pd.concat(all_dfs, ignore_index=True)
    full_df = full_df.fillna(0)
    full_df['datetime_tz_CET'] = pd.to_datetime(full_df['datetime_tz_CET'], utc=True, errors='coerce')
    full_df = full_df.dropna(subset=['datetime_tz_CET'])
    full_df = full_df.sort_values('datetime_tz_CET').reset_index(drop=True)

    return full_df

import pandas as pd
from collections import defaultdict

def calculate_gain(transactions_df: pd.DataFrame) -> float:
    """
    Compute crypto capital gains using FIFO, aggregated per year.
    Returns a dict like: {2023: 152.4, 2024: -32.8, ...}
    """
    gain_by_year = defaultdict(float)
    holdings = defaultdict(list)  # currency -> list of FIFO lots

    # Ensure chronological order
    transactions_df = transactions_df.sort_values("datetime_tz_CET")

    for _, row in transactions_df.iterrows():
        t_type = row["type"]
        sent_amt, sent_cur = row["sent_amount"], row["sent_currency"]
        recv_amt, recv_cur = row["received_amount"], row["received_currency"]
        sent_val, recv_val = row["sent_value_EUR"], row["received_value_EUR"]
        fee_val = row["fee_value_EUR"]
        year = pd.to_datetime(row["datetime_tz_CET"]).year  # Extract year

        # --- Handle acquisitions ---
        if t_type in ["Receive", "Buy", "Reward", "Payment"]:
            if recv_amt and recv_cur:
                unit_cost = recv_val / recv_amt if recv_amt > 0 else 0
                holdings[recv_cur].append({"amount": recv_amt, "unit_cost": unit_cost})

        # --- Handle trades ---
        elif t_type == "Trade":
            # Disposal side
            if sent_amt and sent_cur:
                remaining = sent_amt
                cost_basis = 0.0
                fifo = holdings[sent_cur]

                while remaining > 0 and fifo:
                    lot = fifo[0]
                    if remaining >= lot["amount"]:
                        cost_basis += lot["amount"] * lot["unit_cost"]
                        remaining -= lot["amount"]
                        fifo.pop(0)
                    else:
                        cost_basis += remaining * lot["unit_cost"]
                        lot["amount"] -= remaining
                        remaining = 0

                gain = recv_val - cost_basis - fee_val
                gain_by_year[year] += gain

            # Acquisition side
            if recv_amt and recv_cur:
                unit_cost = recv_val / recv_amt if recv_amt > 0 else 0
                holdings[recv_cur].append({"amount": recv_amt, "unit_cost": unit_cost})

        # --- Handle sales (to fiat) ---
        elif t_type == "Sell":
            if sent_amt and sent_cur:
                remaining = sent_amt
                cost_basis = 0.0
                fifo = holdings[sent_cur]

                while remaining > 0 and fifo:
                    lot = fifo[0]
                    if remaining >= lot["amount"]:
                        cost_basis += lot["amount"] * lot["unit_cost"]
                        remaining -= lot["amount"]
                        fifo.pop(0)
                    else:
                        cost_basis += remaining * lot["unit_cost"]
                        lot["amount"] -= remaining
                        remaining = 0

                gain = sent_val - cost_basis - fee_val
                gain_by_year[year] += gain

    # Round all yearly totals
    return {yr: round(val, 2) for yr, val in gain_by_year.items()}