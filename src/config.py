from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PDF_DIR = DATA / "pdfs"
UPLOAD_DIR = DATA / "uploads"
EXTRACTED_DIR = DATA / "extracted"
QDRANT_DIR = DATA / "qdrant"
MANIFEST = DATA / "documents.json"
PAGES_FILE = EXTRACTED_DIR / "pages.jsonl"
COLLECTION = "uaeu_sections"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

for directory in (PDF_DIR, UPLOAD_DIR, EXTRACTED_DIR, QDRANT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
