# /offline/run.py
from pathlib import Path
from processing import extract_md, md_processing, section_chunking, page_chunking
from embeddings import create_db

def main():
    print("📄 Step 1: Extract PDFs to Markdown")
    extract_md.extract_all_pdfs()  # Function inside extract_md.py

    print("\n🧹 Step 2: Process Markdown files")
    md_processing.process_all_markdown()  # Function inside md_processing.py

    print("\n✂️ Step 3: Split Markdown into sections")
    section_chunking.chunk_all_sections()  # Function inside section_chunking.py

    print("\n📄 Step 4: Split sections into page-level chunks")
    page_chunking.chunk_sections_into_pages()  # Function inside page_chunking.py

    print("\n🧠 Step 5: Create Embedding Database")
    create_db.create_chroma_db()  # Function inside create_db.py

    print("\n✅ Pipeline completed!")

if __name__ == "__main__":
    main()