from __future__ import annotations

import json
import os
import re
from typing import Any, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class OpenRouterFreeLLM:
    """OpenAI-compatible client configured for OpenRouter's hosted Free Models Router."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        max_json_attempts: int = 3,
    ):
        self.model = model or os.getenv("OPENROUTER_MODEL", "openrouter/free")
        self.base_url = base_url or os.getenv(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.site_url = os.getenv("OPENROUTER_SITE_URL")
        self.app_name = os.getenv(
            "OPENROUTER_APP_NAME", "Multi-Agent Oncology ADC Target Discovery"
        )
        self.max_json_attempts = max_json_attempts
        self._client = None

        if self.api_key:
            try:
                from openai import OpenAI

                headers: dict[str, str] = {}
                if self.site_url:
                    headers["HTTP-Referer"] = self.site_url
                if self.app_name:
                    headers["X-OpenRouter-Title"] = self.app_name

                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    default_headers=headers or None,
                )
            except Exception:
                self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def _require_client(self):
        if not self.available:
            raise RuntimeError(
                "OpenRouter is not configured. Set OPENROUTER_API_KEY before using the LLM chat interface."
            )
        return self._client

    def complete_text(self, system_prompt: str, user_prompt: str) -> str:
        client = self._require_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: str = "auto",
    ):
        """Send a chat request that allows the routed free model to choose platform tools."""
        client = self._require_client()
        return client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=0.1,
        )

    def complete_json(self, system_prompt: str, user_prompt: str, schema: Type[T]) -> T:
        prompt = (
            user_prompt
            + "\n\nReturn only valid JSON matching this schema:\n"
            + json.dumps(schema.model_json_schema())
        )
        error: Exception | None = None
        for _ in range(self.max_json_attempts):
            try:
                text = self.complete_text(system_prompt, prompt)
                return schema.model_validate(self._extract_json_object(text))
            except Exception as exc:
                error = exc
                prompt += (
                    "\nThe previous response could not be validated. Repair it and return JSON only. "
                    f"Validation error: {exc}"
                )
        raise RuntimeError(f"Structured response failed after retries: {error}")

    @staticmethod
    def _extract_json_object(text: str) -> dict[str, Any]:
        cleaned = re.sub(
            r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I | re.S
        )
        try:
            obj = json.loads(cleaned)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end < start:
            raise ValueError("No JSON object found in model response")
        return json.loads(cleaned[start : end + 1])
