import json, re, uuid
from functools import lru_cache
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from .config import COLLECTION, MODEL_NAME, PAGES_FILE, QDRANT_DIR

@lru_cache(maxsize=1)
def encoder(): return SentenceTransformer(MODEL_NAME)

@lru_cache(maxsize=1)
def client(): return QdrantClient(path=str(QDRANT_DIR))

def split_words(text: str, size: int = 400, overlap: int = 60):
    words = text.split()
    for start in range(0, len(words), size - overlap):
        section = words[start:start + size]
        if section: yield " ".join(section)
        if start + size >= len(words): break

def heading(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[0][:180] if lines else "Untitled section"

def build_sections():
    pages = [json.loads(line) for line in PAGES_FILE.read_text(encoding="utf-8").splitlines()]
    sections = []
    for page in pages:
        if not page["text"]: continue
        for part, text in enumerate(split_words(page["text"])):
            sections.append({**page, "chunk": part, "heading": heading(page["text"]), "text": text})
    return sections

def rebuild_index():
    sections = build_sections()
    if not sections: raise ValueError("No text extracted. Add PDFs and run: python -m src.extract")
    vectors = encoder().encode([s["text"] for s in sections], normalize_embeddings=True, show_progress_bar=True)
    db = client()
    db.recreate_collection(COLLECTION, vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE))
    points = [models.PointStruct(id=str(uuid.uuid4()), vector=vector.tolist(), payload=section) for vector, section in zip(vectors, sections)]
    db.upsert(COLLECTION, points=points, wait=True)
    print(f"Indexed {len(points)} sections in {COLLECTION}.")

def search(question: str, limit: int = 5) -> list[dict]:
    vector = encoder().encode(question, normalize_embeddings=True).tolist()
    hits = client().query_points(COLLECTION, query=vector, limit=limit).points
    return [{"score": hit.score, **hit.payload} for hit in hits]
