from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime
from app.models.knowledge.evidence import EvidenceContext, EvidenceCandidate

class VerificationVerdict(str, Enum):
    VERIFIED = "VERIFIED"
    REFUTED = "REFUTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"

class InvestigationResult(BaseModel):
    """The final output from the InvestigatorAgent."""
    evidence_context: EvidenceContext
    confidence: float
    missing_evidence: List[str] = Field(default_factory=list)
    reasoning_trace: List[str] = Field(default_factory=list)
    recommended_action: str
    retrieval_attempts: int

class VerificationResult(BaseModel):
    """The final verified output from the VerificationEngine."""
    claim_id: str
    verdict: VerificationVerdict
    trust_score: float
    supporting_evidence: List[EvidenceCandidate] = Field(default_factory=list)
    reasoning_trace: List[str] = Field(default_factory=list)
    verification_timestamp: datetime = Field(default_factory=datetime.utcnow)
    verification_version: str = "1.0.0"
