from typing import List

from app.models.knowledge.feature_instance import FeatureInstance
from app.services.knowledge.semantic_registry import SEMANTIC_REGISTRY


class CapabilityDetector:
    """
    Maps validated FeatureInstances to high-level Capabilities
    using the SemanticRegistry ontology.
    """

    def detect(self, features: List[FeatureInstance]) -> List[str]:
        capabilities = set()

        for feat in features:
            definition = SEMANTIC_REGISTRY.get_by_id(feat.definition_id)
            if definition:
                for cap in definition.capabilities:
                    capabilities.add(cap)

        cap_list = sorted(list(capabilities))
        print(f"  Capabilities extracted from features: {cap_list}")
        return cap_list
