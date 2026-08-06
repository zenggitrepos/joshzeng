from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class EvidenceRecord(BaseModel):
    document_id: str
    source_type: str
    title: str
    year: int | None = None
    disease: str | None = None
    interventions: list[str] = Field(default_factory=list)
    biomarkers: list[str] = Field(default_factory=list)
    evidence_level: str
    study_design: str
    text: str
    url: str | None = None
    is_synthetic: bool = False

class EvidenceCitation(BaseModel):
    document_id: str
    statement: str
    evidence_quality: Literal["high", "moderate", "low", "uncertain"]

class BiomarkerCandidate(BaseModel):
    name: str
    rationale: str
    status: Literal["validated", "clinical_association", "hypothesis_generating", "unknown"]
    supporting_document_ids: list[str]

class StructuredAnswer(BaseModel):
    direct_answer: str
    biological_rationale: list[str]
    supporting_studies: list[EvidenceCitation]
    candidate_biomarkers: list[BiomarkerCandidate]
    contradictory_evidence: list[EvidenceCitation]
    confidence: Literal["high", "moderate", "low", "insufficient_evidence"]
    confidence_rationale: str
    limitations: list[str]
    cited_document_ids: list[str]
