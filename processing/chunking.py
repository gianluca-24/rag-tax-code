# first start with section chunking
import markdown_to_json
import pathlib
import json


path = "../data/markdown/fascicolo1_processed.md"
fascicolo = 1

md_path = pathlib.Path(f"../data/markdown/fascicolo{fascicolo}.md")

# Read the Markdown content
md_text = md_path.read_text(encoding="utf-8")

dictified = markdown_to_json.dictify(md_text)

json_path = pathlib.Path(f"../data/json/fascicolo{fascicolo}_chunked.json")
json_path.write_text(json.dumps(dictified, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"✅ Chunked JSON saved to {json_path}")