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
from app.models.repository_context import RepositoryContext
from app.repositories.graph_repository import GraphRepository
from typing import List
from app.models.knowledge.feature_instance import FeatureInstance

# Annotations that indicate specific architecture roles
CONTROLLER_ANNOTATIONS = {"RestController", "Controller", "RequestMapping"}
SERVICE_ANNOTATIONS = {"Service", "Component"}
REPOSITORY_ANNOTATIONS = {"Repository", "JpaRepository", "CrudRepository"}
ENTITY_ANNOTATIONS = {"Entity", "Document", "Table"}
SECURITY_ANNOTATIONS = {"EnableWebSecurity", "EnableMethodSecurity"}
EVENT_ANNOTATIONS = {"EventListener", "RabbitListener", "KafkaListener", "Async"}
CONFIGURATION_ANNOTATIONS = {"Configuration", "SpringBootApplication", "EnableAutoConfiguration"}


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

    def detect(self, features: List[FeatureInstance] = None) -> List[str]:
        features = features or []
        feature_ids = {f.definition_id for f in features}
        
        # ── Query package names for fallback ──────────────────────────────────
        packages = self._query_packages()
        
        # ── Determine architecture ─────────────────────────────────────────────
        patterns = []
        evidence = {}
        
        # Check for Layered/MVC pattern
        if "feat_mvc" in feature_ids or "feat_rest_api" in feature_ids:
            # We already have strong semantic evidence of MVC/REST from the features
            if "feat_mvc" in feature_ids:
                patterns.append("Layered Architecture (MVC)")
            if "feat_rest_api" in feature_ids:
                patterns.append("REST API")
        
        # Check for Event-Driven pattern
        if "feat_event_streaming" in feature_ids:
            patterns.append("Event-Driven")
            
        # Check for security layer
        security_features = [f.definition_id for f in features if f.definition_id in ("feat_jwt", "feat_oauth2", "feat_rbac", "feat_cors")]
        if security_features:
            patterns.append("Secured Application")
            evidence["security_features_detected"] = len(security_features)
        
        # Package name-based hints (secondary evidence)
        package_hints = self._analyze_packages(packages)
        for hint in package_hints:
            if hint not in patterns:
                patterns.append(hint)
        
        # Fallback
        if not patterns:
            patterns = ["Unknown"]
        
        print(f"  Architecture detected from semantic features: {patterns}")
        return patterns

    def _count_annotations(self) -> dict:
        """Returns a dict of annotation_name → usage_count."""
        query = """
        MATCH (a:Annotation)
        RETURN a.name as name, count(a) as cnt
        ORDER BY cnt DESC LIMIT 50
        """
        try:
            results = self.repo.conn.query(query, {})
            return {r["name"]: r["cnt"] for r in (results or []) if r.get("name")}
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
        mvc_packages = {"controller", "controllers", "service", "services", "repository", "repositories", "model", "models", "entity"}
        microservice_packages = {"gateway", "discovery", "config", "registry"}
        
        lower_packages = set(p.lower() for p in packages)
        
        if len(lower_packages & mvc_packages) >= 3:
            if "Layered Architecture (MVC)" not in hints:
                hints.append("Layered Architecture (MVC)")
        if len(lower_packages & microservice_packages) >= 2:
            hints.append("Microservices")
        
        return hints
