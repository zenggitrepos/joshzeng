from __future__ import annotations
import json
from pathlib import Path
from src.pipeline import answer_question


def citation_precision(cited: set[str], retrieved: set[str]) -> float:
    return len(cited & retrieved) / len(cited) if cited else 1.0


def evaluate(path: str = "eval/questions.jsonl", k: int = 6) -> dict:
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    precisions, expected_recalls, unsupported_rates = [], [], []
    for row in rows:
        answer, evidence = answer_question(row["question"], top_k=k)
        retrieved_ids = {e.document_id for e in evidence}
        cited_ids = set(answer.cited_document_ids)
        expected = set(row["expected_document_ids"])
        precisions.append(citation_precision(cited_ids, retrieved_ids))
        expected_recalls.append(len(expected & retrieved_ids) / len(expected))
        unsupported_rates.append(len(cited_ids - retrieved_ids) / max(len(cited_ids), 1))
    return {
        "citation_precision": sum(precisions) / len(precisions),
        "evidence_recall": sum(expected_recalls) / len(expected_recalls),
        "unsupported_citation_rate": sum(unsupported_rates) / len(unsupported_rates),
    }

if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
