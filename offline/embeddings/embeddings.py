from dotenv import load_dotenv
import os
import json
from openai import OpenAI
from tqdm import tqdm

def get_embedding(text, client, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")  # make sure your .env has OPENAI_KEY=sk-xxxx
client = OpenAI(api_key=openai_api_key)

with open("../data/json/fascicolo_final_chunks.json", "r", encoding="utf-8") as f:
    all_chunks = json.load(f)

for chunk in tqdm(all_chunks):
    text = chunk["chunk_text"]
    embedding_response = get_embedding(text, client)
    chunk["embedding"] = embedding_response  # store the embedding in your JSON object

with open("../data/json/embeddings.json", "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=2)

print(f"✅ Created embeddings for {len(all_chunks)} chunks")