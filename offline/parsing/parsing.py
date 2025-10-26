from llama_parse import LlamaParse
from dotenv import load_dotenv
import os
from pathlib import Path
import sys
# --- Add parent folder to sys.path to import config ---
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import RAW_PATH, MD_PATH, PAGE_RANGES

load_dotenv()
llama_api_key = os.getenv("LLAMAINDEX_API_KEY")


parser = LlamaParse(
   api_key=llama_api_key,  
   result_type="markdown",  # "markdown" and "text" are available
   )
fascicolo = 1
file_name = Path(RAW_PATH) / f"fascicolo{fascicolo}.pdf"
output_path = Path(MD_PATH) / f"fascicolo{fascicolo}.md"

extra_info = {"file_name": file_name}

# print('ciaooooo')

documents = parser.load_data(str(file_name),extra_info=extra_info)
#    print(documents)
# print('dopo load data')
# Write the output to a file
with open(output_path, "w", encoding="utf-8") as f:
   for doc in documents:
       f.write(doc.text)