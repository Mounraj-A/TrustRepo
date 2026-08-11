from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import uuid

from app.models.repository_context import RepositoryContext
from app.models.document_context import DocumentContext
from app.models.code.code_context import CodeContext
from app.models.claim import Claim
from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph
from app.models.knowledge.evidence import EvidenceContext
from app.models.knowledge.investigation import InvestigationResult, VerificationResult
from app.models.report.trust_report import RepositoryReport, ArchitectureFinding, ReasoningTrace


class SemanticContext(BaseModel):
    technologies: List[str] = Field(default_factory=list)
    technology_categories: Dict[str, List[str]] = Field(default_factory=dict)
    features: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    architectures: List[str] = Field(default_factory=list)
    architecture_findings: List[ArchitectureFinding] = Field(default_factory=list)
    evidence_chains: List[Any] = Field(default_factory=list)
    reasoning_traces: List[ReasoningTrace] = Field(default_factory=list)


class GraphContext(BaseModel):
    graph: Optional[RepositoryKnowledgeGraph] = None
    analytics: Dict[str, Any] = Field(default_factory=dict)


class EvidenceContextData(BaseModel):
    contexts: Dict[str, EvidenceContext] = Field(default_factory=dict)


class VerificationContext(BaseModel):
    investigation_results: Dict[str, InvestigationResult] = Field(
        default_factory=dict)
    verification_results: Dict[str, VerificationResult] = Field(
        default_factory=dict)


class ReportContext(BaseModel):
    report: Optional[RepositoryReport] = None


class TrustRepoContext(BaseModel):
    """
    Master state object for the entire TrustRepo pipeline.
    Stores all intermediate artifacts to ensure perfect traceability.
    """
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    repository_context: Optional[RepositoryContext] = None
    document_context: Optional[DocumentContext] = None
    code_context: Optional[CodeContext] = None
    graph_context: GraphContext = Field(default_factory=GraphContext)
    semantic_context: SemanticContext = Field(default_factory=SemanticContext)
    evidence_context: EvidenceContextData = Field(
        default_factory=EvidenceContextData)
    verification_context: VerificationContext = Field(
        default_factory=VerificationContext)
    report_context: ReportContext = Field(default_factory=ReportContext)

    claims: List[Claim] = Field(default_factory=list)

    # Phase 10: Runtime Dashboard — per-layer execution trace
    execution_trace: List[Dict[str, Any]] = Field(default_factory=list)

    # Phase 11: Code Intelligence Mode — populated when no docs exist
    code_intelligence: Dict[str, Any] = Field(default_factory=dict)
