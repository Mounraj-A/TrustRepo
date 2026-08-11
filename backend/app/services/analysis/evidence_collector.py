from app.models.claim import Claim
from app.models.knowledge.evidence import EvidenceContext
from app.services.knowledge.graph_retrieval import GraphRetrievalEngine
from app.services.knowledge.semantic_retrieval import SemanticRetrievalEngine
from app.services.knowledge.code_retrieval import CodeRetrievalEngine
from app.services.knowledge.documentation_retrieval import DocumentationRetrievalEngine
from app.services.analysis.evidence_fusion import EvidenceFusion


class EvidenceCollector:
    """Orchestrates retrieval from all engines without any LLM logic."""

    def __init__(self):
        self.graph = GraphRetrievalEngine()
        self.semantic = SemanticRetrievalEngine()
        self.code = CodeRetrievalEngine()
        self.docs = DocumentationRetrievalEngine()
        self.fusion = EvidenceFusion()

    def collect(self, claim: Claim) -> EvidenceContext:
        candidates = []
        candidates.extend(self.graph.retrieve(claim))
        candidates.extend(self.semantic.retrieve(claim))
        candidates.extend(self.code.retrieve(claim))
        candidates.extend(self.docs.retrieve(claim))

        fused = self.fusion.fuse(candidates)
        return EvidenceContext(claim=claim, candidates=fused)
