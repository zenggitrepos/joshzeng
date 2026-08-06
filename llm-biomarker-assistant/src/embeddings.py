from __future__ import annotations
from typing import Sequence
from sentence_transformers import SentenceTransformer

class LocalEmbeddingFunction:
    """Chroma-compatible embedding function using a local biomedical-capable baseline."""
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model = SentenceTransformer(model_name)

    def name(self) -> str:
        return "local_sentence_transformer"

    def __call__(self, input: Sequence[str]) -> list[list[float]]:
        vectors = self.model.encode(list(input), normalize_embeddings=True)
        return vectors.tolist()

    def embed_query(self, input: Sequence[str]) -> list[list[float]]:
        return self(input)
