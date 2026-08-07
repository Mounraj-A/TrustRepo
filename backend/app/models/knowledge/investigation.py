from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime
from app.models.knowledge.evidence import EvidenceContext, EvidenceCandidate

class VerificationVerdict(str, Enum):
    VERIFIED = "VERIFIED"
    CONTRADICTION = "CONTRADICTION"
    MISSING_DOCUMENTATION = "MISSING_DOCUMENTATION"
    UNSUPPORTED_DOCUMENTATION = "UNSUPPORTED_DOCUMENTATION"
    PARTIAL_DOCUMENTATION = "PARTIAL_DOCUMENTATION"

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
    
    # Expected vs Observed Model Output
    expected_features: List[str] = Field(default_factory=list)
    observed_features: List[str] = Field(default_factory=list)
    missing_features: List[str] = Field(default_factory=list)
    unsupported_features: List[str] = Field(default_factory=list)
    contradicted_features: List[str] = Field(default_factory=list)
    
    # Reasoning Metrics
    evidence_count: int = 0
    evidence_diversity: float = 0.0
    evidence_quality: float = 0.0
    graph_connectivity: float = 0.0
    evidence_agreement: float = 0.0
    
    verification_timestamp: datetime = Field(default_factory=datetime.utcnow)
    verification_version: str = "2.0.0"
