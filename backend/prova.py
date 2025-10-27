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

# Get embedding for the query
def get_query_embedding(text: str):
    text = text.replace("\n", " ")
    return client_ai.embeddings.create(
        input=[text],
        model=EMBED_MODEL
    ).data[0].embedding

# Semantic search in the vector DB
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


examples = [
    {
        "question": "Quali sono gli obblighi di monitoraggio fiscale nel quadro RW?",
        "answer": "I soggetti residenti devono indicare nel quadro RW gli investimenti e le attività estere di natura finanziaria detenute all'estero. \n Fonti: Sezione Monitoraggio fiscale, Quadro: RW, Fascicolo: 1 , Pagina: 15 "
    },
    {
        "question": "Come si calcola l'IVAFE per i conti correnti esteri?",
        "answer": "L'IVAFE è dovuta in misura proporzionale al valore medio di giacenza dei conti correnti esteri, applicando l'aliquota dello 0,2%. \n Fonti:  Sezione: IVAFE, Quadro RW, fascicolo: 2, Pagina: 22 "
    }
]



# create a new conversation
conversation = client_ai.conversations.create()

# Generate LLM answer based on retrieved docs
def answer_question(query: str, docs: list, examples: list = None, conversation: str = conversation):
    prompt_text = generate_chat_messages(query, docs, examples)

    response = client_ai.responses.create(
        model=CHAT_MODEL,
        conversation= conversation.id,
        input = prompt_text,
        instructions = "Rispondi citando le fonti e non aggiungere suggerimenti o richieste extra."
    )
    print(response)
    print("\n\n\n")
    # Extract JSON content safely
    content = response.output_text
    return content

# Example usage
query = "Come si dichiarano gli affitti brevi con cedulare secca?"
n_results = 5

# Step 1: Retrieve relevant docs from the vector DB
docs = semantic_search(query, 5)

# Step 2: Generate LLM answer based on retrieved docs
answer = answer_question(query, docs, examples, conversation)

print(json.dumps(answer, indent=2, ensure_ascii=False))