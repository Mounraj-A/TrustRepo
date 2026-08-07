"""
FeatureExtractor — Semantic Discovery Engine

Orchestrates feature detection from the in-memory RepositoryKnowledgeGraph.
All detector plugins receive the graph directly — zero live Neo4j queries.

Pipeline
--------
RepositoryKnowledgeGraph
    ↓
[ApiDetector | SecurityDetector | DatabaseDetector | ConfigurationDetector]
    ↓ raw_features: List[FeatureInstance]
FeatureFusionEngine (deduplicate overlapping features)
    ↓ fused_features
FeatureValidationLayer (remove false positives)
    ↓ validated_features
FeatureConfidenceEngine (score remaining features)
    ↓ final_features: List[FeatureInstance]
"""
from typing import List

from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph
from app.models.knowledge.feature_instance import FeatureInstance

from app.services.analysis.semantic.feature_fusion_engine import FeatureFusionEngine
from app.services.analysis.semantic.feature_validation_layer import FeatureValidationLayer
from app.services.analysis.semantic.feature_confidence_engine import FeatureConfidenceEngine
from app.services.knowledge.technology_kb import TECHNOLOGY_KB, CAPABILITY_KB
from app.services.knowledge.semantic_registry import SEMANTIC_REGISTRY
import uuid


class FeatureExtractor:
    """
    Orchestrates semantic feature extraction from the Knowledge Graph.

    All detector plugins query the in-memory RepositoryKnowledgeGraph.
    No live Neo4j/Cypher queries are made.
    """

    def __init__(self):
        self.fusion_engine = FeatureFusionEngine()
        self.validation_layer = FeatureValidationLayer()
        self.confidence_engine = FeatureConfidenceEngine()

    def extract(self, graph: RepositoryKnowledgeGraph, tech_results: dict = None) -> List[FeatureInstance]:
        """
        Extract features from the Knowledge Graph based on detected technologies.
        
        Parameters
        ----------
        graph : RepositoryKnowledgeGraph
            Fully built in-memory graph produced by GraphBuilder.
        tech_results : dict
            The output from TechnologyDetection containing technologies and evidence.

        Returns
        -------
        List[FeatureInstance]
            Validated, scored feature instances with evidence chains.
        """
        raw_features: List[FeatureInstance] = []
        tech_results = tech_results or {}
        
        # 1. Derive features from detected technologies
        for tech_name in tech_results.get("technologies", []):
            # Find the tech in KB to get its category/capabilities, or map to features
            for tech_def in TECHNOLOGY_KB.values():
                if tech_def.display_name == tech_name:
                    # Resolve features that this technology implies via SEMANTIC_REGISTRY
                    # e.g., 'Spring MVC' -> 'MVC Architecture', 'REST API'
                    # Currently SEMANTIC_REGISTRY has features like 'feat_rest_api'
                    # We can use the capability -> feature mapping or string matching for now
                    
                    # Look up features in semantic registry that match this technology's capabilities
                    caps = [cap for cap in CAPABILITY_KB.values() if tech_def.category in cap.category_triggers]
                    cap_names = [c.display_name for c in caps]
                    
                    for feature_def in SEMANTIC_REGISTRY.get_all():
                        if any(c in feature_def.capabilities for c in cap_names) or feature_def.category == tech_def.category:
                            
                            # Find the evidence chain for this tech
                            tech_chains = [c for c in tech_results.get("evidence_chains", []) if tech_name in c.chain_type]
                            
                            raw_features.append(FeatureInstance(
                                id=f"inst_{uuid.uuid4().hex[:8]}",
                                definition_id=feature_def.id,
                                canonical_name=feature_def.canonical_name,
                                evidence=tech_chains,
                                technologies=[tech_name]
                            ))

        # 2. Fuse duplicate features
        fused_features = self.fusion_engine.fuse(raw_features)

        # 3. Validate (remove false positives)
        validated_features = self.validation_layer.validate(fused_features)

        # 4. Score confidence
        final_features = self.confidence_engine.calculate(validated_features)

        print(f"  Extracted {len(final_features)} validated features from {len(raw_features)} raw detections.")
        return final_features
