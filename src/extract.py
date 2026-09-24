"""Extract each PDF into page-level JSONL with an OCR review signal."""
import json, re
from pathlib import Path
import fitz
from .config import MANIFEST, PDF_DIR, UPLOAD_DIR, PAGES_FILE

def clean(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).replace(" \n", "\n").strip()

def manifest_by_id():
    records = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else []
    return {record["id"]: record for record in records}

def extract_pdf(path: Path, metadata: dict) -> list[dict]:
    document = fitz.open(path)
    pages = []
    for index, page in enumerate(document):
        text = clean(page.get_text("text"))
        # Arabic Unicode letters offer a lightweight manual-review indicator, not OCR.
        arabic_letters = len(re.findall(r"[\u0600-\u06ff]", text))
        pages.append({
            "document_id": metadata["id"], "document_title": metadata["title"],
            "source_url": metadata.get("url", "uploaded"), "publication_date": metadata.get("publication_date", "unknown"),
            "page": index + 1, "text": text,
            "needs_ocr_review": len(text) < 40,
            "arabic_characters": arabic_letters,
        })
    return pages

def main():
    records = manifest_by_id()
    uploaded = [{"id": p.stem, "title": p.stem, "url": "uploaded", "publication_date": "uploaded"} for p in UPLOAD_DIR.glob("*.pdf")]
    all_pages = []
    for path in [*PDF_DIR.glob("*.pdf"), *UPLOAD_DIR.glob("*.pdf")]:
        metadata = records.get(path.stem) or next((x for x in uploaded if x["id"] == path.stem), None)
        if metadata:
            all_pages.extend(extract_pdf(path, metadata))
            print(f"Extracted {path.name}")
    PAGES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PAGES_FILE.open("w", encoding="utf-8") as output:
        for page in all_pages: output.write(json.dumps(page, ensure_ascii=False) + "\n")
    flagged = sum(page["needs_ocr_review"] for page in all_pages)
    print(f"Wrote {len(all_pages)} pages; {flagged} need OCR/manual review.")

if __name__ == "__main__": main()
