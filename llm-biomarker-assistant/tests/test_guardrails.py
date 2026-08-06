import pytest
from src.guardrails import UnsupportedCitationError, validate_citations
from src.schemas import StructuredAnswer, EvidenceCitation


def base_answer() -> StructuredAnswer:
    return StructuredAnswer(
        direct_answer="Test",
        biological_rationale=[],
        supporting_studies=[EvidenceCitation(document_id="DOC-1", statement="Test", evidence_quality="low")],
        candidate_biomarkers=[], contradictory_evidence=[], confidence="low",
        confidence_rationale="Test", limitations=[], cited_document_ids=["DOC-1"]
    )


def test_valid_citation_passes():
    validate_citations(base_answer(), {"DOC-1"})


def test_unsupported_citation_fails():
    with pytest.raises(UnsupportedCitationError):
        validate_citations(base_answer(), {"DOC-2"})
