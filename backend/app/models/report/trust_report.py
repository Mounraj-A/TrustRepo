from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from app.models.knowledge.investigation import VerificationVerdict
from enum import Enum

from app.models.knowledge.evidence import EvidenceChain

class VerificationCategory(str, Enum):
    STRUCTURAL = "Structural"
    BEHAVIORAL = "Behavioral"
    CONFIGURATION = "Configuration"
    DEPENDENCY = "Dependency"
    ARCHITECTURE = "Architecture"
    SECURITY = "Security"
    UNKNOWN = "Unknown"

class RecommendationPriority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class Recommendation(BaseModel):
    priority: RecommendationPriority
    message: str

class UndocumentedFeature(BaseModel):
    feature_name: str
    status: str = "⚠ Missing"
    evidence_chain: Optional[EvidenceChain] = None
    reason: str = ""
    documentation_analysis: str = ""
    verdict: str = "Missing Documentation"
    confidence: float = 0.0
    recommendation: str

class DocumentationCoverage(BaseModel):
    detected_features: int = 0
    documented_features: int = 0
    verified_features: int = 0
    contradicted_features: int = 0
    missing_features: int = 0
    coverage_percentage: int = 0

class RepositorySummary(BaseModel):
    repository_url: str = ""
    commit_sha: str = ""
    branch: str = "main"
    technologies: List[str] = Field(default_factory=list)
    architecture: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    total_claims: int = 0
    verified_claims: int = 0
    refuted_claims: int = 0
    insufficient_claims: int = 0
    repository_trust_score: float = 0.0
    status: str = "Unknown"
    verification_version: str = "2.0.0"
    verification_timestamp: datetime = Field(default_factory=datetime.utcnow)

class ClaimReport(BaseModel):
    claim_id: str
    claim_text: str
    verdict: VerificationVerdict
    verification_category: VerificationCategory = VerificationCategory.UNKNOWN
    trust_score: float
    explanation: str
    provenance_chain: Optional[EvidenceChain] = None

class RepositoryTrustReport(BaseModel):
    summary: RepositorySummary
    claim_reports: List[ClaimReport] = Field(default_factory=list)
    undocumented_features: List[UndocumentedFeature] = Field(default_factory=list)
    coverage: DocumentationCoverage = Field(default_factory=DocumentationCoverage)
    recommendations: List[Recommendation] = Field(default_factory=list)
