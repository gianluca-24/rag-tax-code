import gradio as gr
import requests

BACKEND_URL = "http://127.0.0.1:8000/query"

chat_history = []

EXAMPLE_QUESTIONS = [
    "Come si compila il quadro RA del fascicolo 1?",
    "Quali sezioni devo completare per la detrazione figli?",
    "Come si dichiara il reddito da lavoro autonomo?",
]

PDF_PATHS = {
    "Fascicolo 1": "../data/raw/fascicolo1.pdf",
    "Fascicolo 2": "../data/raw/fascicolo2.pdf",
    "Fascicolo 3": "../data/raw/fascicolo3.pdf",
}

def get_answer(user_message):
    global chat_history
    payload = {"query": user_message, "n_results": 5}
    try:
        response = requests.post(BACKEND_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        bot_message = data.get("answer", "Nessuna risposta trovata.")

        # Always append properly formatted messages
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": bot_message})

        return chat_history  # This is now correctly a list of dicts
    except requests.exceptions.RequestException as e:
        error_msg = f"Errore nella connessione al backend: {e}"
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": error_msg})
        return chat_history

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown("## Scopri il Sistema Fiscale Italiano")
            chatbot = gr.Chatbot(elem_id="chatbot", type="messages")
            query_input = gr.Textbox(
                placeholder="Es. Come si compila il quadro RA del fascicolo 1?",
                label="Inserisci la tua domanda"
            )
            submit_button = gr.Button("Invia")
            submit_button.click(fn=get_answer, inputs=query_input, outputs=chatbot)

        with gr.Column(scale=1):
            gr.Markdown("## Scarica i Fascicoli")
            for name, path in PDF_PATHS.items():
                gr.DownloadButton(
                    label=name,
                    value=path,
                    variant="secondary",
                )

            gr.Markdown("## Esempi di domande")
            for question in EXAMPLE_QUESTIONS:
                btn = gr.Button(question)
                # Fill query_input when button is clicked (doesn't submit yet)
                btn.click(fn=lambda q=question: q, inputs=[], outputs=query_input)

demo.launch()