"""
Technology & Architecture Ontology

An explicit, hierarchical ontology for claim normalization.
Instead of hardcoded synonyms, every normalization comes from the ontology tree.

Architecture position: ClaimNormalizationLayer → Ontology → Expected Features

Ontology Design:
    Intent Mapping      — Claim text → high-level intent (e.g., "Uses Spring Security" → Authentication)
    Feature Mapping     — Intent → concrete expected features (Authentication → ["JWT", "OAuth2", "RBAC"])
    Technology Mapping  — Technology names → categories
    Architecture Mapping — Architecture patterns → sub-features
"""
from typing import List, Dict, Set


class Ontology:
    """
    Ontology-driven normalization. Every recognized claim is mapped to its
    canonical feature set through a formal intent tree.
    """

    # ─── Intent Mapping ─────────────────────────────────────────────────────
    # Maps raw claim text synonyms to canonical intents
    INTENT_MAP: Dict[str, str] = {
        # Authentication & Authorization
        "secure login": "Authentication",
        "authentication": "Authentication",
        "authorization": "Authorization",
        "login": "Authentication",
        "auth": "Authentication",
        "access control": "Authorization",
        "role-based": "Authorization",
        "rbac": "Authorization",
        "oauth2": "OAuth2",
        "oauth": "OAuth2",
        "jwt": "JWT",
        "json web token": "JWT",
        "bearer token": "JWT",
        "spring security": "SpringSecurity",
        "web security": "SpringSecurity",
        "keycloak": "Keycloak",

        # Database
        "database": "Database",
        "persistence": "Database",
        "jpa": "JPA",
        "hibernate": "JPA",
        "sql": "Database",
        "relational": "Database",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL",
        "mongodb": "MongoDB",
        "nosql": "MongoDB",
        "neo4j": "Neo4j",

        # API
        "rest api": "REST_API",
        "restful": "REST_API",
        "endpoints": "REST_API",
        "graphql": "GraphQL",
        "grpc": "gRPC",
        "swagger": "APIDocumentation",
        "openapi": "APIDocumentation",

        # Caching
        "caching": "Caching",
        "cache": "Caching",
        "redis": "Redis",
        "memcached": "Memcached",

        # Messaging
        "messaging": "Messaging",
        "message broker": "Messaging",
        "kafka": "Kafka",
        "rabbitmq": "RabbitMQ",
        "event-driven": "EventDriven",

        # Architecture
        "microservices": "Microservices",
        "monolith": "Monolith",
        "monolithic": "Monolith",
        "serverless": "Serverless",
        "event driven": "EventDriven",
        "layered architecture": "LayeredArchitecture",
        "mvc": "MVC",
        "spring boot": "SpringBoot",
        "spring mvc": "SpringMVC",
        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",

        # Containerization
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "container": "Docker",
        "k8s": "Kubernetes",
    }

    # ─── Feature Mapping ────────────────────────────────────────────────────
    # Maps canonical intents to concrete expected code features
    FEATURE_MAP: Dict[str, List[str]] = {
        "Authentication": ["SpringSecurity", "JWT", "OAuth2", "Keycloak", "Authentication"],
        "Authorization": ["RBAC", "RoleBasedAccess", "Authorization", "SpringSecurity"],
        "JWT": ["JWT", "JwtFilter", "JwtProvider", "JwtTokenUtil"],
        "OAuth2": ["OAuth2", "OAuth2Login", "OAuth2ResourceServer"],
        "SpringSecurity": ["SpringSecurity", "WebSecurityConfigurer", "SecurityFilterChain"],
        "Keycloak": ["Keycloak", "KeycloakAdapter", "KeycloakSpringBootConfigResolver"],
        "Database": ["JPA", "MySQL", "PostgreSQL", "MongoDB", "Neo4j"],
        "JPA": ["JPA", "Hibernate", "EntityManager", "JpaRepository"],
        "MySQL": ["MySQL", "MySQLDialect", "mysqlconnector"],
        "PostgreSQL": ["PostgreSQL", "psycopg2", "PostgreSQLDialect"],
        "MongoDB": ["MongoDB", "MongoRepository", "MongoTemplate"],
        "Neo4j": ["Neo4j", "Neo4jRepository", "Neo4jTemplate"],
        "REST_API": ["RestController", "RequestMapping", "GetMapping"],
        "GraphQL": ["GraphQL", "GraphQLSchema", "QueryType"],
        "gRPC": ["gRPC", "GrpcService", "GrpcChannel"],
        "APIDocumentation": ["Swagger", "OpenAPI", "SpringDoc"],
        "Caching": ["Redis", "Memcached", "CacheManager", "Cacheable"],
        "Redis": ["Redis", "RedisTemplate", "Jedis", "Lettuce"],
        "Messaging": ["Kafka", "RabbitMQ", "MessageBroker"],
        "Kafka": ["Kafka", "KafkaTemplate", "KafkaListener"],
        "RabbitMQ": ["RabbitMQ", "AmqpTemplate", "RabbitListener"],
        "Microservices": ["Microservices", "ServiceDiscovery", "APIGateway"],
        "SpringBoot": ["SpringBoot", "SpringBootApplication", "SpringApplication"],
        "SpringMVC": ["SpringMVC", "RestController", "Controller", "RequestMapping"],
        "FastAPI": ["FastAPI", "APIRouter", "Depends"],
        "Docker": ["Docker", "Dockerfile", "docker-compose"],
        "Kubernetes": ["Kubernetes", "k8s", "Deployment", "Service"],
        "EventDriven": ["Kafka", "RabbitMQ", "EventPublisher", "EventListener"],
        "LayeredArchitecture": ["Controller", "Service", "Repository", "Entity"],
        "MVC": ["Controller", "View", "Model"],
    }

    # ─── Technology Mapping ─────────────────────────────────────────────────
    TECHNOLOGY_MAP: Dict[str, str] = {
        "Spring Boot": "BackendFramework",
        "Spring Security": "Authentication",
        "JPA": "Database",
        "MySQL": "Database",
        "PostgreSQL": "Database",
        "MongoDB": "Database",
        "Neo4j": "Database",
        "Redis": "Caching",
        "Kafka": "Messaging",
        "RabbitMQ": "Messaging",
        "React": "FrontendFramework",
        "Angular": "FrontendFramework",
        "Docker": "Containerization",
        "Kubernetes": "Orchestration",
        "JWT": "Authentication",
        "OAuth2": "Authentication",
        "FastAPI": "BackendFramework",
        "Django": "BackendFramework",
        "Flask": "BackendFramework",
    }

    # ─── Architecture Mapping ───────────────────────────────────────────────
    ARCHITECTURE_MAP: Dict[str, List[str]] = {
        "Microservices": ["ServiceDiscovery", "APIGateway", "LoadBalancer", "CircuitBreaker"],
        "Monolith": ["SingleDeployment", "SharedDatabase"],
        "MVC": ["Model", "View", "Controller"],
        "LayeredArchitecture": ["PresentationLayer", "BusinessLayer", "DataAccessLayer"],
        "EventDriven": ["EventBus", "EventStore", "CommandHandler", "QueryHandler"],
    }

    @classmethod
    def normalize(cls, raw_claim: str) -> List[str]:
        """
        Normalizes a raw claim string to a deduplicated list of canonical expected features.
        Works through Intent → Feature mapping.
        """
        raw_lower = raw_claim.lower()
        intents: Set[str] = set()

        # Map raw text to intents
        for synonym, intent in cls.INTENT_MAP.items():
            if synonym in raw_lower:
                intents.add(intent)

        # Map intents to expected features
        features: Set[str] = set()
        for intent in intents:
            features.add(intent)
            sub_features = cls.FEATURE_MAP.get(intent, [])
            features.update(sub_features)

        return sorted(list(features)) if features else ["General"]

    @classmethod
    def get_technology_category(cls, tech_name: str) -> str:
        return cls.TECHNOLOGY_MAP.get(tech_name, "Unknown")

    @classmethod
    def get_architecture_features(cls, arch_pattern: str) -> List[str]:
        return cls.ARCHITECTURE_MAP.get(arch_pattern, [])
