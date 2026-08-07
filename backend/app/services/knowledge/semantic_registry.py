from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class FeatureDefinition(BaseModel):
    id: str
    canonical_name: str
    aliases: List[str] = Field(default_factory=list)
    category: str
    description: str
    ontology_path: List[str] = Field(default_factory=list) # e.g. ["Security", "Authentication", "Token Authentication", "JWT"]
    capabilities: List[str] = Field(default_factory=list)
    severity: str = "Info"
    relationships: Dict[str, List[str]] = Field(default_factory=dict)

class SemanticFeatureRegistry:
    """
    Single source of truth ontology for all semantic features, capabilities, and aliases.
    """
    def __init__(self):
        self._features: Dict[str, FeatureDefinition] = {}
        self._build_registry()

    def _build_registry(self):
        # ── API Features ────────────────────────────────────────────────────────
        self._add(FeatureDefinition(
            id="feat_rest_api",
            canonical_name="REST API",
            aliases=["REST", "RESTful API", "HTTP API"],
            category="API",
            description="RESTful web API endpoints",
            ontology_path=["API", "Web API", "REST"],
            capabilities=["API Infrastructure"]
        ))
        self._add(FeatureDefinition(
            id="feat_graphql",
            canonical_name="GraphQL API",
            aliases=["GraphQL"],
            category="API",
            description="GraphQL endpoints",
            ontology_path=["API", "Web API", "GraphQL"],
            capabilities=["API Infrastructure"]
        ))
        
        # ── Security Features ───────────────────────────────────────────────────
        self._add(FeatureDefinition(
            id="feat_jwt",
            canonical_name="JWT Authentication",
            aliases=["JWT", "JSON Web Token", "Bearer Authentication"],
            category="Security",
            description="Stateless authentication using JSON Web Tokens",
            ontology_path=["Security", "Authentication", "Token Authentication", "JWT"],
            capabilities=["Authentication & Security"],
            severity="High"
        ))
        self._add(FeatureDefinition(
            id="feat_oauth2",
            canonical_name="OAuth2",
            aliases=["OAuth", "OAuth2.0", "OpenID Connect", "OIDC"],
            category="Security",
            description="Delegated authorization using OAuth2",
            ontology_path=["Security", "Authentication", "Delegated Authentication", "OAuth2"],
            capabilities=["Authentication & Security"],
            severity="High"
        ))
        self._add(FeatureDefinition(
            id="feat_rbac",
            canonical_name="Role-Based Access Control",
            aliases=["RBAC", "Role Based Authorization"],
            category="Security",
            description="Authorization based on user roles",
            ontology_path=["Security", "Authorization", "RBAC"],
            capabilities=["Authentication & Security"],
            severity="High"
        ))
        self._add(FeatureDefinition(
            id="feat_cors",
            canonical_name="CORS Configured",
            aliases=["CORS", "Cross-Origin Resource Sharing"],
            category="Security",
            description="Cross-Origin Resource Sharing rules",
            ontology_path=["Security", "Web Security", "CORS"],
            capabilities=["Authentication & Security"]
        ))
        
        # ── Database Features ───────────────────────────────────────────────────
        self._add(FeatureDefinition(
            id="feat_orm",
            canonical_name="ORM Usage",
            aliases=["ORM", "Object Relational Mapping", "JPA", "Hibernate", "Entity Framework", "SQLAlchemy"],
            category="Database",
            description="Object-Relational Mapping to a relational database",
            ontology_path=["Database", "Data Access", "ORM"],
            capabilities=["Database Management"]
        ))
        self._add(FeatureDefinition(
            id="feat_connection_pool",
            canonical_name="Connection Pooling",
            aliases=["Connection Pool", "HikariCP", "BoneCP", "C3P0"],
            category="Database",
            description="Database connection pooling for performance",
            ontology_path=["Database", "Performance", "Connection Pooling"],
            capabilities=["Database Management"]
        ))
        self._add(FeatureDefinition(
            id="feat_migration",
            canonical_name="Database Migration",
            aliases=["Migration", "Flyway", "Liquibase", "Alembic"],
            category="Database",
            description="Database schema migration management",
            ontology_path=["Database", "Schema Management", "Migration"],
            capabilities=["Database Management"]
        ))
        
        # ── Architecture Features ───────────────────────────────────────────────
        self._add(FeatureDefinition(
            id="feat_mvc",
            canonical_name="MVC Architecture",
            aliases=["MVC", "Model-View-Controller", "Layered Architecture"],
            category="Architecture",
            description="Model-View-Controller layered architectural pattern",
            ontology_path=["Architecture", "Pattern", "MVC"],
            capabilities=["Frontend / UI", "API Infrastructure"]
        ))
        
        # ── Messaging Features ──────────────────────────────────────────────────
        self._add(FeatureDefinition(
            id="feat_event_streaming",
            canonical_name="Event Streaming",
            aliases=["Event Streaming", "Kafka", "Message Queue", "RabbitMQ", "SQS", "ActiveMQ"],
            category="Messaging",
            description="Asynchronous message or event streaming",
            ontology_path=["Messaging", "Event Streaming"],
            capabilities=["Messaging & Events"]
        ))
        
        # ── Infrastructure Features ─────────────────────────────────────────────
        self._add(FeatureDefinition(
            id="feat_docker",
            canonical_name="Docker Containerization",
            aliases=["Docker", "Containerization"],
            category="Infrastructure",
            description="Application packaged as a Docker container",
            ontology_path=["Infrastructure", "Containerization", "Docker"],
            capabilities=["Containerization"]
        ))

    def _add(self, feat: FeatureDefinition):
        self._features[feat.id] = feat

    def get_by_id(self, definition_id: str) -> Optional[FeatureDefinition]:
        return self._features.get(definition_id)

    def resolve(self, query: str) -> List[FeatureDefinition]:
        """Resolve a string query (e.g. 'JWT', 'REST API') to FeatureDefinitions via exact match or aliases."""
        results = []
        q = query.lower()
        for feat in self._features.values():
            if q == feat.id.lower() or q == feat.canonical_name.lower():
                results.append(feat)
                continue
            for alias in feat.aliases:
                if q == alias.lower():
                    results.append(feat)
                    break
        return results

    def get_all(self) -> List[FeatureDefinition]:
        return list(self._features.values())

# Singleton instance
SEMANTIC_REGISTRY = SemanticFeatureRegistry()
