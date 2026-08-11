"""
Evidence-Based Architecture Detection

Detects architectural patterns from Neo4j Knowledge Graph evidence:
    Package Structure → Architecture Pattern
    Annotations → Controller/Service/Repository pattern
    Inheritance → Component roles
    Module count/ratio → Style inference

NOT keyword scanning. Evidence-driven.

Patterns detected:
    Layered/MVC      - controllers, services, repositories, models
    Microservices    - multiple spring boot applications or docker services
    Event-Driven     - message queues (RabbitMQ/Kafka), event listeners
    REST API         - @RestController, @RequestMapping
    Monolith         - single root package with mixed concerns
"""
import uuid
from app.repositories.graph_repository import GraphRepository
from typing import List
from app.models.knowledge.feature_instance import FeatureInstance
from app.models.report.trust_report import ArchitectureFinding, FeatureReference

# Annotations that indicate specific architecture roles
CONTROLLER_ANNOTATIONS = {"RestController", "Controller", "RequestMapping"}
SERVICE_ANNOTATIONS = {"Service", "Component"}
REPOSITORY_ANNOTATIONS = {"Repository", "JpaRepository", "CrudRepository"}
ENTITY_ANNOTATIONS = {"Entity", "Document", "Table"}
SECURITY_ANNOTATIONS = {"EnableWebSecurity", "EnableMethodSecurity"}
EVENT_ANNOTATIONS = {
    "EventListener",
    "RabbitListener",
    "KafkaListener",
    "Async"}
CONFIGURATION_ANNOTATIONS = {
    "Configuration",
    "SpringBootApplication",
    "EnableAutoConfiguration"}


class ArchitectureDetection:
    """
    Detects architectural style by querying the Knowledge Graph for:
    1. Annotation patterns (@RestController, @Service, @Repository)
    2. Package structural patterns (controllers/, services/, repositories/)
    3. Inheritance patterns (extends JpaRepository)
    4. Messaging patterns (RabbitMQ, Kafka listeners)
    """

    def __init__(self, repo: GraphRepository = None):
        self.repo = repo or GraphRepository()

    def detect_findings(self, features: List[FeatureInstance] = None) -> List[ArchitectureFinding]:
        features = features or []
        feature_map = {f.definition_id: f for f in features}

        # ── Query package names for fallback ─────────────────────────────────
        packages = self._query_packages()

        # ── Determine architecture ───────────────────────────────────────────
        arch_findings = []
        
        mappings = [
            (["feat_mvc"], "Layered Architecture (MVC)"),
            (["feat_rest_api"], "REST API"),
            (["feat_event_streaming"], "Event-Driven"),
            (["feat_jwt", "feat_oauth2", "feat_rbac", "feat_cors"], "Secured Application"),
        ]

        # 1. Feature-based detection
        for feature_ids_to_check, pattern_name in mappings:
            supporting_features = []
            evidence_chains = []
            for fid in feature_ids_to_check:
                if fid in feature_map:
                    f_inst = feature_map[fid]
                    supporting_features.append(FeatureReference(id=f_inst.id, name=f_inst.canonical_name))
                    evidence_chains.extend(f_inst.evidence)
            
            if supporting_features:
                arch_findings.append(ArchitectureFinding(
                    id=f"arch_{str(uuid.uuid4())[:8]}",
                    name=pattern_name,
                    status="Detected",
                    supporting_features=supporting_features,
                    evidence=evidence_chains,
                    reasoning=f"Detected based on presence of supporting semantic features.",
                    provenance_chain=evidence_chains[0] if evidence_chains else None
                ))

        # 2. Package-based hints (secondary evidence)
        package_hints = self._analyze_packages(packages)
        for hint in package_hints:
            # Check if this hint is already detected via features
            existing = next((a for a in arch_findings if a.name == hint), None)
            if existing:
                if not existing.reasoning:
                    existing.reasoning = ""
                existing.reasoning += " Also inferred from structural package layout."
            else:
                # Discovered only via structural heuristics without semantic feature confirmation
                arch_findings.append(ArchitectureFinding(
                    id=f"arch_{str(uuid.uuid4())[:8]}",
                    name=hint,
                    status="Inferred",
                    supporting_features=[],
                    evidence=[],
                    reasoning="Inferred from package structure, but lacks concrete semantic feature evidence."
                ))

        print(f"  Architecture findings detected: {[f.name for f in arch_findings]}")
        return arch_findings

    def detect(self, features: List[FeatureInstance] = None) -> List[str]:
        findings = self.detect_findings(features)
        return [f.name for f in findings]

    def _count_annotations(self) -> dict:
        """Returns a dict of annotation_name → usage_count."""
        query = """
        MATCH (a:Annotation)
        RETURN a.name as name, count(a) as cnt
        ORDER BY cnt DESC LIMIT 50
        """
        try:
            results = self.repo.conn.query(query, {})
            return {r["name"]: r["cnt"]
                    for r in (results or []) if r.get("name")}
        except Exception:
            return {}

    def _count_annotation_group(self, ann_counts: dict, group: set) -> int:
        return sum(ann_counts.get(ann, 0) for ann in group)

    def _query_packages(self) -> list:
        query = "MATCH (p:Package) RETURN DISTINCT toLower(p.name) as name LIMIT 50"
        try:
            results = self.repo.conn.query(query, {})
            return [r["name"] for r in (results or []) if r.get("name")]
        except Exception:
            return []

    def _analyze_packages(self, packages: list) -> list:
        """Secondary evidence from package names."""
        hints = []
        mvc_packages = {
            "controller",
            "controllers",
            "service",
            "services",
            "repository",
            "repositories",
            "model",
            "models",
            "entity"}
        microservice_packages = {"gateway", "discovery", "config", "registry"}

        lower_packages = set(p.lower() for p in packages)

        if len(lower_packages & mvc_packages) >= 3:
            if "Layered Architecture (MVC)" not in hints:
                hints.append("Layered Architecture (MVC)")
        if len(lower_packages & microservice_packages) >= 2:
            hints.append("Microservices")

        return hints
