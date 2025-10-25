import json
from pathlib import Path
import sys
from langchain_text_splitters import MarkdownHeaderTextSplitter

# Add parent folder to sys.path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import MD_PATH, JSON_PATH

def chunk_all_sections():
    """Split processed Markdown files into sections and save as JSON."""
    JSON_PATH.mkdir(parents=True, exist_ok=True)

    all_chunks = {}
    output_json_path = JSON_PATH / "fascicolo_chunks.json"

    for fascicolo in range(1, 4):
        md_path = MD_PATH / f"fascicolo{fascicolo}_processed.md"

        if not md_path.exists():
            print(f"⚠️ File not found: {md_path}")
            continue

        md_text = md_path.read_text(encoding="utf-8")

        headers_to_split_on = [("##", "Header 2")]
        splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        sections = splitter.split_text(md_text)

        for i, section in enumerate(sections):
            section_data = section.model_dump()
            header_name = section_data['metadata'].get('Header 2')
            all_chunks[f'fascicolo{fascicolo}_section{i}'] = {
                'text': section_data['page_content'],
                'metadata': {
                    'name': header_name,
                    'fascicolo': fascicolo
                }
            }

    # Save to JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=4)

    print(f"✅ Chunked JSON saved to {output_json_path}")


if __name__ == "__main__":
    chunk_all_sections()