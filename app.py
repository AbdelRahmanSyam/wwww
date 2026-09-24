import hashlib
import streamlit as st
from src.config import UPLOAD_DIR
from src.extract import main as extract
from src.retrieval import rebuild_index, search
from src.answering import generate

st.set_page_config(page_title="UAEU Document Assistant", page_icon="📚")
st.title("UAEU Arabic–English Document Assistant")
st.caption("Answers are grounded only in retrieved passages. Verify policy currency before relying on it.")

with st.sidebar:
    st.header("Document upload")
    files = st.file_uploader("Add university PDFs", type="pdf", accept_multiple_files=True)
    if st.button("Index uploaded PDFs", disabled=not files):
        for file in files:
            safe_name = hashlib.sha256(file.name.encode()).hexdigest()[:10] + ".pdf"
            (UPLOAD_DIR / safe_name).write_bytes(file.getvalue())
        with st.spinner("Extracting and indexing..."):
            extract(); rebuild_index()
        st.success("Documents indexed.")
    st.info("For the curated collection, review data/documents.json, download approved PDFs, then run ingestion from the terminal.")

question = st.text_input("Ask a question / اطرح سؤالاً", placeholder="What are the prerequisites for this course? / ما متطلبات التسجيل؟")
if question:
    try:
        passages = search(question)
        result = generate(question, passages)
        st.subheader("Answer / الإجابة")
        st.write(result["answer"])
        if result["citations"]:
            titles = {p["document_id"]: p["document_title"] for p in passages}
            st.caption("Citations: " + ", ".join(f"{titles[c['document_id']]} (p. {c['page']})" for c in result["citations"]))
        st.subheader("Retrieved sources / المصادر المسترجعة")
        for item in passages:
            with st.expander(f"{item['document_title']} — page {item['page']} · score {item['score']:.3f}"):
                st.write(item["text"])
                st.caption(item["source_url"])
    except Exception as exc:
        st.error(f"Search is unavailable: {exc}")
        st.caption("Add/index PDFs first. For a new collection use: python -m src.ingest")
