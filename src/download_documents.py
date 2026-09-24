"""Download manifest PDFs after a human has reviewed their status."""
import argparse, json
from pathlib import Path
import requests
from .config import MANIFEST, PDF_DIR

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-review", action="store_true", help="Download review candidates too")
    args = parser.parse_args()
    documents = json.loads(MANIFEST.read_text(encoding="utf-8"))
    selected = [d for d in documents if d["status"] == "current" or args.include_review]
    if not selected:
        raise SystemExit("No current documents. Verify sources and set approved records to status: current in data/documents.json.")
    for doc in selected:
        target = PDF_DIR / f"{doc['id']}.pdf"
        if target.exists():
            print(f"Exists: {target.name}")
            continue
        response = requests.get(doc["url"], timeout=60, headers={"User-Agent": "UAEU-doc-assistant/1.0"})
        response.raise_for_status()
        if not response.content.startswith(b"%PDF"):
            raise ValueError(f"Source was not a PDF: {doc['url']}")
        target.write_bytes(response.content)
        print(f"Downloaded: {target.name}")

if __name__ == "__main__": main()
