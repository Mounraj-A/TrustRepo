import uuid
from typing import List
from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph
from app.models.knowledge.evidence import EvidenceItem, EvidenceSource, EvidenceStrength, EvidenceType
from app.services.analysis.providers.evidence_provider import EvidenceProvider

class AnnotationProvider(EvidenceProvider):
    """
    Extracts class, method, or field level annotations and decorators.
    """

    def extract_evidence(self, graph: RepositoryKnowledgeGraph) -> List[EvidenceItem]:
        items = []
        for node in graph.nodes:
            if node.label == "Annotation":
                name = node.properties.get("name", "")
                if not name:
                    name = node.properties.get("qualname", "")
                if not name:
                    continue
                
                source = EvidenceSource(
                    file_path=node.properties.get("file_path", "unknown"),
                    parser_used="AnnotationProvider",
                    language=self._detect_language(node.properties.get("file_path", "unknown")),
                    line_number=node.properties.get("start_line", None),
                    commit_sha=graph.metadata.get("commit_sha", "HEAD"),
                    branch=graph.metadata.get("branch", "main")
                )
                
                item = EvidenceItem(
                    id=str(uuid.uuid4()),
                    source=source,
                    node_type="Annotation",
                    symbol_kind="Decorator",
                    symbol=name,
                    qualified_name=name,
                    context_type="decorator_usage",
                    evidence_type=EvidenceType.ANNOTATION,
                    code_snippet=f"@{name}",
                    graph_node_id=str(id(node)),
                    evidence_strength=EvidenceStrength.PRIMARY
                )
                items.append(item)
        return items

    def _detect_language(self, path: str) -> str:
        path = path.lower()
        if path.endswith(".py"): return "Python"
        if path.endswith(".ts") or path.endswith(".tsx"): return "TypeScript"
        if path.endswith(".java"): return "Java"
        return "Unknown"
