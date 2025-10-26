import json
import re
from pathlib import Path
from langchain_text_splitters import MarkdownTextSplitter
import sys

# Add parent folder to sys.path to import config
sys.path.append(str(Path(__file__).resolve().parent))
from config import JSON_PATH, CHUNK_SIZE, CHUNK_OVERLAP

# Track last page numbers per fascicolo
LAST_PAGES = {1: 12, 2: 3, 3: 3}

def extract_page_positions(text: str):
    """Return the first page number found in text, or None if not found."""
    pattern = r'PAGE\s+(\d+)'
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None

def chunk_sections_into_pages(input_json: Path = JSON_PATH / "fascicolo_chunks.json",
                               output_json: Path = JSON_PATH / "fascicolo_final_chunks.json",
                               chunk_size: int = CHUNK_SIZE,
                               chunk_overlap: int = CHUNK_OVERLAP):
    """
    Splits section chunks into page-level chunks and saves final JSON.
    """
    if not input_json.exists():
        raise FileNotFoundError(f"Input JSON not found: {input_json}")

    with open(input_json, "r", encoding="utf-8") as f:
        sections = json.load(f)

    splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    all_chunks = []
    chunk_id = 0

    for section_key, section in sections.items():
        text = section['text']
        metadata = section['metadata']
        fascicolo = metadata.get("fascicolo", 1)
        last_page = LAST_PAGES.get(fascicolo, 1)

        chunks = splitter.split_text(text)

        for chunk in chunks:
            pages_re = extract_page_positions(chunk)
            if pages_re is None:
                pages = f"{last_page}"
            else:
                pages = f"{pages_re}, {pages_re + 1}"
                last_page = pages_re + 1
                LAST_PAGES[fascicolo] = last_page

            chunk_entry = {
                "id": chunk_id,
                "chunk_text": chunk,
                "metadata": {
                    "fascicolo": fascicolo,
                    "section_name": metadata.get("name", section_key),
                    "pages": pages,
                }
            }
            all_chunks.append(chunk_entry)
            chunk_id += 1

    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(all_chunks)} page chunks to {output_json}")
    return all_chunks

if __name__ == "__main__":
    chunk_sections_into_pages()