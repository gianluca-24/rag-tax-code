from pathlib import Path

# Base data directory is the parent of this file + /data
BASE_DIR = Path(__file__).resolve().parent.parent / "data"

RAW_PATH = BASE_DIR / "raw"
MD_PATH = BASE_DIR / "markdown"
JSON_PATH = BASE_DIR / "json"
DB_PATH = BASE_DIR / "db"

EMBED_MODEL = "text-embedding-3-small"

PAGE_RANGES = {
    1: range(11, 160),
    2: range(2, 61),
    3: range(2, 127),
}

CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200