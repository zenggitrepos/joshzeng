from __future__ import annotations

from openai import OpenAI
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings


def main() -> None:
    if not settings.openrouter_api_key:
        raise RuntimeError("Add OPENROUTER_API_KEY to .env first.")

    client = OpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        timeout=settings.request_timeout_seconds,
    )
    response = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: OpenRouter connection successful",
            }
        ],
        temperature=0,
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
