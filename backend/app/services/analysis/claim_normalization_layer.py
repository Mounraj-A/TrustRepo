"""
Claim Normalization Layer

Pipeline:
  Raw Text → Atomic Statements → Candidate Claims → Normalized Claims → Intent → Expected Features

This ensures that semantically equivalent claims like:
  "Supports JWT", "Uses JWT", "JWT Authentication", "Authentication via JWT"
all map to the same normalized form with identical intent + features.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Dict, Set
from app.models.claim import Claim


# ─────────────────────────────────────────────────────────────────────────────
# Intent taxonomy: maps keyword patterns → (intent_label, feature_tags)
# ─────────────────────────────────────────────────────────────────────────────
INTENT_TAXONOMY: List[Dict] = [
    # Authentication & Security
    {
        "patterns": ["jwt", "json web token"],
        "intent": "Authentication",
        "features": ["jwt", "authentication"],
        "technology": "JWT"
    },
    {
        "patterns": ["oauth", "oauth2"],
        "intent": "Authentication",
        "features": ["oauth2", "authentication"],
        "technology": "OAuth2"
    },
    {
        "patterns": ["spring security"],
        "intent": "Authentication",
        "features": ["spring_security", "authentication"],
        "technology": "Spring Security"
    },
    {
        "patterns": ["basic auth", "basic authentication", "http basic"],
        "intent": "Authentication",
        "features": ["basic_auth", "authentication"],
        "technology": "Basic Auth"
    },
    # Backend Frameworks
    {
        "patterns": ["spring boot", "springboot"],
        "intent": "BackendFramework",
        "features": ["spring_boot", "backend"],
        "technology": "Spring Boot"
    },
    {
        "patterns": ["fastapi", "fast api"],
        "intent": "BackendFramework",
        "features": ["fastapi", "backend"],
        "technology": "FastAPI"
    },
    {
        "patterns": ["django"],
        "intent": "BackendFramework",
        "features": ["django", "backend"],
        "technology": "Django"
    },
    {
        "patterns": ["flask"],
        "intent": "BackendFramework",
        "features": ["flask", "backend"],
        "technology": "Flask"
    },
    {
        "patterns": ["express", "expressjs"],
        "intent": "BackendFramework",
        "features": ["express", "backend"],
        "technology": "Express.js"
    },
    # Frontend Frameworks
    {
        "patterns": ["react", "reactjs"],
        "intent": "FrontendFramework",
        "features": ["react", "frontend"],
        "technology": "React"
    },
    {
        "patterns": ["angular", "angularjs"],
        "intent": "FrontendFramework",
        "features": ["angular", "frontend"],
        "technology": "Angular"
    },
    {
        "patterns": ["vue", "vuejs"],
        "intent": "FrontendFramework",
        "features": ["vue", "frontend"],
        "technology": "Vue.js"
    },
    # Databases
    {
        "patterns": ["postgresql", "postgres", "pg"],
        "intent": "Database",
        "features": ["postgresql", "database"],
        "technology": "PostgreSQL"
    },
    {
        "patterns": ["mysql"],
        "intent": "Database",
        "features": ["mysql", "database"],
        "technology": "MySQL"
    },
    {
        "patterns": ["mongodb", "mongo"],
        "intent": "Database",
        "features": ["mongodb", "database"],
        "technology": "MongoDB"
    },
    {
        "patterns": ["neo4j"],
        "intent": "Database",
        "features": ["neo4j", "graph_database"],
        "technology": "Neo4j"
    },
    {
        "patterns": ["redis"],
        "intent": "Caching",
        "features": ["redis", "caching"],
        "technology": "Redis"
    },
    # Infrastructure
    {
        "patterns": ["docker"],
        "intent": "Containerization",
        "features": ["docker", "containerization"],
        "technology": "Docker"
    },
    {
        "patterns": ["kubernetes", "k8s"],
        "intent": "Orchestration",
        "features": ["kubernetes", "orchestration"],
        "technology": "Kubernetes"
    },
    {
        "patterns": ["rabbitmq", "rabbit mq"],
        "intent": "Messaging",
        "features": ["rabbitmq", "messaging"],
        "technology": "RabbitMQ"
    },
    {
        "patterns": ["kafka"],
        "intent": "Messaging",
        "features": ["kafka", "messaging"],
        "technology": "Kafka"
    },
    # API
    {
        "patterns": ["rest api", "restful", "rest endpoint"],
        "intent": "API",
        "features": ["rest_api", "api"],
        "technology": "REST API"
    },
    {
        "patterns": ["graphql"],
        "intent": "API",
        "features": ["graphql", "api"],
        "technology": "GraphQL"
    },
    {
        "patterns": ["swagger", "openapi"],
        "intent": "APIDocumentation",
        "features": ["swagger", "api_documentation"],
        "technology": "Swagger/OpenAPI"
    },
    # Build Tools
    {
        "patterns": ["maven"],
        "intent": "BuildTool",
        "features": ["maven", "build"],
        "technology": "Maven"
    },
    {
        "patterns": ["gradle"],
        "intent": "BuildTool",
        "features": ["gradle", "build"],
        "technology": "Gradle"
    },
    {
        "patterns": ["npm", "node package manager"],
        "intent": "BuildTool",
        "features": ["npm", "build"],
        "technology": "npm"
    },
    # Architecture Patterns
    {
        "patterns": ["microservice", "micro service"],
        "intent": "ArchitecturePattern",
        "features": ["microservices", "architecture"],
        "technology": "Microservices"
    },
    {
        "patterns": ["layered architecture", "mvc", "model view controller"],
        "intent": "ArchitecturePattern",
        "features": ["layered_architecture", "architecture"],
        "technology": "MVC/Layered"
    },
    {
        "patterns": ["event driven", "event-driven"],
        "intent": "ArchitecturePattern",
        "features": ["event_driven", "architecture"],
        "technology": "Event-Driven"
    },
]


@dataclass
class NormalizedClaim:
    """
    A fully normalized, intent-tagged claim produced by the ClaimNormalizationLayer.

    Pipeline trace:
        raw_text → normalized_text → intent → expected_features
    """
    claim_id: str
    raw_text: str
    normalized_text: str
    intent: str                        # e.g. "Authentication", "Database"
    expected_features: List[str]       # e.g. ["jwt", "authentication"]
    matched_technologies: List[str]    # e.g. ["JWT"]
    canonical_form: str                # Deduplicated canonical representation
    confidence: float = 1.0
    metadata: Dict = field(default_factory=dict)


class ClaimNormalizationLayer:
    """
    Implements the full Claim Normalization pipeline:

        Atomic Statements
              ↓
        Candidate Claims
              ↓
        Normalized Claims
              ↓
        Intent Extraction
              ↓
        Expected Features

    Ensures semantically equivalent claims ("Uses JWT", "JWT Authentication",
    "Supports JWT") all resolve to the same intent and feature set.
    """

    def __init__(self):
        # Pre-compile all patterns for efficiency
        self._compiled_taxonomy = []
        for entry in INTENT_TAXONOMY:
            compiled_patterns = [
                re.compile(r'\b' + re.escape(p) + r'\b', re.IGNORECASE)
                for p in entry["patterns"]
            ]
            self._compiled_taxonomy.append({
                **entry,
                "compiled_patterns": compiled_patterns
            })

    def normalize(self, claims: List[Claim]) -> List[NormalizedClaim]:
        """
        Normalize a list of raw claims into structured NormalizedClaims.
        Deduplicates claims with the same canonical form and intent.
        """
        normalized: List[NormalizedClaim] = []
        seen_canonical: Set[str] = set()

        for claim in claims:
            nc = self._normalize_single(claim)
            if nc.canonical_form not in seen_canonical:
                seen_canonical.add(nc.canonical_form)
                normalized.append(nc)
            else:
                # Merge: if duplicate found, update confidence
                for existing in normalized:
                    if existing.canonical_form == nc.canonical_form:
                        existing.confidence = min(
                            1.0, existing.confidence + 0.1)
                        break

        return normalized

    def _normalize_single(self, claim: Claim) -> NormalizedClaim:
        """Normalize a single Claim → NormalizedClaim."""
        text = claim.text

        # Step 1: Text Normalization
        normalized_text = self._clean_text(text)

        # Step 2: Intent + Feature Extraction via taxonomy
        intent = "General"
        features: List[str] = []
        technologies: List[str] = []

        for entry in self._compiled_taxonomy:
            for pattern in entry["compiled_patterns"]:
                if pattern.search(normalized_text):
                    intent = entry["intent"]
                    features.extend(entry["features"])
                    technologies.append(entry["technology"])
                    break  # One match per taxonomy entry is enough

        # Deduplicate
        features = list(dict.fromkeys(features))
        technologies = list(dict.fromkeys(technologies))

        # Step 3: Build canonical form for deduplication
        canonical = self._build_canonical(intent, features)

        # Update the original claim metadata
        claim.normalized_text = normalized_text
        import hashlib
        # Use a stable hash of the canonical form as the ID
        claim.normalized_claim_id = "norm-" + hashlib.md5(canonical.encode()).hexdigest()[:8]
        # Metadata deprecated in Phase 3

        return NormalizedClaim(
            claim_id=claim.normalized_claim_id,
            raw_text=claim.text,
            normalized_text=normalized_text,
            intent=intent,
            expected_features=features,
            matched_technologies=technologies,
            canonical_form=canonical,
            confidence=1.0,
            metadata={"source_document": claim.source_document}
        )

    def _clean_text(self, text: str) -> str:
        """Minimal normalization — preserve meaning, just clean noise."""
        cleaned = text.lower()
        cleaned = re.sub(r'\*\*', '', cleaned)      # Remove markdown bold
        cleaned = re.sub(r'`', '', cleaned)         # Remove backticks
        cleaned = re.sub(r'#+\s*', '', cleaned)     # Remove markdown headings
        cleaned = re.sub(r'\s+', ' ', cleaned)      # Normalize whitespace
        return cleaned.strip()

    def _build_canonical(self, intent: str, features: List[str]) -> str:
        """
        Builds a canonical string that uniquely identifies the semantic content.
        "Uses JWT" and "JWT Authentication" → "Authentication::jwt::authentication"
        """
        sorted_features = sorted(features)
        return f"{intent}::{':'.join(sorted_features)}"
