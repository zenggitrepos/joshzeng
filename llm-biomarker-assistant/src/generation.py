from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI
from pydantic import ValidationError

from src.config import settings
from src.guardrails import enforce_minimum_evidence, validate_citations
from src.retrieval import RetrievedEvidence
from src.schemas import StructuredAnswer

SYSTEM_PROMPT = """You are a translational biomarker evidence assistant.
Use ONLY the supplied evidence passages. Never use unstated background knowledge.
Every study-level or biomarker claim must cite one or more supplied document IDs.
Clearly distinguish validated biomarkers, clinical associations, and hypotheses.
Discuss conflicting evidence. If evidence is weak, synthetic, indirect, or absent, say so.
Do not provide medical advice.
Return ONLY one valid JSON object matching the supplied schema. Do not use markdown fences.
"""


def evidence_context(evidence: list[RetrievedEvidence]) -> str:
    blocks: list[str] = []
    for item in evidence:
        blocks.append(
            f"DOCUMENT_ID: {item.document_id}\n"
            f"TITLE: {item.metadata.get('title')}\n"
            f"SOURCE_TYPE: {item.metadata.get('source_type')}\n"
            f"EVIDENCE_LEVEL: {item.metadata.get('evidence_level')}\n"
            f"SYNTHETIC: {item.metadata.get('is_synthetic')}\n"
            f"TEXT: {item.text}"
        )
    return "\n\n---\n\n".join(blocks)


def _client() -> OpenAI:
    if settings.llm_provider.lower() != "openrouter":
        raise ValueError(
            "This free-hosted edition supports LLM_PROVIDER=openrouter."
        )
    if not settings.openrouter_api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is missing. Create a free OpenRouter key and add "
            "it to the .env file. Do not paste the key into source code."
        )
    return OpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        timeout=settings.request_timeout_seconds,
        default_headers={
            "HTTP-Referer": settings.app_url,
            "X-OpenRouter-Title": settings.app_name,
        },
    )


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        value = json.loads(cleaned)
        if not isinstance(value, dict):
            raise ValueError("The model output was JSON, but not a JSON object.")
        return value
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            value = json.loads(cleaned[start : end + 1])
            if isinstance(value, dict):
                return value
        raise


def _user_prompt(question: str, evidence: list[RetrievedEvidence]) -> str:
    schema = StructuredAnswer.model_json_schema()
    return (
        f"QUESTION:\n{question}\n\n"
        f"EVIDENCE:\n{evidence_context(evidence)}\n\n"
        "OUTPUT JSON SCHEMA:\n"
        f"{json.dumps(schema, indent=2)}"
    )


def generate_answer(question: str, evidence: list[RetrievedEvidence]) -> StructuredAnswer:
    if not evidence:
        return StructuredAnswer(
            direct_answer="Insufficient retrieved evidence to answer the question.",
            biological_rationale=[],
            supporting_studies=[],
            candidate_biomarkers=[],
            contradictory_evidence=[],
            confidence="insufficient_evidence",
            confidence_rationale="No evidence passages were retrieved.",
            limitations=["The corpus may not cover the question."],
            cited_document_ids=[],
        )

    client = _client()
    allowed_ids = {item.document_id for item in evidence}
    last_error: Exception | None = None

    for attempt in range(1, settings.max_generation_attempts + 1):
        repair_instruction = ""
        if last_error is not None:
            repair_instruction = (
                "\n\nYour previous response failed validation. Return corrected JSON only. "
                f"Validation problem: {last_error}"
            )

        try:
            response = client.chat.completions.create(
                model=settings.openrouter_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": _user_prompt(question, evidence)
                        + repair_instruction,
                    },
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if not content:
                raise RuntimeError("The free model returned an empty response.")
            answer = StructuredAnswer.model_validate(_extract_json(content))
            validate_citations(answer, allowed_ids)
            return enforce_minimum_evidence(answer)
        except (json.JSONDecodeError, ValidationError, ValueError, RuntimeError) as exc:
            last_error = exc
            if attempt == settings.max_generation_attempts:
                break

    raise RuntimeError(
        "The selected free model could not produce a valid citation-grounded JSON "
        f"answer after {settings.max_generation_attempts} attempts. Last error: {last_error}"
    )
