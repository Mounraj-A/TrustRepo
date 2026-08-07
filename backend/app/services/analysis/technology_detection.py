"""
Evidence-Based Technology Detection

Detects technology stack from actual code evidence in Neo4j by extracting
full graph paths (EvidenceChains).

Examples:
    org.springframework.boot → Spring Boot
    import jwt → JWT
    @RestController → Spring MVC
"""
import uuid
from typing import Dict, List, Tuple
from app.models.repository_context import RepositoryContext
from app.repositories.graph_repository import GraphRepository
from app.models.knowledge.evidence import (
    EvidenceChain, EvidenceItem, EvidenceSource, EvidenceStrength
)

from app.services.knowledge.technology_kb import resolve_technology, get_capabilities_for_tech, TECHNOLOGY_KB, CAPABILITY_KB

ANNOTATION_TECHNOLOGY_MAP = {
    "RestController": "spring_web",
    "Controller": "spring_web",
    "Service": "spring_context",
    "Repository": "spring_data_jpa",
    "Entity": "hibernate",
    "SpringBootApplication": "spring_boot",
    "EnableWebSecurity": "spring_security",
    "EnableJwtTokenStore": "jwt_java",
    "CrossOrigin": "spring_web",
    "RequestMapping": "spring_web",
    "GetMapping": "spring_web",
    "PostMapping": "spring_web",
    "PutMapping": "spring_web",
    "DeleteMapping": "spring_web",
}

from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph

class TechnologyDetection:
    """
    Detects technology stack by querying the RepositoryKnowledgeGraph directly.
    Constructs full EvidenceChains for each detected technology.
    """

    def __init__(self, repo: GraphRepository = None):
        # We keep the repo parameter for backward compatibility if needed, 
        # but the primary source of truth is now the in-memory graph.
        self.repo = repo or GraphRepository()

    def _detect_language_from_path(self, path: str) -> str:
        path = path.lower()
        if path.endswith(".py"): return "Python"
        if path.endswith(".js") or path.endswith(".jsx"): return "JavaScript"
        if path.endswith(".ts") or path.endswith(".tsx"): return "TypeScript"
        if path.endswith(".java"): return "Java"
        if "package.json" in path: return "JavaScript"
        if "requirements.txt" in path or path.endswith(".toml"): return "Python"
        return "Unknown"

    def detect(self, graph: RepositoryKnowledgeGraph) -> dict:
        detected_techs = {}
        evidence_chains = []
        capabilities_found = set()

        import_records = self._query_import_evidence(graph)
        for r in import_records:
            name = r.get("import_name", "")
            file_path = r.get("file_path", "")
            file_lang = self._detect_language_from_path(file_path)
            
            matched_technologies = resolve_technology(name, [file_lang] if file_lang != "Unknown" else [])
            for tech in matched_technologies:
                detected_techs[tech.display_name] = tech.category
                chain = self._build_evidence_chain(tech.display_name, "Import", r)
                evidence_chains.append(chain)
                
                for cap in get_capabilities_for_tech(tech):
                    capabilities_found.add(cap.display_name)

        annotation_records = self._query_annotation_evidence(graph)
        for r in annotation_records:
            name = r.get("annotation_name", "")
            for pattern, tech_id in ANNOTATION_TECHNOLOGY_MAP.items():
                if pattern.lower() == name.lower():
                    tech = TECHNOLOGY_KB.get(tech_id)
                    if tech:
                        detected_techs[tech.display_name] = tech.category
                        chain = self._build_evidence_chain(tech.display_name, "Annotation", r)
                        evidence_chains.append(chain)
                        
                        for cap in get_capabilities_for_tech(tech):
                            capabilities_found.add(cap.display_name)
                    break

        dependency_records = self._query_dependency_evidence(graph)
        for r in dependency_records:
            name = r.get("dependency_name", "")
            file_path = r.get("file_path", "")
            file_lang = self._detect_language_from_path(file_path)
            
            matched_technologies = resolve_technology(name, [file_lang] if file_lang != "Unknown" else [])
            for tech in matched_technologies:
                detected_techs[tech.display_name] = tech.category
                chain = self._build_evidence_chain(tech.display_name, "Dependency", r)
                evidence_chains.append(chain)
                
                for cap in get_capabilities_for_tech(tech):
                    capabilities_found.add(cap.display_name)

        tech_list = sorted(detected_techs.keys())
        tech_categories = {tech: cat for tech, cat in detected_techs.items()}
        cap_list = sorted(capabilities_found)

        print(f"  Technologies detected ({len(tech_list)}): {tech_list}")
        
        return {
            "technologies": tech_list,
            "technology_categories": tech_categories,
            "capabilities": cap_list,
            "evidence_chains": evidence_chains
        }

    def _query_import_evidence(self, graph: RepositoryKnowledgeGraph) -> list:
        records = []
        for i, node in enumerate(graph.nodes):
            if node.label == "Import":
                name = node.properties.get("name", "")
                if not name:
                    name = node.properties.get("qualname", "")
                records.append({
                    "import_name": name,
                    "file_path": node.properties.get("file_path", ""),
                    "node_id": id(node)
                })
        return records

    def _query_annotation_evidence(self, graph: RepositoryKnowledgeGraph) -> list:
        records = []
        # Find Annotation nodes that are connected via edges.
        # But for simpler traversal without checking edges (since annotations belong to classes inherently in properties):
        for node in graph.nodes:
            if node.label == "Annotation":
                name = node.properties.get("name", "")
                if not name:
                    name = node.properties.get("qualname", "")
                records.append({
                    "annotation_name": name,
                    "file_path": node.properties.get("file_path", ""),
                    "class_name": "Class", # Extracted from edge or parent in Neo4j, but placeholder works for Evidence
                    "node_id": id(node)
                })
        return records
            
    def _query_dependency_evidence(self, graph: RepositoryKnowledgeGraph) -> list:
        records = []
        for node in graph.nodes:
            if node.label == "Dependency":
                name = node.properties.get("name", "")
                records.append({
                    "dependency_name": name,
                    "file_path": node.properties.get("file_path", ""),
                    "node_id": id(node)
                })
        return records
            
    def _build_evidence_chain(self, tech: str, kind: str, record: dict) -> EvidenceChain:
        source = EvidenceSource(
            file_path=record.get("file_path", "Unknown"),
            parser_used="KnowledgeGraph"
        )
        
        snippet = ""
        symbol_name = ""
        if kind == "Import":
            snippet = f"import {record.get('import_name')}"
            symbol_name = record.get("import_name")
        elif kind == "Dependency":
            snippet = f"Dependency configuration: {record.get('dependency_name')}"
            symbol_name = record.get("dependency_name")
        else:
            snippet = f"@{record.get('annotation_name')}"
            symbol_name = record.get("class_name", "Unknown Class")
            
        item = EvidenceItem(
            source=source,
            node_type=kind,
            symbol_kind="Class" if kind == "Annotation" else "Import",
            symbol=symbol_name,
            qualified_name=symbol_name,
            context_type=kind.lower(),
            code_snippet=snippet,
            graph_node_id=str(record.get("node_id", "")),
            evidence_strength=EvidenceStrength.PRIMARY
        )
        
        return EvidenceChain(
            chain_id=str(uuid.uuid4()),
            chain_type=f"{kind} Match for {tech}",
            retrieval_strategy="Graph Traversal",
            sequence=[item],
            graph_path=f"File -> {kind}",
            ranking_score=1.0 if kind == "Annotation" else 0.8,
            confidence=0.9,
            reasoning_trace=f"AST parser identified {snippet} in {source.file_path}. Knowledge Graph links this to {tech}."
        )
