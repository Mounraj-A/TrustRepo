"""
Reasoning Agent

The Core Reasoning Agent in the TrustRepo Multi-Agent Architecture.
Orchestrates the complete verification pipeline:

    Expected Features (Ontology)
         ↓
    Evidence Chains (from EvidenceFusionEngine)
         ↓
    Evidence Quality Assessment
         ↓
    Evidence Validation
         ↓
    Decision Matrix (Expected vs. Observed)
         ↓
    Deterministic Confidence Calculation
         ↓
    Verdict (5-state)

Architecture position:
    EvidenceFusionAgent → EvidenceValidationAgent → ReasoningAgent → VerificationAgent
"""
from typing import List, Tuple

from app.models.claim import Claim
from app.models.knowledge.investigation import VerificationVerdict
from app.models.report.trust_report import VerificationCategory
from app.models.knowledge.evidence import EvidenceChain
from app.services.verification.ontology import Ontology
from app.services.verification.decision_matrix import DecisionMatrix, DecisionVerdictState
from app.services.verification.evidence_quality_assessor import EvidenceQualityAssessor
from app.services.verification.evidence_validation_engine import EvidenceValidationEngine


class ReasoningAgent:
    """
    The Core Reasoning Engine for the TrustRepo architecture.
    Orchestrates the deterministic verification pipeline.
    """

    def __init__(self):
        self.decision_matrix = DecisionMatrix()
        self.quality_assessor = EvidenceQualityAssessor()
        self.validation_engine = EvidenceValidationEngine()

    def evaluate(
        self,
        claim: Claim,
        evidence_chains: List[EvidenceChain],
    ) -> Tuple[VerificationVerdict, VerificationCategory, str, float]:
        """
        Evaluates a claim against the full reasoning pipeline.

        Pipeline:
        1. Intent Extraction (Ontology)
        2. Evidence Quality Assessment
        3. Evidence Validation
        4. Decision Matrix (Expected vs. Observed)
        5. Deterministic Confidence Formula
        6. Verdict Selection

        Returns: (Verdict, Category, Reasoning Trace, Confidence)
        """
        trace = []

        # ── Stage 1: Intent Extraction & Expected Features ───────────────────
        expected_features = Ontology.normalize(claim.text)
        if not expected_features or expected_features == ["General"]:
            expected_features = ["General Architectural Claim"]
        trace.append(
            f"[Stage 1 — Ontology] Normalized claim to expected features: {expected_features}")

        # ── Stage 2: Evidence Quality Assessment ─────────────────────────────
        quality_results = self.quality_assessor.assess_all(evidence_chains)
        aggregate_quality = self.quality_assessor.aggregate_quality(
            quality_results)
        for qr in quality_results:
            trace.append(
                f"[Stage 2 — Quality] Chain '{qr.chain_id[:8]}': "
                f"{
                    qr.quality_label} (score={
                    qr.quality_score:.2f}, class={
                    qr.classification.value})"
            )

        # ── Stage 3: Evidence Validation (false positive + completeness) ─────
        tech_context = claim.text
        validation_results = self.validation_engine.validate_all(
            evidence_chains, tech_context)
        valid_chain_ids = {
            vr.chain_id for vr in validation_results if vr.is_valid}
        validated_chains = [
            c for c in evidence_chains if c.chain_id in valid_chain_ids]

        false_positives = [
            vr for vr in validation_results if vr.is_false_positive]
        trace.append(
            f"[Stage 3 — Validation] {
                len(validated_chains)} of {
                len(evidence_chains)} chains passed. "
            f"{len(false_positives)} false positives removed."
        )
        for fp in false_positives:
            trace.append(f"  ⚠ False Positive: {fp.false_positive_reason}")

        # ── Stage 4: Extract Observed Features from validated chains ─────────
        observed_features = self._extract_observed_features(
            validated_chains, expected_features)
        trace.append(
            f"[Stage 4 — Observation] Observed features: {observed_features}")

        # ── Stage 5: Decision Matrix ─────────────────────────────────────────
        dm_result = self.decision_matrix.evaluate(
            expected_features, observed_features, tech_context)
        trace.append(
            f"[Stage 5 — Decision Matrix]\n{
                dm_result.reasoning_trace}")

        # ── Stage 6: Dynamic Evidence-Based Confidence ───────────────────────
        # Determine the types of evidence we found
        evidence_types_found = set()
        for chain in validated_chains:
            for item in chain.sequence:
                kind = item.context_type.lower()
                if "import" in kind:
                    evidence_types_found.add("Import detected")
                if "method" in kind or "function" in kind:
                    evidence_types_found.add("Function calls detected")
                if "class" in kind:
                    evidence_types_found.add("Class usage detected")
                if "dependency" in kind:
                    evidence_types_found.add("Dependency found")
                if "annotation" in kind or "decorator" in kind:
                    evidence_types_found.add("Annotation/Decorator verified")

        # README mentions only count if code evidence also exists
        if dm_result.final_verdict == DecisionVerdictState.VERIFIED:
            evidence_types_found.add("README verified")

        # Calculate dynamic confidence
        # Base confidence from quality and consistency
        base_confidence = (0.4 * aggregate_quality) + \
            (0.3 * dm_result.consistency_score)

        # Add dynamic bonuses based on evidence types found
        evidence_bonus = min(len(evidence_types_found) * 0.1, 0.3)

        confidence = round(min(base_confidence + evidence_bonus, 1.0), 4)

        trace.append(f"[Stage 6 — Confidence] Score: {confidence:.2%}")
        trace.append("Evidence breakdown:")
        if not evidence_types_found:
            trace.append("  ⚠ No strong code evidence verified.")
        else:
            for ev in sorted(evidence_types_found):
                trace.append(f"  ✓ {ev}")

        # ── Stage 7: Map Decision Matrix Verdict to VerificationVerdict ──────
        verdict = self._map_verdict(dm_result.final_verdict)
        category = self._infer_category(claim.text)
        trace.append(f"[Stage 7 — Verdict] {verdict.value} | {category.value}")

        return verdict, category, "\n".join(trace), round(confidence * 100, 2)

    # ─── Internal helpers ───────────────────────────────────────────────────

    def _extract_observed_features(
        self, chains: List[EvidenceChain], expected_features: List[str]
    ) -> List[str]:
        """
        Checks which expected features are corroborated by the validated chains.
        Returns the subset of features that are actually observed in evidence.
        """
        observed = []
        for feat in expected_features:
            feat_lower = feat.lower()
            for chain in chains:
                evidence_text = (
                    chain.chain_type.lower() + " " +
                    chain.reasoning_trace.lower() + " " +
                    " ".join(item.code_snippet.lower() + " " + item.symbol.lower()
                             for item in chain.sequence)
                )
                if feat_lower in evidence_text:
                    observed.append(feat)
                    break
        return list(set(observed))

    def _map_verdict(
            self, decision_verdict: DecisionVerdictState) -> VerificationVerdict:
        """Maps Decision Matrix 5-state to VerificationVerdict."""
        mapping = {
            DecisionVerdictState.VERIFIED: VerificationVerdict.VERIFIED,
            DecisionVerdictState.CONTRADICTION: VerificationVerdict.CONTRADICTION,
            DecisionVerdictState.MISSING_DOCUMENTATION: VerificationVerdict.MISSING_DOCUMENTATION,
            DecisionVerdictState.UNSUPPORTED_DOCUMENTATION: VerificationVerdict.MISSING_DOCUMENTATION,
            DecisionVerdictState.PARTIAL_DOCUMENTATION: VerificationVerdict.PARTIAL_DOCUMENTATION,
        }
        return mapping.get(
            decision_verdict, VerificationVerdict.MISSING_DOCUMENTATION)

    def _infer_category(self, claim_text: str) -> VerificationCategory:
        """Infers verification category from the claim text via the Ontology."""
        claim_lower = claim_text.lower()
        if any(k in claim_lower for k in [
               "security", "auth", "jwt", "oauth", "login"]):
            return VerificationCategory.SECURITY
        if any(k in claim_lower for k in [
               "database", "jpa", "sql", "mongo", "redis"]):
            return VerificationCategory.DEPENDENCY
        if any(k in claim_lower for k in [
               "microservice", "monolith", "architecture", "layer"]):
            return VerificationCategory.ARCHITECTURE
        if any(k in claim_lower for k in [
               "api", "endpoint", "rest", "graphql"]):
            return VerificationCategory.BEHAVIORAL
        if any(k in claim_lower for k in ["docker", "kubernetes", "config"]):
            return VerificationCategory.CONFIGURATION
        return VerificationCategory.STRUCTURAL
