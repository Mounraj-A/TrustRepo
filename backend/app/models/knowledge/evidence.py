import uuid
import hashlib
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timezone

from app.models.claim import Claim


class EvidenceStrength(str, Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    SUPPORTING = "SUPPORTING"


class EvidenceType(str, Enum):
    SOURCE_CODE = "SOURCE_CODE"
    DOCUMENTATION = "DOCUMENTATION"
    AST = "AST"
    GRAPH = "GRAPH"
    TEST = "TEST"
    CI = "CI"
    ISSUE = "ISSUE"
    PR = "PR"
    CONFIGURATION = "CONFIGURATION"
    STRUCTURAL = "STRUCTURAL"
    IMPORT = "IMPORT"
    ANNOTATION = "ANNOTATION"
    DEPENDENCY = "DEPENDENCY"
    CALL = "CALL"
    DECLARATION = "DECLARATION"
    INSTANTIATION = "INSTANTIATION"
    UNKNOWN = "UNKNOWN"


class EvidenceSource(BaseModel):
    """Deep provenance metadata for reproducibility."""
    repository_id: str = "local"
    repository_relative_path: str = ""
    commit_sha: str = "HEAD"
    branch: str = "main"
    language: str = "unknown"
    file_path: str = "unknown"
    line_number: Optional[int] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    column: Optional[int] = None
    parser_used: str = "unknown"
    parser_version: str = "1.0"
    analysis_version: str = "2.0.0"
    reasoning_engine_version: str = "2.0.0"
    analysis_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))


class EvidenceItem(BaseModel):
    """A discrete piece of evidence derived from the UIR or Knowledge Graph."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: EvidenceSource
    node_type: str = "unknown"
    symbol_kind: str = "unknown"
    symbol: str = "unknown"
    qualified_name: str = "unknown"
    context_type: str = "unknown"
    evidence_type: EvidenceType = EvidenceType.UNKNOWN
    code_snippet: Optional[str] = None
    graph_node_id: Optional[str] = None
    graph_relationship: Optional[str] = None
    evidence_strength: EvidenceStrength = EvidenceStrength.SUPPORTING
    extraction_method: str = "unknown"
    source_reference: Optional[str] = None
    explanation: Optional[str] = None

    @property
    def hash(self) -> str:
        """Deterministic hash for caching and deduplication."""
        h = hashlib.sha256()
        h.update(self.source.file_path.encode('utf-8'))
        h.update(str(self.source.line_number or 0).encode('utf-8'))
        h.update(self.symbol.encode('utf-8'))
        h.update(self.evidence_type.value.encode('utf-8'))
        return h.hexdigest()


class DocumentationSearchResult(BaseModel):
    """Explicit record of a documentation search for negative evidence tracking."""
    searched_sources: List[str] = Field(default_factory=list)
    searched_terms: List[str] = Field(default_factory=list)
    matches: List[str] = Field(default_factory=list)
    search_method: str = "string_match"
    found: bool = False
    search_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))


class EvidenceChain(BaseModel):
    """A full traversal path representing a complete reasoning context."""
    chain_id: str
    chain_type: str = "Graph Traversal"
    retrieval_strategy: str = "Hybrid"
    sequence: List[EvidenceItem] = Field(default_factory=list)
    graph_path: str = ""
    ranking_score: float = 0.0
    confidence: float = 0.0
    reasoning_trace: str = ""

# Legacy or intermediate models for compatibility during refactoring


class EvidenceCandidate(BaseModel):
    source_engine: str
    content: str
    file_path: Optional[str] = None
    content_snippet: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chain: Optional[EvidenceChain] = None


class EvidenceContext(BaseModel):
    claim: Claim
    candidates: List[EvidenceCandidate] = Field(default_factory=list)
    chains: List[EvidenceChain] = Field(default_factory=list)

    def add_candidates(self, new_candidates: List[EvidenceCandidate]):
        self.candidates.extend(new_candidates)
