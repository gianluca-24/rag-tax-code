import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from config_backend import EMBED_MODEL, CHAT_MODEL, N_RESULTS
import json

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

def generate_chat_messages(query: str, docs: list, examples: list = None):
    messages = []
    #System role: set context + formatting expectations
    messages.append({
        "role": "system",
        "content": (
            "Sei un esperto del sistema fiscale italiano. "
            "Usa SOLO i documenti forniti per rispondere alle domande. "
            "Rispondi in formato JSON con la seguente struttura:\n\n"
            "{\n"
            '  "answer": "testo della risposta",\n'
            '  "references": [\n'
            '    {"document": n, "section": "...", "quadro": "...", "fascicolo": "..."}\n'
            '  ]\n'
            "}\n\n"
            "Non includere testo fuori dal JSON."
        )
    })
    # #Few-shot examples (as assistant + user pairs)
    # if examples:
    #     for ex in examples:
    #         messages.append({
    #             "role": "user",
    #             "content": f"Domanda: {ex['question']}"
    #         })
    #         messages.append({
    #             "role": "assistant",
    #             "content": json.dumps(ex["answer"], ensure_ascii=False, indent=2)
    #         })

    #Add retrieved documents as context
    context_text = "Documenti rilevanti:\n\n"
    for i, doc in enumerate(docs):
        context_text += f"Documento {i+1} (similarità {doc['similarity']:.4f}):\n{doc['text']}\n\n"

    #User question (final)
    messages.append({
        "role": "user",
        "content": f"{context_text}\nDomanda: '{query}'\nRispondi solo in JSON valido. Usa i riferimenti ai documenti forniti."
    })

    return messages


examples = [
    {
        "question": "Quali sono gli obblighi di monitoraggio fiscale nel quadro RW?",
        "answer": {
            "answer": "I soggetti residenti devono indicare nel quadro RW gli investimenti e le attività estere di natura finanziaria detenute all'estero.",
            "references": [
                {"document": 1, "section": "Monitoraggio fiscale", "quadro": "RW", "fascicolo": "1"}
            ]
        }
    },
    {
        "question": "Come si calcola l'IVAFE per i conti correnti esteri?",
        "answer": {
            "answer": "L'IVAFE è dovuta in misura proporzionale al valore medio di giacenza dei conti correnti esteri, applicando l'aliquota dello 0,2%.",
            "references": [
                {"document": 2, "section": "IVAFE", "quadro": "RW", "fascicolo": "2"}
            ]
        }
    }
]

def answer_question(query: str, docs: list, examples: list = None):
    prompt_text = generate_chat_messages(query, docs, examples)

    response = client_ai.chat.completions.create(
        model=CHAT_MODEL,
        messages=prompt_text,
        response_format={"type": "json_object"}
    )
    print(response)
    # Extract JSON content safely
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("Warning: response was not valid JSON. Raw output returned.")
        return content

# Example usage
query = "Come compilare il quadro RW per investimenti esteri?"
n_results = 10

# Step 1: Retrieve relevant docs from the vector DB
docs = semantic_search(query, n_results)

# Step 2: Generate LLM answer based on retrieved docs
answer = answer_question(query, docs, examples)

print(json.dumps(answer, indent=2, ensure_ascii=False))