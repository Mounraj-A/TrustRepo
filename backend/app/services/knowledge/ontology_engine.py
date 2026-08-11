from app.models.knowledge.technology_registry import TechnologyRegistry
from app.models.knowledge.feature_registry import FeatureRegistry
from app.models.knowledge.capability_registry import CapabilityRegistry
from app.models.knowledge.architecture_registry import ArchitectureRegistry
from app.models.knowledge.evidence_registry import EvidenceRegistry
from app.models.knowledge.relationship_registry import RelationshipRegistry
from app.models.knowledge.parser_registry import ParserRegistry


class OntologyEngine:
    """
    The semantic backbone of the system. Unifies all registries and manages
    the ontology of Technologies, Features, Capabilities, Architectures,
    Evidences, and Relationships.
    """

    def __init__(self):
        self.technologies = TechnologyRegistry()
        self.features = FeatureRegistry()
        self.capabilities = CapabilityRegistry()
        self.architectures = ArchitectureRegistry()
        self.evidences = EvidenceRegistry()
        self.relationships = RelationshipRegistry()
        self.parsers = ParserRegistry()

    def get_all_concepts(self):
        """Returns all recognized semantic concepts."""
        return {
            "technologies": self.technologies.get_all_technologies() if hasattr(self.technologies, 'get_all_technologies') else [],
            "features": self.features.get_all_features() if hasattr(self.features, 'get_all_features') else [],
            "capabilities": self.capabilities.get_all_capabilities() if hasattr(self.capabilities, 'get_all_capabilities') else [],
            "architectures": self.architectures.all_patterns(),
            "evidences": self.evidences.all_types(),
            "relationships": self.relationships.all_types(),
            # Placeholder
            "parser_reliabilities": [p.name for p in self.parsers.get_reliability.__annotations__]
        }
