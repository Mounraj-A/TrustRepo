import uuid
import os
from typing import List

from app.models.repository_context import RepositoryContext
from app.models.knowledge.feature_instance import FeatureInstance
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceSource, EvidenceStrength
from app.services.analysis.semantic.detectors.base_feature_detector import BaseFeatureDetector
from app.services.knowledge.semantic_registry import SEMANTIC_REGISTRY

class ConfigurationDetector(BaseFeatureDetector):
    def detect(self, context: RepositoryContext) -> List[FeatureInstance]:
        features = []
        
        all_files = context.configuration_files + context.source_code_files
        
        # Look for Docker / Containerization
        docker_evidence = self._find_docker_evidence(all_files)
        if docker_evidence:
            # Note: We need a 'feat_docker' in the registry, we'll assume it exists or use a generic one
            # For now, let's say "feat_docker" is registered.
            feat_def = SEMANTIC_REGISTRY.get_by_id("feat_docker")
            if feat_def:
                features.append(FeatureInstance(
                    id=f"inst_{uuid.uuid4().hex[:8]}",
                    definition_id=feat_def.id,
                    canonical_name=feat_def.canonical_name,
                    evidence=[docker_evidence]
                ))

        return features

    def _find_docker_evidence(self, files: List[str]) -> EvidenceChain:
        docker_files = [f for f in files if "Dockerfile" in f or "docker-compose" in f.lower()]
        if not docker_files:
            return None
            
        items = []
        for df in docker_files[:3]:
            items.append(EvidenceItem(
                source=EvidenceSource(file_path=df),
                node_type="File",
                symbol=os.path.basename(df),
                context_type="Configuration",
                evidence_strength=EvidenceStrength.PRIMARY
            ))
            
        return EvidenceChain(
            chain_id=f"chain_{uuid.uuid4().hex[:8]}",
            chain_type="Docker Configuration",
            sequence=items,
            reasoning_trace="Found Docker configuration files."
        )
