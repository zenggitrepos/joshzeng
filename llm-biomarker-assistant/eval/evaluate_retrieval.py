from __future__ import annotations
import json
from pathlib import Path
from src.retrieval import retrieve


def recall_at_k(expected: set[str], retrieved: list[str]) -> float:
    return len(expected.intersection(retrieved)) / len(expected) if expected else 1.0


def evaluate(path: str = "eval/questions.jsonl", k: int = 6) -> dict:
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    scores = []
    for row in rows:
        hits = retrieve(row["question"], top_k=k)
        retrieved_ids = [hit.document_id for hit in hits]
        score = recall_at_k(set(row["expected_document_ids"]), retrieved_ids)
        scores.append(score)
        print(row["question_id"], round(score, 3), retrieved_ids)
    result = {"questions": len(scores), f"mean_recall_at_{k}": sum(scores) / len(scores)}
    print(result)
    return result

if __name__ == "__main__":
    evaluate()
