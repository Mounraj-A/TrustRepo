import uuid
from typing import List

from app.models.repository_context import RepositoryContext
from app.models.knowledge.feature_instance import FeatureInstance
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceSource, EvidenceStrength
from app.services.analysis.semantic.detectors.base_feature_detector import BaseFeatureDetector
from app.services.knowledge.semantic_registry import SEMANTIC_REGISTRY

class DatabaseDetector(BaseFeatureDetector):
    def detect(self, context: RepositoryContext) -> List[FeatureInstance]:
        features = []
        
        # Look for ORM evidence
        orm_evidence = self._find_orm_evidence()
        if orm_evidence:
            feat_def = SEMANTIC_REGISTRY.get_by_id("feat_orm")
            if feat_def:
                features.append(FeatureInstance(
                    id=f"inst_{uuid.uuid4().hex[:8]}",
                    definition_id=feat_def.id,
                    canonical_name=feat_def.canonical_name,
                    evidence=[orm_evidence]
                ))

        return features

    def _find_orm_evidence(self) -> EvidenceChain:
        query = """
        MATCH (a:Annotation)
        WHERE a.name IN ['Entity', 'Table', 'Column', 'Id', 'GeneratedValue']
        RETURN a.name as name, a.file_path as file_path, id(a) as node_id
        LIMIT 5
        """
        try:
            results = self.repo.conn.query(query, {})
            if results:
                items = []
                for r in results:
                    items.append(EvidenceItem(
                        source=EvidenceSource(file_path=r.get("file_path", "unknown")),
                        node_type="Annotation",
                        symbol=r.get("name"),
                        context_type="Data Access",
                        graph_node_id=str(r.get("node_id")),
                        evidence_strength=EvidenceStrength.PRIMARY
                    ))
                return EvidenceChain(
                    chain_id=f"chain_{uuid.uuid4().hex[:8]}",
                    chain_type="ORM Annotations",
                    sequence=items,
                    reasoning_trace="Found explicit ORM mapping annotations."
                )
        except Exception:
            pass
            
        return None
