from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Hosted free-model routing through OpenRouter. No LLM is downloaded locally.
    llm_provider: str = os.getenv("LLM_PROVIDER", "openrouter")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openrouter/free")
    openrouter_base_url: str = os.getenv(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    )
    app_url: str = os.getenv("APP_URL", "http://localhost:8501")
    app_name: str = os.getenv(
        "APP_NAME", "LLM Translational Biomarker Assistant"
    )
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "120"))
    max_generation_attempts: int = int(os.getenv("MAX_GENERATION_ATTEMPTS", "3"))

    embedding_backend: str = os.getenv("EMBEDDING_BACKEND", "local")
    chroma_path: str = os.getenv("CHROMA_PATH", ".chroma")
    collection_name: str = os.getenv(
        "COLLECTION_NAME", "translational_evidence"
    )


settings = Settings()
