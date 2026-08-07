from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class RepositoryContext:
    """
    Repository Context

    Central data object shared between all TrustRepo layers.
    Layer 1 produces this object, and subsequent layers enrich it.

    Every list field corresponds to an evidence category from RepositoryScanner.
    Downstream parsers read these lists to determine what to parse.
    """

    # ------------------------------------------------------------------
    # Repository Information
    # ------------------------------------------------------------------

    repository_name: str = ""
    repository_url: str = ""
    repository_path: str = ""

    # ------------------------------------------------------------------
    # Repository Metadata (from git / service layer)
    # ------------------------------------------------------------------

    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Evidence Categories (produced by RepositoryScanner)
    # Each category feeds a different set of parsers / evidence engines
    # ------------------------------------------------------------------

    # Source files for AST parsing (Python, Java, JS/TS, Go, Rust…)
    source_code_files: List[str] = field(default_factory=list)

    # Test files — separate from source for test-coverage evidence
    test_files: List[str] = field(default_factory=list)

    # Human-readable documentation (README, docs/, CHANGELOG…)
    documentation_files: List[str] = field(default_factory=list)

    # Build tool manifests (pom.xml, build.gradle, Cargo.toml…)
    build_files: List[str] = field(default_factory=list)

    # Package manager manifests (requirements.txt, package.json, Pipfile…)
    package_manifests: List[str] = field(default_factory=list)

    # Docker / Compose files
    infrastructure_files: List[str] = field(default_factory=list)

    # CI/CD pipeline definitions (.github/workflows/, Jenkinsfile…)
    ci_cd_files: List[str] = field(default_factory=list)

    # Infrastructure-as-Code (Terraform, Helm, Kubernetes YAML…)
    infrastructure_as_code_files: List[str] = field(default_factory=list)

    # App configuration files (.env, application.yml, *.ini…)
    configuration_files: List[str] = field(default_factory=list)

    # Shell / PowerShell / batch scripts
    script_files: List[str] = field(default_factory=list)

    # Generated code / migration files (excluded from most parsers)
    generated_files: List[str] = field(default_factory=list)

    # Static assets — images, fonts, media (lowest evidence priority)
    asset_files: List[str] = field(default_factory=list)

    # Catch-all for unrecognised files
    other_files: List[str] = field(default_factory=list)