import pathlib
import re

# Path to your original Markdown file
fascicolo = 1

for fascicolo in range(1, 4):
    md_path = pathlib.Path(f"../data/markdown/fascicolo{fascicolo}.md")

    # Read the Markdown content
    md_text = md_path.read_text(encoding="utf-8")

    # ---- 7. Ensure '##' section headers have a blank line before and after ----
    md_text = re.sub(r'(?m)^(## .+)$', r'----\n\1\n\n----', md_text)
    # Detect lines that contain only a page number delimited by single asterisks (*123*)
    md_text = re.sub(r'(?m)^\s*\*\*(\d+)\*\*\s*$', r'----\n\nPAGE \1\n\n----', md_text)

    # ---- 0. Remove Unicode soft hyphen (U+00AD) which often splits words invisibly ----
    # Example: "de\u00ADtrazione" -> "detrazione"
    md_text = md_text.replace("\u00AD", "")

    # ---- 2. Fix plain split words across lines (no hyphen): letter\nletter -> letterletter ----
    # Use \w to match unicode word characters (letters, numbers, underscore). This will
    # merge cases like "dichiara\nzione" -> "dichiarazione".
    md_text = re.sub(r'(?<=\w)\n(?=\w)', '', md_text)

    # ---- 3. Replace bullet indicators 'n ' at start of lines with '- ' ----
    md_text = re.sub(r'(?m)^n\s+', '- ', md_text)

    # ---- 4. Remove specified page headers (example values for Fascicolo 1/2/3) ----
    header_pattern = (
        r'REDDITI PERSONE FISICHE 2025\s*\s*Fascicolo\s*[123]\s*\s*\*\*ISTRUZIONI PER LA COMPILAZIONE\*\*'
    )
    md_text = re.sub(header_pattern, '', md_text, flags=re.IGNORECASE)

    # ---- 5. Remove all '**' bold markers ----
    md_text = re.sub(r'\*\*', '', md_text)

    # ---- 6. Remove line breaks that are "soft" wraps (replace with a space)
    #        where previous char is letter/number/comma/space (as you wanted).
    #        We already merged split words in step 2, so this step won't re-join inside words.
    md_text = re.sub(r'(?<=[A-Za-z0-9, ])\n', '', md_text)

    # ---- 7. Ensure '##' section headers have a blank line before and after ----
    md_text = re.sub(r'(?m)^(## .+)$', r'\n\n\1\n\n', md_text)

    # ---- 8. Collapse multiple consecutive newlines into a single newline ----
    md_text = re.sub(r'\n{2,}', '\n', md_text)

    md_text = re.sub(r'(?<=\w)\n(?=\w)', '', md_text)

    md_text = re.sub(r'----', ' ', md_text)
    md_text = re.sub(r',\s*\n\s*', ', ', md_text)
    md_text = re.sub(r'-\s*\n\s*', '- ', md_text)


    # Save the processed Markdown
    processed_path = md_path.with_name(md_path.stem + "_processed.md")
    processed_path.write_text(md_text, encoding="utf-8")

    print(f"✅ Processed Markdown saved to {processed_path}")