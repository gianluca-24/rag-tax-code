from dotenv import load_dotenv
import os
import json
import chromadb
from openai import OpenAI
from tqdm import tqdm

load_dotenv()

# Ensure your .env has: OPENAI_API_KEY=sk-xxxx
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Initialize persistent Chroma database
chroma_client = chromadb.PersistentClient(path="../db")

# Create or get your RAG collection
collection_name = "db_taxcode"
collection = chroma_client.get_or_create_collection(name=collection_name)


def get_embedding(text, client, model="text-embedding-3-small"):
    """Generate an embedding vector for a given text."""
    text = text.replace("\n", " ")
    response = client.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding

with open("../data/json/fascicolo_final_chunks.json", "r", encoding="utf-8") as f:
    all_chunks = json.load(f)

ids, documents, metadatas, embeddings = [], [], [], []

for chunk in tqdm(all_chunks):
    chunk_id = str(chunk["id"])
    text = chunk["chunk_text"]
    metadata = chunk["metadata"]

    # Generate embedding
    embedding = get_embedding(text, client)

    ids.append(chunk_id)
    documents.append(text)
    metadatas.append(metadata)
    embeddings.append(embedding)

# Add all chunks to persistent Chroma collection
collection.add(
    ids=ids,
    embeddings=embeddings,
    documents=documents,
    metadatas=metadatas
)

print(f"✅ Added {len(ids)} chunks to persistent collection '{collection_name}'")
print("📦 Data stored in:", os.path.abspath("../db"))
print("Total documents in collection:", collection.count())

