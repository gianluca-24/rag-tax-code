import requests
import gradio as gr

BACKEND_URL = "http://127.0.0.1:8000/query"  # FastAPI endpoint

def get_answer(query):
    payload = {"query": query, "n_results": 5}
    try:
        response = requests.post(BACKEND_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        # Return the LLM answer from the backend
        return data.get("answer", "Nessuna risposta trovata.")
    except requests.exceptions.RequestException as e:
        return f"Errore nella connessione al backend: {e}"

with gr.Blocks() as demo:
    gr.Markdown("# Scopri il Sistema Fiscale Italiano")
    
    query_input = gr.Textbox(
        label="Inserisci la tua domanda sulla dichiarazione dei redditi:", 
        placeholder="Es. Come si compila il quadro RA del fascicolo 1?"
    )
    
    submit_button = gr.Button("Invia")
    answer_output = gr.Textbox(label="Risposta")
    
    # Link button to function
    submit_button.click(fn=get_answer, inputs=query_input, outputs=answer_output)

demo.launch()