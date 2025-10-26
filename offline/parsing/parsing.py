from llama_cloud_services import LlamaParse
from dotenv import load_dotenv
from pathlib import Path
import sys
# --- Add parent folder to sys.path to import config ---
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import RAW_PATH, MD_PATH, PAGE_RANGES, BASE_URL
import os

# Load API key
load_dotenv()
llama_api_key = os.getenv("LLAMAINDEX_API_KEY")
if not llama_api_key:
    raise ValueError("LLAMAINDEX_API_KEY not found in .env")

# Initialize parser
parser = LlamaParse(
    api_key=llama_api_key,
    language="it",
   #  base_url=BASE_URL,
    parse_mode="parse_page_with_agent",
    model="openai-gpt-4-1-mini",
    high_res_ocr=True,
    adaptive_long_table=True,
    outlined_table_extraction=True,
    output_tables_as_HTML=True,
    page_separator="\n\n---\n\n",
)

# Loop through fascicoli
for fascicolo in range(1, 4):
    file_path = Path(RAW_PATH) / f"fascicolo{fascicolo}.pdf"
    output_path = Path(MD_PATH) / f"fascicolo{fascicolo}.md"

    # Convert local path to file URI
    file_url = file_path.resolve().as_uri()

    # Parse the PDF
    result = parser.parse(file_url)

    # Get Markdown documents split by page
    markdown_documents = result.get_markdown_documents(split_by_page=True)

    # Write output to Markdown
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for doc in markdown_documents:
            f.write(doc.text)
            f.write("\n\n---\n\n")  # optional page separator

    print(f"✅ Fascicolo {fascicolo} processed and saved to {output_path}")