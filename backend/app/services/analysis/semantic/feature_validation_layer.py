from typing import List
from app.models.knowledge.feature_instance import FeatureInstance
from app.models.knowledge.evidence import EvidenceStrength


class FeatureValidationLayer:
    """
    Validates fused features to prevent false positives before persistence.
    Applies logic to ensure that a feature has sufficient evidence to be considered 'Verified'.
    """

    def validate(
            self, features: List[FeatureInstance]) -> List[FeatureInstance]:
        valid_features = []

        for feat in features:
            if self._is_valid(feat):
                valid_features.append(feat)

        return valid_features

    def _is_valid(self, feat: FeatureInstance) -> bool:
        # 1. Must have at least some evidence
        if not feat.evidence:
            return False

        # 2. Check for PRIMARY evidence
        has_primary = False
        secondary_count = 0

        for chain in feat.evidence:
            for item in chain.sequence:
                if item.evidence_strength == EvidenceStrength.PRIMARY:
                    has_primary = True
                elif item.evidence_strength == EvidenceStrength.SECONDARY:
                    secondary_count += 1

        # Feature is valid if it has at least 1 PRIMARY evidence
        # OR at least 2 SECONDARY evidence pieces
        if has_primary or secondary_count >= 2:
            return True

        # 3. Special rules per feature definition could be implemented here
        # e.g., if feat.definition_id == "feat_rest_api":
        #       must have at least one method-level mapping annotation

        return False
