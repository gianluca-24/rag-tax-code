import json
import pathlib
from langchain_text_splitters import MarkdownTextSplitter
import re

# last pages per fascicolo
last_pages = {
    1: 12, 2:3, 3:3
}

def extract_page_positions(text):
    """
    Returns the first page number found in the text, or None if no 'PAGE XX' is found.
    """
    pattern = r'PAGE\s+(\d+)'
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None


json_path = pathlib.Path("../data/json/fascicolo_chunks.json")

splitter = MarkdownTextSplitter(chunk_size=2000, chunk_overlap=200)

all_chunks = []

with open(json_path, 'r', encoding='utf-8') as f:
    sections = json.load(f)
    id = 0

    for i, section_key in enumerate(sections.keys()):
        section = sections[section_key]
        text = section['text']
        metadata = section['metadata']

        page_pos = extract_page_positions(text)
        # print(page_pos)
        # print(len(text))
        chunks = splitter.split_text(text)

        # last_page = starting_pages[metadata['fascicolo']]
        last_page = last_pages[metadata['fascicolo']]

        for j, chunk in enumerate(chunks):
            pages_re = extract_page_positions(chunk)

            if pages_re == None:
                # pages = [last_pages[metadata['fascicolo']]]
                pages = f"{last_pages[metadata['fascicolo']]}"
            else:
                # pages = [pages_re, pages_re + 1]
                pages = f"{pages_re}, {pages_re + 1}"
                # last_page = pages_re + 1
                last_pages[metadata['fascicolo']] = pages_re + 1
            

            chunk_entry = {
                "id": id,
                "chunk_text": chunk,
                "metadata": {
                    "fascicolo": metadata.get("fascicolo"),
                    "section_name": metadata.get("name", section_key),
                    "pages": pages,
                }
            }
            all_chunks.append(chunk_entry)
            id += 1

# Save all chunks to JSON
output_path = pathlib.Path("../data/json/fascicolo_final_chunks.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=2)

print(f"✅ Saved {len(all_chunks)} chunks to {output_path}")