from typing import List

from app.models.repository_context import RepositoryContext
from app.models.knowledge.feature_instance import FeatureInstance
from app.repositories.graph_repository import GraphRepository

# Import the detectors
from app.services.analysis.semantic.detectors.api_detector import ApiDetector
from app.services.analysis.semantic.detectors.security_detector import SecurityDetector
from app.services.analysis.semantic.detectors.database_detector import DatabaseDetector
from app.services.analysis.semantic.detectors.configuration_detector import ConfigurationDetector

# Import the engines
from app.services.analysis.semantic.feature_fusion_engine import FeatureFusionEngine
from app.services.analysis.semantic.feature_validation_layer import FeatureValidationLayer
from app.services.analysis.semantic.feature_confidence_engine import FeatureConfidenceEngine

class FeatureExtractor:
    """
    Orchestrates the semantic feature extraction process.
    1. Runs all independent feature detector plugins.
    2. Fuses duplicate features.
    3. Validates features to prevent false positives.
    4. Calculates final feature confidence.
    """
    
    def __init__(self, repo: GraphRepository = None):
        self.repo = repo or GraphRepository()
        
        # Load plugin detectors
        self.detectors = [
            ApiDetector(repo=self.repo),
            SecurityDetector(repo=self.repo),
            DatabaseDetector(repo=self.repo),
            ConfigurationDetector(repo=self.repo)
            # Add more detectors here as they are implemented
        ]
        
        self.fusion_engine = FeatureFusionEngine()
        self.validation_layer = FeatureValidationLayer()
        self.confidence_engine = FeatureConfidenceEngine()
        
    def extract(self, context: RepositoryContext) -> List[FeatureInstance]:
        raw_features: List[FeatureInstance] = []
        
        # 1. Run all independent plugins
        for detector in self.detectors:
            try:
                features = detector.detect(context)
                if features:
                    raw_features.extend(features)
            except Exception as e:
                print(f"  [FeatureExtractor] Detector {detector.__class__.__name__} failed: {e}")
                
        # 2. Fuse duplicate features
        fused_features = self.fusion_engine.fuse(raw_features)
        
        # 3. Validate features
        validated_features = self.validation_layer.validate(fused_features)
        
        # 4. Calculate confidence
        final_features = self.confidence_engine.calculate(validated_features)
        
        print(f"  Extracted {len(final_features)} validated features from {len(raw_features)} raw detections.")
        return final_features
