# first start with section chunking
import markdown_to_json
import pathlib
import json
from langchain_text_splitters import MarkdownHeaderTextSplitter, ExperimentalMarkdownSyntaxTextSplitter


path = "../data/markdown/fascicolo1_processed.md"
fascicolo = 1

chunks = {}

for fascicolo in range(1, 4):
    md_path = pathlib.Path(f"../data/markdown/fascicolo{fascicolo}_processed.md")
    json_path = pathlib.Path(f"../data/json/fascicolo_chunks.json")

    # Read the Markdown content
    md_text = md_path.read_text(encoding="utf-8")
    # splitter = MarkdownHeaderTextSplitter(chunk_size=40, chunk_overlap=0)

    headers_to_split_on = [
        ("##", "Header 2"),
    ]
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )
    sections = splitter.split_text(md_text)
    for i, section in enumerate(sections):
        section = section.model_dump()
        chunks['fascicolo{}_section{}'.format(fascicolo, i)] = {
            'text': section['page_content'],
            'metadata': {'name': section['metadata']['Header 2'],
                         'fascicolo': fascicolo}
        }

    # splitter.create_documents([md_text])
print(f"✅ Chunked JSON saved to {json_path}")

# save as json
# json_path = md_path.with_name(json_path)
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(chunks, f, ensure_ascii=False, indent=4)