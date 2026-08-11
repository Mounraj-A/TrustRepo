import uuid
from typing import List
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceType, EvidenceStrength, EvidenceSource
from app.services.analysis.retrievers.base_retriever import BaseEvidenceRetriever
from app.models.knowledge.feature_instance import FeatureInstance


class ArchitectureRetriever(BaseEvidenceRetriever):
    """Retrieves structural evidence for architecture (e.g. MVC, Layered)."""

    def retrieve(self, feature: FeatureInstance) -> List[EvidenceChain]:
        evidence_chains = []

        if feature.definition_id in ("feat_mvc", "feat_layered"):
            chain = self._detect_layered_mvc()
            if chain:
                chain.chain_id = f"arch_{feature.definition_id}_{uuid.uuid4()}"
                chain.reasoning_trace = "Found structural evidence of layered architecture."
                evidence_chains.append(chain)

        return evidence_chains

    def _detect_layered_mvc(self) -> EvidenceChain:
        """
        Looks for structural relationships: Routes -> Services -> Database/Models
        or Controllers -> Services -> Repositories.
        """
        # A simple Cypher query to find calls from a 'route/controller' file to a 'service' file
        query = """
        MATCH (f1:File)-[:CONTAINS]->(n1)-[:CALLS]->(n2)<-[:CONTAINS]-(f2:File)
        WHERE (f1.file_path CONTAINS 'route' OR f1.file_path CONTAINS 'controller' OR f1.file_path CONTAINS 'view')
          AND (f2.file_path CONTAINS 'service' OR f2.file_path CONTAINS 'manager')
        RETURN f1.file_path as layer1, f2.file_path as layer2, n1.name as caller, n2.name as callee,
               n1.start_line as line1, n2.start_line as line2
        LIMIT 5
        """
        results = self.repo.conn.query(query, {})
        if not results:
            return None

        items = []
        for r in results:
            # Layer 1 Item
            items.append(EvidenceItem(
                source=EvidenceSource(file_path=r.get("layer1"), line_number=r.get("line1")),
                evidence_type=EvidenceType.STRUCTURAL,
                symbol=r.get("caller"),
                context_type="controller_layer",
                evidence_strength=EvidenceStrength.PRIMARY,
                extraction_method="GraphStructuralQuery",
                explanation=f"Controller/Route layer ({r.get('layer1')}) calls Service layer ({r.get('layer2')})."
            ))
            # Layer 2 Item
            items.append(EvidenceItem(
                source=EvidenceSource(file_path=r.get("layer2"), line_number=r.get("line2")),
                evidence_type=EvidenceType.STRUCTURAL,
                symbol=r.get("callee"),
                context_type="service_layer",
                evidence_strength=EvidenceStrength.PRIMARY,
                extraction_method="GraphStructuralQuery",
                explanation=f"Service layer ({r.get('layer2')}) receives call."
            ))

        if items:
            return EvidenceChain(
                chain_id="",
                chain_type="Structural Architecture",
                retrieval_strategy="Graph Pattern Match",
                sequence=items,
                graph_path="Route -> Service",
                confidence=0.9
            )
        return None
