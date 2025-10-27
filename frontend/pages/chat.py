import requests
import gradio as gr
from config_frontend import BACKEND_URL, PDF_PATHS, N_RESULTS

chat_history = []

def get_answer(user_message, session_id):
    global chat_history
    payload = {"query": user_message, "n_results": N_RESULTS}
    headers = {"X-Session-ID": session_id}
    try:
        response = requests.post(BACKEND_URL + '/query', json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        bot_message = data.get("answer", "Nessuna risposta trovata.")
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": bot_message})
        return chat_history
    except requests.exceptions.RequestException as e:
        return [{"role": "assistant", "content": f"❌ Errore di connessione: {e}"}]

def chat_interface(session_state):
    with gr.Row() as chat_row:
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="Assistente Fiscale", type="messages", height=500)
            query_input = gr.Textbox(label="Domanda", placeholder="Es. Come si compila il quadro RA del fascicolo 1?")
            submit_button = gr.Button("Invia", variant="primary")
            submit_button.click(fn=get_answer, inputs=[query_input, session_state], outputs=chatbot)
            query_input.submit(fn=get_answer, inputs=[query_input, session_state], outputs=chatbot)

        with gr.Column(scale=1):
            gr.Markdown("### 📂 Scarica i Fascicoli")
            for name, path in PDF_PATHS.items():
                gr.Button(value=f"Apri {name}", link=path, variant="secondary")

    return chat_row
