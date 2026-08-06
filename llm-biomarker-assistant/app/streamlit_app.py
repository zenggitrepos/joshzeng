from __future__ import annotations
import pandas as pd
import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from src.pipeline import answer_question

st.set_page_config(page_title="Translational Biomarker Assistant", layout="wide")
st.title("LLM-Powered Translational Biomarker Assistant")
st.caption("Generation uses a hosted free model through OpenRouter; no LLM is downloaded locally.")
st.warning("The bundled dataset is synthetic and intended only for software demonstration.")

question = st.text_area(
    "Ask a translational research question",
    value="What evidence supports combining a TIGIT inhibitor with anti-PD-1 therapy in NSCLC, and which biomarkers could identify responsive patients?",
    height=100,
)
top_k = st.slider("Retrieved passages", 3, 10, 6)

if st.button("Generate evidence-grounded answer", type="primary"):
    with st.spinner("Retrieving evidence and generating answer..."):
        try:
            answer, evidence = answer_question(question, top_k=top_k)
            st.subheader("Structured answer")
            st.json(answer.model_dump())
            st.subheader("Evidence table")
            table = pd.DataFrame([
                {
                    "document_id": e.document_id,
                    "title": e.metadata.get("title"),
                    "source_type": e.metadata.get("source_type"),
                    "evidence_level": e.metadata.get("evidence_level"),
                    "synthetic": e.metadata.get("is_synthetic"),
                    "distance": round(e.distance, 4),
                    "passage": e.text,
                }
                for e in evidence
            ])
            st.dataframe(table, use_container_width=True, hide_index=True)
        except Exception as exc:
            st.exception(exc)
