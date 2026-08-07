import uuid
from typing import List
from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph
from app.models.knowledge.evidence import EvidenceItem, EvidenceSource, EvidenceStrength, EvidenceType
from app.services.analysis.providers.evidence_provider import EvidenceProvider

class DependencyProvider(EvidenceProvider):
    """
    Extracts package dependencies (e.g. from package.json, requirements.txt, pom.xml).
    """

    def extract_evidence(self, graph: RepositoryKnowledgeGraph) -> List[EvidenceItem]:
        items = []
        for node in graph.nodes:
            if node.label == "Dependency":
                name = node.properties.get("name", "")
                if not name:
                    continue
                
                source = EvidenceSource(
                    file_path=node.properties.get("file_path", "unknown"),
                    parser_used="DependencyParser",
                    language=self._detect_language(node.properties.get("file_path", "unknown")),
                    commit_sha=graph.metadata.get("commit_sha", "HEAD"),
                    branch=graph.metadata.get("branch", "main")
                )
                
                item = EvidenceItem(
                    id=str(uuid.uuid4()),
                    source=source,
                    node_type="Dependency",
                    symbol_kind="Package",
                    symbol=name,
                    qualified_name=name,
                    context_type="dependency_declaration",
                    evidence_type=EvidenceType.DEPENDENCY,
                    code_snippet=f"Dependency on {name}",
                    graph_node_id=str(id(node)),
                    evidence_strength=EvidenceStrength.PRIMARY
                )
                items.append(item)
        return items

    def _detect_language(self, path: str) -> str:
        path = path.lower()
        if "package.json" in path: return "JavaScript"
        if "requirements.txt" in path or path.endswith(".toml"): return "Python"
        if "pom.xml" in path or "build.gradle" in path: return "Java"
        return "Unknown"
