from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from app.models.knowledge.evidence import EvidenceChain

class FeatureInstance(BaseModel):
    """
    Represents a concrete instance of a feature found in a specific repository.
    Populated by feature detectors and merged by the Feature Fusion Engine.
    """
    id: str
    definition_id: str
    canonical_name: str
    technologies: List[str] = Field(default_factory=list)
    evidence: List[EvidenceChain] = Field(default_factory=list)
    confidence: float = 0.0  # Calculated by ConfidenceEngine, not detectors
