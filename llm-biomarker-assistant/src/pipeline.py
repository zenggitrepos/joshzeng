from __future__ import annotations
from src.generation import generate_answer
from src.retrieval import retrieve
from src.schemas import StructuredAnswer


def answer_question(question: str, top_k: int = 6) -> tuple[StructuredAnswer, list]:
    evidence = retrieve(question, top_k=top_k)
    answer = generate_answer(question, evidence)
    return answer, evidence
