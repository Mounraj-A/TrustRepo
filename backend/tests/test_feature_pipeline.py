import pytest
from app.models.repository_context import RepositoryContext
from app.models.knowledge.feature_instance import FeatureInstance
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceStrength, EvidenceSource
from app.services.analysis.semantic.feature_fusion_engine import FeatureFusionEngine
from app.services.analysis.semantic.feature_validation_layer import FeatureValidationLayer
from app.services.analysis.semantic.feature_confidence_engine import FeatureConfidenceEngine

def test_feature_fusion():
    engine = FeatureFusionEngine()
    
    f1 = FeatureInstance(id="1", definition_id="feat_rest_api", canonical_name="REST API", technologies=["Spring Boot"], evidence=[])
    f2 = FeatureInstance(id="2", definition_id="feat_rest_api", canonical_name="REST API", technologies=["FastAPI"], evidence=[])
    
    fused = engine.fuse([f1, f2])
    
    assert len(fused) == 1
    assert "Spring Boot" in fused[0].technologies
    assert "FastAPI" in fused[0].technologies

def test_feature_validation():
    layer = FeatureValidationLayer()
    
    # 1. Feature with no evidence (should fail)
    f1 = FeatureInstance(id="1", definition_id="test", canonical_name="Test", evidence=[])
    
    # 2. Feature with 1 PRIMARY evidence (should pass)
    chain1 = EvidenceChain(chain_id="c1", sequence=[
        EvidenceItem(source=EvidenceSource(file_path="a.py"), evidence_strength=EvidenceStrength.PRIMARY)
    ])
    f2 = FeatureInstance(id="2", definition_id="test", canonical_name="Test", evidence=[chain1])
    
    # 3. Feature with 1 SECONDARY evidence (should fail)
    chain2 = EvidenceChain(chain_id="c2", sequence=[
        EvidenceItem(source=EvidenceSource(file_path="a.py"), evidence_strength=EvidenceStrength.SECONDARY)
    ])
    f3 = FeatureInstance(id="3", definition_id="test", canonical_name="Test", evidence=[chain2])
    
    validated = layer.validate([f1, f2, f3])
    
    assert len(validated) == 1
    assert validated[0].id == "2"

def test_feature_confidence():
    engine = FeatureConfidenceEngine()
    
    # Feature with 2 PRIMARY pieces
    chain1 = EvidenceChain(chain_id="c1", sequence=[
        EvidenceItem(source=EvidenceSource(file_path="a.py"), context_type="API", evidence_strength=EvidenceStrength.PRIMARY),
        EvidenceItem(source=EvidenceSource(file_path="b.py"), context_type="Config", evidence_strength=EvidenceStrength.PRIMARY)
    ])
    f1 = FeatureInstance(id="1", definition_id="test", canonical_name="Test", evidence=[chain1])
    
    conf_features = engine.calculate([f1])
    # 0.85 base + (2 types * 0.05) + (2 volume * 0.02) = 0.85 + 0.10 + 0.04 = 0.99
    assert conf_features[0].confidence >= 0.90
