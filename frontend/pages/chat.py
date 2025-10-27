import requests
import gradio as gr
from config_frontend import BACKEND_URL

chat_history = []

def get_answer(user_message):
    global chat_history
    payload = {"query": user_message, "n_results": 5}
    try:
        response = requests.post(BACKEND_URL + '/query', json=payload)
        response.raise_for_status()
        data = response.json()
        bot_message = data.get("answer", "Nessuna risposta trovata.")
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": bot_message})
        return chat_history
    except requests.exceptions.RequestException as e:
        return [{"role": "assistant", "content": f"❌ Errore di connessione: {e}"}]

PDF_PATHS = {
    "Fascicolo 1": "../data/raw/fascicolo1.pdf",
    "Fascicolo 2": "../data/raw/fascicolo2.pdf",
    "Fascicolo 3": "../data/raw/fascicolo3.pdf",
}

def chat_interface():
    with gr.Row() as chat_row:
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="Assistente Fiscale", type="messages", height=500)
            query_input = gr.Textbox(label="Domanda", placeholder="Es. Come si compila il quadro RA del fascicolo 1?")
            submit_button = gr.Button("Invia", variant="primary")
            submit_button.click(fn=get_answer, inputs=query_input, outputs=chatbot)

        with gr.Column(scale=1):
            gr.Markdown("### 📂 Scarica i Fascicoli")
            for name, path in PDF_PATHS.items():
                gr.Button(value=f"Apri {name}", link=path, variant="secondary")

    return chat_row

# demo.launch()