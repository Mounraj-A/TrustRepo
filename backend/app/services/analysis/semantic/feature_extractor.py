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

# Plugin detectors (all now accept RepositoryKnowledgeGraph)
from app.services.analysis.semantic.detectors.api_detector import ApiDetector
from app.services.analysis.semantic.detectors.security_detector import SecurityDetector
from app.services.analysis.semantic.detectors.database_detector import DatabaseDetector
from app.services.analysis.semantic.detectors.configuration_detector import ConfigurationDetector

# Engine pipeline
from app.services.analysis.semantic.feature_fusion_engine import FeatureFusionEngine
from app.services.analysis.semantic.feature_validation_layer import FeatureValidationLayer
from app.services.analysis.semantic.feature_confidence_engine import FeatureConfidenceEngine


class FeatureExtractor:
    """
    Orchestrates semantic feature extraction from the Knowledge Graph.

    All detector plugins query the in-memory RepositoryKnowledgeGraph.
    No live Neo4j/Cypher queries are made.
    """

    def __init__(self):
        self.detectors = [
            ApiDetector(),
            SecurityDetector(),
            DatabaseDetector(),
            ConfigurationDetector(),
        ]
        self.fusion_engine = FeatureFusionEngine()
        self.validation_layer = FeatureValidationLayer()
        self.confidence_engine = FeatureConfidenceEngine()

    def extract(self, graph: RepositoryKnowledgeGraph) -> List[FeatureInstance]:
        """
        Extract features from the Knowledge Graph.

        Parameters
        ----------
        graph : RepositoryKnowledgeGraph
            Fully built in-memory graph produced by GraphBuilder.

        Returns
        -------
        List[FeatureInstance]
            Validated, scored feature instances with evidence chains.
        """
        raw_features: List[FeatureInstance] = []

        # 1. Run all detector plugins
        for detector in self.detectors:
            try:
                features = detector.detect(graph)
                if features:
                    raw_features.extend(features)
            except Exception as e:
                print(f"  [FeatureExtractor] {detector.__class__.__name__} failed: {e}")

        # 2. Fuse duplicate features
        fused_features = self.fusion_engine.fuse(raw_features)

        # 3. Validate (remove false positives)
        validated_features = self.validation_layer.validate(fused_features)

        # 4. Score confidence
        final_features = self.confidence_engine.calculate(validated_features)

        print(f"  Extracted {len(final_features)} validated features from {len(raw_features)} raw detections.")
        return final_features
