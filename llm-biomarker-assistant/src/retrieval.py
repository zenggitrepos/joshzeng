from __future__ import annotations
from dataclasses import dataclass
import chromadb
from src.config import settings
from src.embeddings import LocalEmbeddingFunction

@dataclass
class RetrievedEvidence:
    document_id: str
    text: str
    metadata: dict
    distance: float


def retrieve(question: str, top_k: int = 6) -> list[RetrievedEvidence]:
    client = chromadb.PersistentClient(path=settings.chroma_path)
    collection = client.get_collection(
        name=settings.collection_name,
        embedding_function=LocalEmbeddingFunction(),
    )
    result = collection.query(
        query_texts=[question],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        RetrievedEvidence(document_id=doc_id, text=text, metadata=meta, distance=float(distance))
        for doc_id, text, meta, distance in zip(
            result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]
        )
    ]
