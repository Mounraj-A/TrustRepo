from typing import List
from pydantic import BaseModel
from app.services.knowledge.semantic_registry import SEMANTIC_REGISTRY


class ResolvedIntent(BaseModel):
    intent: str
    expected_features: List[str]      # Semantic Registry IDs (e.g. feat_jwt)
    expected_capabilities: List[str]  # Derived capabilities
    expected_architecture: str        # Derived architecture


class IntentResolver:
    """
    Maps natural language claims to semantic ontology constraints.
    Claim -> Intent -> Expected Features -> Capabilities -> Architecture
    """

    def resolve(self, claim_text: str) -> ResolvedIntent:
        """
        Parses a raw claim string into a strictly structured semantic intent.
        For Phase 3, this uses basic heuristic mapping (which could be replaced by an LLM).
        """
        claim_lower = claim_text.lower()

        expected_features = set()
        intent = "General Claim"

        # 1. Map to Features via Semantic Registry Aliases
        for feature_def in SEMANTIC_REGISTRY.get_all():
            # Check canonical name
            if feature_def.canonical_name.lower() in claim_lower:
                expected_features.add(feature_def.id)
                continue

            # Check aliases
            for alias in feature_def.aliases:
                if alias.lower() in claim_lower:
                    expected_features.add(feature_def.id)
                    break

        # 2. Derive Intent based on category
        categories = set()
        for f_id in expected_features:
            feat = SEMANTIC_REGISTRY.get_by_id(f_id)
            if feat:
                categories.add(feat.category)

        if "Security" in categories:
            intent = "Authentication/Authorization"
        elif "Database" in categories:
            intent = "Data Persistence"
        elif "API" in categories:
            intent = "Web Interface"

        # 3. Derive Capabilities
        expected_capabilities = set()
        for f_id in expected_features:
            feat = SEMANTIC_REGISTRY.get_by_id(f_id)
            if feat:
                for cap in feat.capabilities:
                    expected_capabilities.add(cap)

        # 4. Derive Architecture
        architecture = "Unknown"
        if "REST API" in expected_capabilities:
            architecture = "Layered MVC"
        elif "Microservice" in expected_capabilities:
            architecture = "Microservices"

        return ResolvedIntent(
            intent=intent,
            expected_features=list(expected_features),
            expected_capabilities=list(expected_capabilities),
            expected_architecture=architecture
        )
