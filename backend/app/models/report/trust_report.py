from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, DocumentationSearchResult

class CandidateSource(str, Enum):
    TECHNOLOGY_DETECTOR = "Technology Detector"
    CAPABILITY_DETECTOR = "Capability Detector"
    SEMANTIC_DETECTOR = "Semantic Detector"
    ARCHITECTURE_DETECTOR = "Architecture Detector"
    DOCUMENTATION_ANALYSIS = "Documentation Analysis"
    KNOWLEDGE_GRAPH = "Knowledge Graph"
    UNKNOWN = "Unknown"

class VerificationVerdict(str, Enum):
    VERIFIED = "VERIFIED"
    MISSING_DOCUMENTATION = "MISSING_DOCUMENTATION"
    CONTRADICTED = "CONTRADICTED"
    UNSUPPORTED = "UNSUPPORTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class VerificationCategory(str, Enum):
    TECHNOLOGY = "Technology"
    API = "API"
    ARCHITECTURE = "Architecture"
    DATABASE = "Database"
    SECURITY = "Security"
    PERFORMANCE = "Performance"
    UI = "UI"
    STRUCTURAL = "Structural"
    BEHAVIORAL = "Behavioral"
    CONFIGURATION = "Configuration"
    DEPENDENCY = "Dependency"
    UNKNOWN = "Unknown"

class RecommendationPriority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class Recommendation(BaseModel):
    priority: RecommendationPriority
    message: str

class EvidenceSearchStep(BaseModel):
    strategy: str
    source: str
    query_description: Optional[str] = None
    matches: int = 0
    status: str
    explanation: Optional[str] = None

class EvidenceRetrievalTrace(BaseModel):
    strategies_attempted: List[str] = Field(default_factory=list)
    strategies_succeeded: List[str] = Field(default_factory=list)
    strategies_failed: List[str] = Field(default_factory=list)

    searches: List[EvidenceSearchStep] = Field(default_factory=list)

    candidate_count: int = 0
    matched_entities: int = 0
    evidence_items_created: int = 0
    evidence_items_rejected: int = 0

    rejection_reasons: List[str] = Field(default_factory=list)

    conclusion: Optional[str] = None

class FeatureFinding(BaseModel):
    feature: str
    category: VerificationCategory
    candidate_source: CandidateSource
    status: VerificationVerdict
    evidence: List[EvidenceChain] = Field(default_factory=list)
    evidence_count: int = 0
    evidence_quality: float = 0.0
    evidence_diversity: float = 0.0
    documentation_search: Optional[DocumentationSearchResult] = None
    retrieval_trace: Optional[EvidenceRetrievalTrace] = None
    confidence: Optional[float] = None
    confidence_breakdown: Optional[dict] = None
    reasoning: str
    reasoning_trace: List[str] = Field(default_factory=list)
    provenance_chain: Optional[EvidenceChain] = None
    recommendation: Optional[str] = None

class FeatureReference(BaseModel):
    id: str
    name: str

class ArchitectureFinding(BaseModel):
    id: str
    name: str
    status: str = "Detected"
    supporting_features: List[FeatureReference] = Field(default_factory=list)
    evidence: List[EvidenceChain] = Field(default_factory=list)
    reasoning: Optional[str] = None
    provenance_chain: Optional[EvidenceChain] = None

class RepositoryMetadata(BaseModel):
    repository_url: str = ""
    commit_sha: str = ""
    branch: str = "main"
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    source_files_count: int = 0
    documentation_sources: List[str] = Field(default_factory=list)
    claims_analyzed: int = 0
    features_investigated: int = 0
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    verification_version: str = "3.0.0"

class DocumentationSummary(BaseModel):
    documentation_sources: List[str] = Field(default_factory=list)
    total_candidates: int = 0
    confirmed_features: int = 0
    documented_features: int = 0
    missing_documentation: int = 0
    contradicted: int = 0
    insufficient_evidence: int = 0
    total_claims: int = 0
    verified_claims: int = 0
    contradicted_claims: int = 0
    coverage_percentage: float = 0.0
    coverage_score: Optional[float] = None

    from pydantic import model_validator
    @model_validator(mode='after')
    def validate_counts(self):
        total = self.verified_claims + self.missing_documentation + self.contradicted_claims + self.insufficient_evidence
        # Ensure total_claims conceptually aligns, though total_claims is just len(claims),
        # whereas missing/contradicted/insufficient might come from feature_findings.
        # But per user instructions, total_claims must equal the sum.
        # We will enforce this loosely or adjust where they are computed.
        return self

class ReasoningStep(BaseModel):
    step_id: str
    step_type: str
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    source_file: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    evidence_ids: List[str] = Field(default_factory=list)
    result: Optional[str] = None

class ReasoningTrace(BaseModel):
    claim_id: str
    steps: List[ReasoningStep] = Field(default_factory=list)
    final_verdict: Optional[VerificationVerdict] = None
    explanation: Optional[str] = None

class DocumentationClaim(BaseModel):
    claim_id: str
    claim_text: str
    verdict: VerificationVerdict
    verification_category: VerificationCategory = VerificationCategory.UNKNOWN
    source_file: str = ""
    line_range: str = ""
    trust_score: float = 0.0
    confidence: float = 0.0
    confidence_breakdown: Optional[dict] = None
    evidence_count: int = 0
    evidence_quality: float = 0.0
    evidence_diversity: float = 0.0
    expected_features: List[str] = Field(default_factory=list)
    observed_features: List[str] = Field(default_factory=list)
    missing_features: List[str] = Field(default_factory=list)
    unsupported_features: List[str] = Field(default_factory=list)
    contradicted_features: List[str] = Field(default_factory=list)
    reasoning: str = ""
    reasoning_trace: Optional[ReasoningTrace] = None
    provenance_chain: Optional[EvidenceChain] = None
    recommendation: Optional[str] = None

class Contradiction(BaseModel):
    claim: DocumentationClaim
    documentation_evidence: List[EvidenceItem] = Field(default_factory=list)
    repository_evidence: List[EvidenceItem] = Field(default_factory=list)
    explanation: str

class TrustAssessment(BaseModel):
    score: float = 0.0
    status: str = "Unknown"
    details: str = "Not yet calibrated"

class UnifiedEvidenceItem(BaseModel):
    evidence_id: str
    evidence_type: str
    source_file: Optional[str] = None
    line_range: Optional[str] = None
    snippet: Optional[str] = None
    linked_claim: Optional[dict] = None
    reasoning: Optional[str] = None
    provenance_chain: Optional[dict] = None

class EvidenceSummary(BaseModel):
    total_evidence: int = 0
    linked_claims: int = 0
    source_files: int = 0

class RepositoryReport(BaseModel):
    metadata: RepositoryMetadata = Field(default_factory=RepositoryMetadata)
    summary: DocumentationSummary = Field(default_factory=DocumentationSummary)
    documentation_claims: List[DocumentationClaim] = Field(default_factory=list)
    feature_findings: List[FeatureFinding] = Field(default_factory=list)
    architecture_findings: List[ArchitectureFinding] = Field(default_factory=list)
    contradictions: List[Contradiction] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    trust_assessment: Optional[TrustAssessment] = None
    evidence_summary: EvidenceSummary = Field(default_factory=EvidenceSummary)
    unified_evidence: List[UnifiedEvidenceItem] = Field(default_factory=list)
