import pymupdf4llm
import pathlib

fascicolo = 1
# Percorso del file PDF

# Define page ranges per fascicolo (customize as needed)
page_ranges = {
    1: range(11, 160),
    2: range(2, 61),
    3: range(2, 127),
}

for fascicolo in range(1, 4):
    pdf_path = f"../data/raw/fascicolo{fascicolo}.pdf"

    output_path = f"../data/markdown/fascicolo{fascicolo}.md"

    # data = md_read.load_data(pdf_path)

    md_text = pymupdf4llm.to_markdown(pdf_path, pages=list(page_ranges[fascicolo]), show_progress=True)

    pathlib.Path(output_path).write_bytes(md_text.encode())


    print(f"Fascicolo {fascicolo} processed and saved to {output_path}")