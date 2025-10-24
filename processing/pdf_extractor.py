import pymupdf4llm
import pathlib

fascicolo = 1

# md_read = pymupdf4llm.LlamaMarkdownReader()
# Percorso del file PDF
pdf_path = f"../data/raw/fascicolo{fascicolo}.pdf"

# data = md_read.load_data(pdf_path)

md_text = pymupdf4llm.to_markdown(pdf_path)

pathlib.Path(f"fascicolo{fascicolo}.md").write_bytes(md_text.encode())


