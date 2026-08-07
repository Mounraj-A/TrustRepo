from typing import List, Dict

from app.models.knowledge.feature_instance import FeatureInstance

class FeatureFusionEngine:
    """
    Merges duplicate FeatureInstances emitted by different detectors.
    If ApiDetector and ConfigurationDetector both detect "REST API",
    this engine merges them into a single FeatureInstance with aggregated evidence.
    """
    
    def fuse(self, raw_features: List[FeatureInstance]) -> List[FeatureInstance]:
        fusion_map: Dict[str, FeatureInstance] = {}
        
        for feat in raw_features:
            if feat.definition_id in fusion_map:
                existing = fusion_map[feat.definition_id]
                # Merge evidence
                existing.evidence.extend(feat.evidence)
                # Merge technologies (deduplicate)
                existing.technologies = list(set(existing.technologies + feat.technologies))
            else:
                # Store a copy to avoid mutating the original detector output if reused
                fusion_map[feat.definition_id] = feat.model_copy(deep=True)
                
        return list(fusion_map.values())
