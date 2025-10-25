import chromadb

# Step 1: Reopen the same database folder
client = chromadb.PersistentClient(path="../db")

# Step 2: Get your existing collection
collection = client.get_collection("db_taxcode")

# Step 3: Check data
print("Total items:", collection.count())

# Optional: fetch one item
data = collection.get(include=["documents", "metadatas", "embeddings"], limit=1)
print(data)