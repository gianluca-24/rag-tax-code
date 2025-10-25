import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

def generate_prompt(query, docs):
    prompt = f"Sei un esperto del sistema fiscale italiano. In base ai seguenti documenti, genera una risposta:\n '{query}'\n\n"
    for i, doc in enumerate(docs):
        prompt += f"Documento {i+1} (Similarity: {doc['similarity']:.4f}):\n{doc['text']}\n\n"
    prompt += "Fornisci una risposta citando la sezione, eventuale quadro di riferimento, ed il fascicolo. Non fornire nessun altro tipo di informazione, ne fai domande all'utente.\n"
    return prompt

def answer_question(query, docs, client_ai):
    prompt_text = generate_prompt(query, docs)  # build as above
    response = client_ai.chat.completions.create(
        model="gpt-5-nano-2025-08-07",
        messages=[{"role": "user", "content": prompt_text}]
    )
    return response.choices[0].message.content

def semantic_search(query, client_ai, collection, n_results=3):
    # Embed the query
    query_embedding = get_query_embedding(query, client_ai)
    
    # Search Chroma DB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    # Extract relevant information
    docs = []
    for doc, meta, score in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
        docs.append({
            "text": doc,
            "metadata": meta,
            "similarity": score
        })
    return docs

def get_query_embedding(text, client):
    text = text.replace("\n", " ")
    return client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    ).data[0].embedding

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")  # make sure your .env has OPENAI_KEY=sk-xxxx
client_ai = OpenAI(api_key=openai_api_key)

# Step 1: Reopen the same database folder
client_db = chromadb.PersistentClient(path="./data/db")

# Step 2: Get your existing collection
collection = client_db.get_collection("db_taxcode")

query = 'Come si compila il quadro RA del fascicolo 1?'  # Example query

docs = semantic_search(query, client_ai, collection)

# TODO
# create prompt, where ask to explain the answer based on the retrieved documents, citing page numbers and sections
answer = answer_question(query, docs, client_ai)

print("Answer:\n", answer)