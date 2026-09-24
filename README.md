# UAEU Arabic–English Document Assistant

A small, local retrieval-augmented assistant for UAEU PDFs. It extracts text page-by-page, indexes bilingual passages in Qdrant, retrieves the best five passages, and can produce source-grounded answers in Arabic or English.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Review the UAEU catalogue, then set approved records to "current" in data/documents.json.
python -m src.download_documents
python -m src.ingest
python -m src.search "ما متطلبات التسجيل في هذا المقرر؟"
streamlit run app.py
```

`download_documents` intentionally skips existing files. Review `data/documents.json` before downloading: URLs and effective dates must be checked against the UAEU catalogue before each production index. The initial manifest has only official UAEU sources and flags every candidate for review, so legacy material cannot be silently mixed with current policy.

## What is included

- PyMuPDF extraction into `data/extracted/pages.jsonl`, retaining page numbers.
- OCR detection/reporting for pages with little or no embedded text; OCR is an explicit optional step.
- 400-word overlapping chunks with headings and page references.
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` embeddings in local Qdrant.
- Command-line retrieval milestone and Streamlit upload/search interface.
- Optional OpenAI-compatible LLM answer generation with strict source/citation validation.
- An evaluation runner and a 36-question bilingual test-set template.

## LLM configuration

Retrieval works without an API key. For generated answers, set `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`, default `gpt-4.1-mini`) in `.env`. The model receives retrieved passages as clearly delimited data, never as instructions. If the key is absent, the interface still shows the five retrieved sources.

## Quality controls

Only documents whose `status` is `current` are ingested by default. Use `--include-review` only after confirming a document is still authoritative. Every answer citation must exactly match a retrieved `(document_id, page)` pair; otherwise it is rejected. Run `python -m src.evaluate` after filling the expected document/page fields in `data/evaluation_questions.json`.

## Data handling

Do not upload confidential student records. This local setup stores PDFs, extracted text, and the Qdrant database under `data/`, which is excluded from Git.
