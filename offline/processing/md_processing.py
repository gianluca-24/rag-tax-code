import re
from pathlib import Path
import sys

# Add parent folder to sys.path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from offline.config import MD_PATH

def process_all_markdown():
    """Cleans and formats all Markdown files in MD_PATH."""
    MD_PATH.mkdir(parents=True, exist_ok=True)

    for fascicolo in range(1, 4):
        md_path = MD_PATH / f"fascicolo{fascicolo}.md"

        if not md_path.exists():
            print(f"⚠️ File not found: {md_path}")
            continue

        md_text = md_path.read_text(encoding="utf-8")

        # ---- Ensure '##' section headers have blank lines before/after ----
        md_text = re.sub(r'(?m)^(## .+)$', r'----\n\1\n\n----', md_text)

        # ---- Detect lines with only a page number like **123** ----
        md_text = re.sub(r'(?m)^\s*\*\*(\d+)\*\*\s*$', r'----\n\nPAGE \1\n\n----', md_text)

        # ---- Remove Unicode soft hyphen ----
        md_text = md_text.replace("\u00AD", "")

        # ---- Merge split words across lines ----
        md_text = re.sub(r'(?<=\w)\n(?=\w)', '', md_text)

        # ---- Replace bullet indicators 'n ' with '- ' ----
        md_text = re.sub(r'(?m)^n\s+', '- ', md_text)

        # ---- Remove specified page headers ----
        header_pattern = r'REDDITI PERSONE FISICHE 2025\s*\s*Fascicolo\s*[123]\s*\s*\*\*ISTRUZIONI PER LA COMPILAZIONE\*\*'
        md_text = re.sub(header_pattern, '', md_text, flags=re.IGNORECASE)

        # ---- Remove all '**' bold markers ----
        md_text = re.sub(r'\*\*', '', md_text)

        # ---- Remove soft line breaks ----
        md_text = re.sub(r'(?<=[A-Za-z0-9, ])\n', '', md_text)

        # ---- Ensure '##' section headers have blank lines ----
        md_text = re.sub(r'(?m)^(## .+)$', r'\n\n\1\n\n', md_text)

        # ---- Collapse multiple newlines ----
        md_text = re.sub(r'\n{2,}', '\n', md_text)

        # ---- Clean remaining artifacts ----
        md_text = re.sub(r'(?<=\w)\n(?=\w)', '', md_text)
        md_text = re.sub(r'----', ' ', md_text)
        md_text = re.sub(r',\s*\n\s*', ', ', md_text)
        md_text = re.sub(r'-\s*\n\s*', '- ', md_text)

        # Save processed Markdown
        processed_path = md_path.with_name(md_path.stem + "_processed.md")
        processed_path.write_text(md_text, encoding="utf-8")

        print(f"✅ Processed Markdown saved to {processed_path}")


if __name__ == "__main__":
    process_all_markdown()