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
from collections import defaultdict
from app.models.repository_context import RepositoryContext
from app.repositories.graph_repository import GraphRepository
from app.models.knowledge.evidence import (
    EvidenceChain, EvidenceItem, EvidenceSource, EvidenceStrength, EvidenceType
)
from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph
from app.services.knowledge.technology_kb import resolve_technology, get_capabilities_for_tech, TECHNOLOGY_KB, CAPABILITY_KB

from app.services.analysis.providers.dependency_provider import DependencyProvider
from app.services.analysis.providers.import_provider import ImportProvider
from app.services.analysis.providers.annotation_provider import AnnotationProvider
from app.services.analysis.confidence_engine import ConfidenceEngine

class TechnologyDetection:
    """
    Detects technology stack by querying the RepositoryKnowledgeGraph via EvidenceProviders.
    Aggregates evidence per technology and constructs full EvidenceChains.
    """

    def __init__(self, repo: GraphRepository = None):
        self.repo = repo or GraphRepository()
        self.providers = [
            DependencyProvider(),
            ImportProvider(),
            AnnotationProvider()
        ]
        self.confidence_engine = ConfidenceEngine()

    def detect(self, graph: RepositoryKnowledgeGraph) -> dict:
        tech_evidence_map = defaultdict(list)
        capabilities_found = set()
        
        # 1. Collect evidence from all providers
        for provider in self.providers:
            items = provider.extract_evidence(graph)
            for item in items:
                file_lang = item.source.language if item.source.language != "unknown" else "Unknown"
                matched_technologies = resolve_technology(item.symbol, [file_lang] if file_lang != "Unknown" else [])
                
                # For annotations, we also need to check the hardcoded map for now if it's not in the KB's aliases directly
                # To maintain compatibility, we can add a fallback here, but ideally they are in TECHNOLOGY_KB aliases
                
                for tech in matched_technologies:
                    tech_evidence_map[tech.id].append(item)
                    for cap in get_capabilities_for_tech(tech):
                        capabilities_found.add(cap.display_name)
        
        detected_techs = {}
        evidence_chains = []
        
        # 2. Aggregate evidence per technology
        for tech_id, items in tech_evidence_map.items():
            tech = TECHNOLOGY_KB[tech_id]
            detected_techs[tech.display_name] = tech.category
            
            # Ranking / Confidence calculation
            confidence = self._calculate_confidence(items)
            
            chain = EvidenceChain(
                chain_id=str(uuid.uuid4()),
                chain_type=f"Technology Match for {tech.display_name}",
                retrieval_strategy="Provider Aggregation",
                sequence=items,
                graph_path=" -> ".join([item.evidence_type.value for item in items[:3]]),
                ranking_score=confidence,
                confidence=confidence,
                reasoning_trace=f"Found {len(items)} pieces of evidence supporting {tech.display_name}."
            )
            evidence_chains.append(chain)

        tech_list = sorted(detected_techs.keys())
        tech_categories = defaultdict(list)
        for tech, cat in detected_techs.items():
            tech_categories[cat].append(tech)
        tech_categories = dict(tech_categories)
        cap_list = sorted(capabilities_found)

        print(f"  Technologies detected ({len(tech_list)}): {tech_list}")
        
        return {
            "technologies": tech_list,
            "technology_categories": tech_categories,
            "capabilities": cap_list,
            "evidence_chains": evidence_chains
        }
        
    def _calculate_confidence(self, items: List[EvidenceItem]) -> float:
        """
        Calculate confidence based on multi-evidence types.
        """
        return self.confidence_engine.calculate_chain_confidence(items)
