from typing import List
from app.models.knowledge.feature_instance import FeatureInstance
from app.models.knowledge.evidence import EvidenceStrength


class FeatureConfidenceEngine:
    """
    Calculates the final confidence score for a FeatureInstance based on the quantity,
    strength, and diversity of its aggregated evidence.
    """

    def calculate(
            self, features: List[FeatureInstance]) -> List[FeatureInstance]:
        for feat in features:
            feat.confidence = self._compute_confidence(feat)
        return features

    def _compute_confidence(self, feat: FeatureInstance) -> float:
        if not feat.evidence:
            return 0.0

        base_score = 0.0
        primary_count = 0
        secondary_count = 0
        supporting_count = 0

        # We also look at the diversity of evidence types (Annotation, Import,
        # Config, etc.)
        context_types = set()

        for chain in feat.evidence:
            for item in chain.sequence:
                context_types.add(item.context_type)
                if item.evidence_strength == EvidenceStrength.PRIMARY:
                    primary_count += 1
                elif item.evidence_strength == EvidenceStrength.SECONDARY:
                    secondary_count += 1
                else:
                    supporting_count += 1

        # Score calculation logic
        # PRIMARY evidence gives a strong base
        if primary_count >= 2:
            base_score = 0.85
        elif primary_count == 1:
            base_score = 0.70
        elif secondary_count >= 2:
            base_score = 0.50
        elif secondary_count == 1:
            base_score = 0.30
        else:
            base_score = 0.10

        # Diversity bonus (up to 0.15)
        diversity_bonus = min(len(context_types) * 0.05, 0.15)

        # Volume bonus (up to 0.10)
        total_evidence = primary_count + secondary_count + supporting_count
        volume_bonus = min(total_evidence * 0.02, 0.10)

        # Calculate final confidence
        confidence = base_score + diversity_bonus + volume_bonus

        # Cap at 1.0
        return round(min(confidence, 1.0), 3)
