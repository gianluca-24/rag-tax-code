from fastapi import FastAPI
from pydantic import BaseModel
from aux import semantic_search, answer_question

app = FastAPI(title="Taxcode Semantic Search API")

class QueryRequest(BaseModel):
    query: str
    n_results: int = 5

@app.post("/query")
def search_documents(request: QueryRequest):
    # Step 1: Retrieve relevant docs from the vector DB
    docs = semantic_search(request.query, request.n_results)
    
    # Step 2: Generate LLM answer based on retrieved docs
    answer = answer_question(request.query, docs)
    
    return {
        "query": request.query,
        "retrieved_documents": docs,
        "answer": answer
    }