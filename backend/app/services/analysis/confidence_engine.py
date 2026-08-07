from typing import List
from datetime import datetime, timezone
from app.models.knowledge.evidence import EvidenceItem, EvidenceType, EvidenceStrength

class ConfidenceEngine:
    """
    Centralized Confidence & Ranking Engine.
    Implements the Evidence Ranking Formula:
    Score = SourceWeight × GraphWeight × Agreement × Freshness × ParserConfidence
    """

    def calculate_chain_confidence(self, items: List[EvidenceItem]) -> float:
        if not items:
            return 0.0

        # Calculate individual item scores
        item_scores = [self.calculate_item_confidence(item) for item in items]
        
        # Base score is the maximum of individual evidence items
        base_score = max(item_scores)
        
        # Agreement multiplier based on number of supporting evidence pieces
        agreement_multiplier = min(1.0 + (len(items) - 1) * 0.05, 1.2)
        
        final_score = base_score * agreement_multiplier
        return min(1.0, final_score)

    def calculate_item_confidence(self, item: EvidenceItem) -> float:
        # 1. Source Weight
        source_weight = self._get_source_weight(item.evidence_type)
        
        # 2. Graph Weight (Strength of evidence)
        graph_weight = self._get_graph_weight(item.evidence_strength)
        
        # 3. Freshness (decay based on analysis timestamp)
        freshness = self._calculate_freshness(item.source.analysis_timestamp)
        
        # 4. Parser Confidence
        parser_confidence = self._get_parser_confidence(item.source.parser_used)
        
        # Score = SourceWeight * GraphWeight * Freshness * ParserConfidence
        # Since this is a single item, Agreement = 1.0
        return source_weight * graph_weight * freshness * parser_confidence

    def _get_source_weight(self, evidence_type: EvidenceType) -> float:
        weights = {
            EvidenceType.DEPENDENCY: 1.0,
            EvidenceType.IMPORT: 0.95,
            EvidenceType.ANNOTATION: 0.90,
            EvidenceType.CONFIGURATION: 0.85,
            EvidenceType.CALL: 0.80,
            EvidenceType.DECLARATION: 0.75,
            EvidenceType.INSTANTIATION: 0.75,
            EvidenceType.UNKNOWN: 0.50
        }
        return weights.get(evidence_type, 0.5)

    def _get_graph_weight(self, strength: EvidenceStrength) -> float:
        weights = {
            EvidenceStrength.PRIMARY: 1.0,
            EvidenceStrength.SECONDARY: 0.8,
            EvidenceStrength.SUPPORTING: 0.5
        }
        return weights.get(strength, 0.5)

    def _calculate_freshness(self, analysis_timestamp: datetime) -> float:
        # For our runtime analysis, it is always fresh (1.0).
        # In a distributed system with stale caches, this could decay.
        if not analysis_timestamp:
            return 1.0
        try:
            now = datetime.now(timezone.utc)
            delta = now - analysis_timestamp
            hours = delta.total_seconds() / 3600
            
            if hours <= 24:
                return 1.0
            elif hours <= 168: # 1 week
                return 0.95
            elif hours <= 720: # 1 month
                return 0.90
            return 0.80
        except TypeError:
            return 1.0 # timezone naive vs aware

    def _get_parser_confidence(self, parser_name: str) -> float:
        # AST parsers are high confidence
        # Regex or unknown parsers are lower confidence
        if parser_name in ("DependencyParser", "ASTParser", "AnnotationProvider"):
            return 1.0
        if "Regex" in parser_name:
            return 0.8
        return 0.9
