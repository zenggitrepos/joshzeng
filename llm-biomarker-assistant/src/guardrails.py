from __future__ import annotations
from src.schemas import StructuredAnswer

class UnsupportedCitationError(ValueError):
    pass


def validate_citations(answer: StructuredAnswer, allowed_document_ids: set[str]) -> None:
    cited = set(answer.cited_document_ids)
    for study in answer.supporting_studies + answer.contradictory_evidence:
        cited.add(study.document_id)
    for biomarker in answer.candidate_biomarkers:
        cited.update(biomarker.supporting_document_ids)
    unsupported = cited - allowed_document_ids
    if unsupported:
        raise UnsupportedCitationError(
            f"Model cited documents that were not retrieved: {sorted(unsupported)}"
        )


def enforce_minimum_evidence(answer: StructuredAnswer) -> StructuredAnswer:
    if not answer.supporting_studies:
        answer.confidence = "insufficient_evidence"
        answer.confidence_rationale = (
            "No supporting study was cited from the retrieved evidence."
        )
    return answer
