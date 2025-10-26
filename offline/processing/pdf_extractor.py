import pymupdf4llm
from pathlib import Path
import sys

# --- Add parent folder to sys.path to import config ---
sys.path.append(str(Path(__file__).resolve().parent))
from config import RAW_PATH, MD_PATH, PAGE_RANGES

def extract_all_pdfs():
    """Convert PDFs to Markdown for all fascicoli based on PAGE_RANGES."""
    MD_PATH.mkdir(parents=True, exist_ok=True)

    for fascicolo, pages in PAGE_RANGES.items():
        pdf_path = Path(RAW_PATH) / f"fascicolo{fascicolo}.pdf"
        output_path = Path(MD_PATH) / f"fascicolo{fascicolo}.md"

        md_text = pymupdf4llm.to_markdown(
            pdf_path,
            pages=list(pages),
            show_progress=True
        )

        output_path.write_bytes(md_text.encode())
        print(f"✅ Fascicolo {fascicolo} processed and saved to {output_path}")


if __name__ == "__main__":
    extract_all_pdfs()