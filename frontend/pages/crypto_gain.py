import gradio as gr
import pandas as pd
import zipfile
from io import TextIOWrapper
import requests
from config_frontend import BACKEND_URL


def process_crypto_file(zip_file):
    if zip_file is None:
        return "❌ Nessun file caricato."

    try:
        # Send file to FastAPI backend
        files = {"transactions": (zip_file.name, open(zip_file.name, "rb"), "application/zip")}
        response = requests.post(BACKEND_URL + '/calculate_gain', files=files)
        response.raise_for_status()
        data = response.json()
        string = f"{data.get('message')}\n\nTotale transazioni processate: {data.get('total_transactions')}\nProfitto calcolato: {data.get('profit')}"
        return string

    except requests.exceptions.RequestException as e:
        return f"❌ Errore di connessione al server: {e}"

def crypto_interface():
    with gr.Row() as crypto_row:
        with gr.Column(scale=2):
            gr.Markdown("### 💰 Calcolatore Plusvalenze Crypto")
            gr.Markdown("📄 Carica il file in formato .zip contenente tutte le transazioni esportate da binance.\n"
                        "Assicurati che il file contenga le transazioni nel formato corretto.")
            file_input = gr.File(label="Carica file .zip Binance", file_types=[".zip"])
            submit_button = gr.Button("Calcola Plusvalenze", variant="primary")
            output = gr.Textbox(label="Risultato", interactive=False, lines=15)

            # Bind the button to the processing function
            submit_button.click(fn=process_crypto_file, inputs=file_input, outputs=output)


    return crypto_row