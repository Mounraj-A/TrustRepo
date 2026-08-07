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
    # Normalized Repository Files
    # ------------------------------------------------------------------

    documentation_files: List[str] = field(default_factory=list)
    source_code_files: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    configuration_files: List[str] = field(default_factory=list)
    ci_cd_files: List[str] = field(default_factory=list)
    other_files: List[str] = field(default_factory=list)