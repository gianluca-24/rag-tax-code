from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from aux import semantic_search, answer_question, process_zip_transactions, calculate_gain
from config_backend import EMBED_MODEL, CHAT_MODEL, N_RESULTS


app = FastAPI(title="Taxcode Semantic Search API")

class QueryRequest(BaseModel):
    query: str
    n_results: int = N_RESULTS

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

@app.post("/calculate_gain")
async def calculate_crypto_gain(transactions: UploadFile = File(...)):
    """
    Receives a ZIP file containing yearly Binance CSV transactions,
    processes it, and returns a summary.
    """
    if transactions.content_type != "application/zip":
        raise HTTPException(status_code=400, detail="Il file deve essere un .zip")

    try:
        full_df = process_zip_transactions(transactions.file)
        profit = calculate_gain(full_df)

        return {
            "message": "✅ File caricati e ordinati correttamente!",
            "total_transactions": len(full_df),
            "profit": profit,
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella lettura dello zip: {e}")