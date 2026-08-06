from __future__ import annotations
import json
from pathlib import Path
import chromadb
from src.config import settings
from src.embeddings import LocalEmbeddingFunction
from src.schemas import EvidenceRecord


def load_jsonl(path: str | Path) -> list[EvidenceRecord]:
    records: list[EvidenceRecord] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(EvidenceRecord.model_validate_json(line))
    return records


def metadata_for(record: EvidenceRecord) -> dict:
    return {
        "source_type": record.source_type,
        "title": record.title,
        "year": record.year or 0,
        "disease": record.disease or "",
        "evidence_level": record.evidence_level,
        "study_design": record.study_design,
        "url": record.url or "",
        "is_synthetic": record.is_synthetic,
        "biomarkers": "|".join(record.biomarkers),
        "interventions": "|".join(record.interventions),
    }


def build_index(input_path: str = "data/raw/example_evidence.jsonl", reset: bool = True) -> int:
    client = chromadb.PersistentClient(path=settings.chroma_path)
    if reset:
        try:
            client.delete_collection(settings.collection_name)
        except Exception:
            pass
    collection = client.get_or_create_collection(
        name=settings.collection_name,
        embedding_function=LocalEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )
    records = load_jsonl(input_path)
    collection.add(
        ids=[r.document_id for r in records],
        documents=[r.text for r in records],
        metadatas=[metadata_for(r) for r in records],
    )
    return len(records)

if __name__ == "__main__":
    count = build_index()
    print(f"Indexed {count} evidence records.")
