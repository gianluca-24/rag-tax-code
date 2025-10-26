import requests
import gradio as gr

BACKEND_URL = "http://127.0.0.1:8000/query"  # FastAPI endpoint

# Initialize chat history
chat_history = []

def get_answer(user_message):
    global chat_history
    payload = {"query": user_message, "n_results": 5}
    try:
        response = requests.post(BACKEND_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        bot_message = data.get("answer", "Nessuna risposta trovata.")

        # Add to chat history as tuple
        chat_history.append((user_message, bot_message))

        return chat_history  # return list of tuples for Chatbot
    except requests.exceptions.RequestException as e:
        error_msg = f"Errore nella connessione al backend: {e}"
        chat_history.append((user_message, error_msg))
        return chat_history
        

with gr.Blocks() as demo:
    gr.Markdown("# Scopri il Sistema Fiscale Italiano")
    
    chatbot = gr.Chatbot()
    query_input = gr.Textbox(
        label="Inserisci la tua domanda sulla dichiarazione dei redditi:", 
        placeholder="Es. Come si compila il quadro RA del fascicolo 1?"
    )
    submit_button = gr.Button("Invia")
    
    # Update chatbot when button is clicked
    submit_button.click(fn=get_answer, inputs=query_input, outputs=chatbot)

demo.launch()