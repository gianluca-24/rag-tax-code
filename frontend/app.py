import gradio as gr
from pages.chat import chat_interface
from pages.crypto_gain import crypto_interface
import uuid

def home():
    gr.Markdown("# 💼 Benvenuto nel Portale Fiscale")
    gr.Markdown("Scegli una delle seguenti opzioni per continuare:")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🇮🇹 Sistema Fiscale Italiano")
            gr.Markdown(
                """
                L'**Assistente Fiscale** utilizza un modello linguistico per rispondere alle tue domande sul sistema fiscale italiano.
                Puoi chiedere informazioni su compilazione dei moduli, detrazioni, imposte e normative fiscali aggiornate.
                """
            )

        with gr.Column():
            gr.Markdown("### 💰 Calcolatore Plusvalenze Crypto")
            gr.Markdown(
                """
                Il **Calcolatore di Plusvalenze Crypto** consente di caricare un file `.zip` con le tue transazioni da Binance
                e calcola automaticamente le plusvalenze annuali in base alla cronologia degli scambi, depositi e prelievi.
                """
            )

# --- Create main app with tabs/pages ---
with gr.Blocks(theme=gr.themes.Soft(), title="Portale Fiscale") as demo:
    session_state = gr.State(str(uuid.uuid4()))
    with gr.Tab("🏠 Home"):
        home()

    with gr.Tab("💬 Sistema Fiscale Italiano"):
        chat_interface(session_state)
        

    with gr.Tab("📊 Calcolatore Crypto"):
        crypto_interface()

demo.launch(share=True)



# import requests
# import gradio as gr

# BACKEND_URL = "http://127.0.0.1:8000/query"  # FastAPI endpoint

# # Initialize chat history
# chat_history = []


# def get_answer(user_message):
#     global chat_history
#     payload = {"query": user_message, "n_results": 5}
#     try:
#         response = requests.post(BACKEND_URL, json=payload)
#         response.raise_for_status()
#         data = response.json()
#         bot_message = data.get("answer", "Nessuna risposta trovata.")

#         chat_history.append((user_message, bot_message))
#         return chat_history

#     except requests.exceptions.RequestException as e:
#         error_msg = f"❌ Errore nella connessione al backend: {e}"
#         chat_history.append((user_message, error_msg))
#         return chat_history


# # Paths for fascicoli
# PDF_PATHS = {
#     "Fascicolo 1": "../data/raw/fascicolo1.pdf",
#     "Fascicolo 2": "../data/raw/fascicolo2.pdf",
#     "Fascicolo 3": "../data/raw/fascicolo3.pdf",
# }


# with gr.Blocks(theme=gr.themes.Soft(), title="Sistema Fiscale Italiano") as demo:
#     gr.Markdown(
#         """
#         # 💬 Scopri il Sistema Fiscale Italiano  
#         Chiedi qualsiasi informazione sui fascicoli della dichiarazione dei redditi.
#         """
#     )

#     with gr.Row():
#         # --- LEFT: Chat section ---
#         with gr.Column(scale=3):
#             chatbot = gr.Chatbot(
#                 label="Assistente Fiscale",
#                 type="messages",
#                 height=500,
#                 avatar_images=(None, "https://cdn-icons-png.flaticon.com/512/4712/4712027.png"),
#             )

#             query_input = gr.Textbox(
#                 label="Domanda",
#                 placeholder="Es. Come si compila il quadro RA del fascicolo 1?",
#             )
#             submit_button = gr.Button("Invia", variant="primary")
#             submit_button.click(fn=get_answer, inputs=query_input, outputs=chatbot)

#         # --- RIGHT: Download sidebar ---
#         with gr.Column(scale=1):
#             gr.Markdown("### 📂 Scarica i Fascicoli")

#             for name, path in PDF_PATHS.items():
#                 gr.DownloadButton(
#                     label=name,
#                     value=path,
#                     variant="secondary",
#                 )

# demo.launch()