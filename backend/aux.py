from io import TextIOWrapper
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
        n_results=N_RESULTS
    )
    docs = []
    for doc, meta, score in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
        docs.append({
            "text": doc,
            "metadata": meta,
            "similarity": score
        })
    return docs


def generate_prompt(query: str, docs: list):
    prompt = f"Sei un esperto del sistema fiscale italiano. In base ai seguenti documenti, genera una risposta:\n '{query}'\n\n"
    for i, doc in enumerate(docs):
        prompt += f"Documento {i+1} (Similarity: {doc['similarity']:.4f}):\n{doc['text']}\n\n"
    prompt += "Fornisci una risposta citando la sezione, eventuale quadro di riferimento, ed il fascicolo. Non fornire altre informazioni o domande."
    return prompt


def answer_question(query: str, docs: list):
    prompt_text = generate_prompt(query, docs)
    response = client_ai.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt_text}]
    )
    return response.choices[0].message.content



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