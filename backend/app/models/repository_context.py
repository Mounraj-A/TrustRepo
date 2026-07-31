from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class RepositoryContext:
    """
    Repository Context

    Central data object shared between all TrustRepo layers.
    Layer 1 produces this object, and subsequent layers enrich it.
    """

    # ------------------------------------------------------------------
    # Repository Information
    # ------------------------------------------------------------------

    repository_name: str = ""
    repository_url: str = ""
    repository_path: str = ""

    # ------------------------------------------------------------------
    # Repository Metadata
    # ------------------------------------------------------------------

    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Normalized Repository Files
    # ------------------------------------------------------------------

    documentation_files: List[str] = field(default_factory=list)
    source_code_files: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    configuration_files: List[str] = field(default_factory=list)
    ci_cd_files: List[str] = field(default_factory=list)
    other_files: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Future Layers
    # ------------------------------------------------------------------

    repository_graph: Any = None
    functional_modules: List[Any] = field(default_factory=list)
    extracted_claims: List[Any] = field(default_factory=list)
    evidence_plan: List[Any] = field(default_factory=list)
    verification_results: List[Any] = field(default_factory=list)
    confidence_scores: Dict[str, Any] = field(default_factory=dict)
    trust_report: Dict[str, Any] = field(default_factory=dict)