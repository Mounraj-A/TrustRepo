"""
Decision Matrix

The Decision Matrix sits between the Reasoning Engine and the Verification Engine.
It accepts the full Expected/Observed feature representations and applies formal
coverage and consistency analysis to select the deterministic 5-state verdict.

Architecture position:
    Reasoning Agent → Decision Matrix → Verdict → VerificationResult

Decision Matrix Schema:
    ┌─────────────────────────────────────────────────────────┐
    │  Expected Feature   │  Observed Feature  │  Decision    │
    ├─────────────────────────────────────────────────────────┤
    │  Spring Security     │  Spring Security   │  VERIFIED    │
    │  JWT                 │  OAuth2            │  CONTRADICTION│
    │  JPA                 │  (missing)         │  MISSING_DOC │
    │  (not claimed)       │  Redis             │  UNDOCUMENTED│
    │  Spring Security     │  Partial config    │  PARTIAL     │
    └─────────────────────────────────────────────────────────┘
"""
from typing import List, Set
from dataclasses import dataclass, field
from enum import Enum


class DecisionVerdictState(str, Enum):
    VERIFIED = "VERIFIED"
    CONTRADICTION = "CONTRADICTION"
    MISSING_DOCUMENTATION = "MISSING_DOCUMENTATION"
    UNSUPPORTED_DOCUMENTATION = "UNSUPPORTED_DOCUMENTATION"
    PARTIAL_DOCUMENTATION = "PARTIAL_DOCUMENTATION"


@dataclass
class FeatureComparison:
    """Represents a single row in the Decision Matrix."""
    feature_name: str
    expected: bool          # Documented in README
    observed: bool          # Found in code via Evidence
    verdict: DecisionVerdictState
    reasoning: str


@dataclass
class DecisionMatrixResult:
    """Complete output of the Decision Matrix evaluation."""
    final_verdict: DecisionVerdictState
    coverage_score: float               # 0.0 – 1.0
    consistency_score: float            # 0.0 – 1.0
    comparisons: List[FeatureComparison] = field(default_factory=list)
    expected_features: List[str] = field(default_factory=list)
    observed_features: List[str] = field(default_factory=list)
    missing_features: List[str] = field(default_factory=list)
    unsupported_features: List[str] = field(default_factory=list)
    contradicted_features: List[str] = field(default_factory=list)
    reasoning_trace: str = ""


# Known contradicting pairs: if expected X and observed Y, it is a
# Contradiction
CONTRADICTION_PAIRS: List[tuple] = [
    ("jwt", "oauth2"),
    ("jwt", "session"),
    ("mysql", "mongodb"),
    ("postgresql", "mongodb"),
    ("rest_api", "graphql"),
    ("microservices", "monolith"),
]


class DecisionMatrix:
    """
    Applies formal coverage and consistency analysis to produce a deterministic verdict.
    This is the sole source of truth for all verdict decisions.
    """

    def evaluate(
        self,
        expected_features: List[str],
        observed_features: List[str],
        technology_context: str = "",
    ) -> DecisionMatrixResult:
        """
        Core evaluation:
        - Compares expected (from normalized claims) vs observed (from validated evidence)
        - Computes coverage and consistency scores
        - Selects verdict from the 5-state model
        """
        expected_set = {f.lower() for f in expected_features}
        observed_set = {f.lower() for f in observed_features}

        comparisons: List[FeatureComparison] = []

        # Row-by-row comparison
        all_features = expected_set | observed_set
        for feat in sorted(all_features):
            exp = feat in expected_set
            obs = feat in observed_set

            if exp and obs:
                row_verdict = DecisionVerdictState.VERIFIED
                reason = f"'{feat}' is documented and confirmed in code."
            elif exp and not obs:
                row_verdict = DecisionVerdictState.MISSING_DOCUMENTATION
                reason = f"'{feat}' is documented but not found in code implementation."
            elif not exp and obs:
                row_verdict = DecisionVerdictState.UNSUPPORTED_DOCUMENTATION
                reason = f"'{feat}' was found in code but not mentioned in documentation."
            else:
                row_verdict = DecisionVerdictState.MISSING_DOCUMENTATION
                reason = "Feature present in neither documentation nor code."

            comparisons.append(FeatureComparison(
                feature_name=feat,
                expected=exp,
                observed=obs,
                verdict=row_verdict,
                reasoning=reason,
            ))

        # Contradiction scan
        contradicted = self._detect_contradictions(expected_set, observed_set)
        for pair in contradicted:
            comparisons.append(FeatureComparison(
                feature_name=f"{pair[0]} vs {pair[1]}",
                expected=True,
                observed=True,
                verdict=DecisionVerdictState.CONTRADICTION,
                reasoning=f"Documentation claims '{
                    pair[0]}' but code implements '{
                    pair[1]}'.",
            ))

        # Coverage Score = |expected ∩ observed| / |expected|
        if expected_set:
            matched = expected_set & observed_set
            coverage_score = round(len(matched) / len(expected_set), 4)
        else:
            coverage_score = 0.0

        # Consistency Score = 1 - (contradictions / total features)
        contradiction_count = len(contradicted)
        total = max(len(all_features), 1)
        consistency_score = round(
            max(1.0 - (contradiction_count / total), 0.0), 4)

        # Final Verdict Selection
        missing_features = [f for f in expected_set if f not in observed_set]
        unsupported_features = [
            f for f in observed_set if f not in expected_set]

        final_verdict = self._select_verdict(
            coverage_score, consistency_score, contradicted, missing_features, unsupported_features
        )

        # Build reasoning trace
        reasoning_trace = self._build_trace(
            expected_features, observed_features, coverage_score, consistency_score,
            missing_features, unsupported_features, contradicted, final_verdict
        )

        return DecisionMatrixResult(
            final_verdict=final_verdict,
            coverage_score=coverage_score,
            consistency_score=consistency_score,
            comparisons=comparisons,
            expected_features=list(expected_features),
            observed_features=list(observed_features),
            missing_features=missing_features,
            unsupported_features=unsupported_features,
            contradicted_features=[f"{p[0]}↔{p[1]}" for p in contradicted],
            reasoning_trace=reasoning_trace,
        )

    # ─── Internal helpers ───────────────────────────────────────────────────

    def _detect_contradictions(
            self, expected: Set[str], observed: Set[str]) -> List[tuple]:
        """Returns list of (expected, observed) pairs that are direct contradictions."""
        found = []
        for exp_kw, obs_kw in CONTRADICTION_PAIRS:
            if exp_kw in expected and obs_kw in observed:
                found.append((exp_kw, obs_kw))
        return found

    def _select_verdict(
        self,
        coverage: float,
        consistency: float,
        contradictions: list,
        missing: list,
        unsupported: list,
    ) -> DecisionVerdictState:
        """Deterministic verdict selection from the 5-state model."""
        # Contradiction takes absolute precedence
        if contradictions:
            return DecisionVerdictState.CONTRADICTION

        # High coverage but some features undocumented in README
        if coverage >= 0.5 and unsupported and not missing:
            return DecisionVerdictState.UNSUPPORTED_DOCUMENTATION

        # Full coverage and high consistency
        if coverage >= 0.9 and consistency >= 0.9 and not missing:
            return DecisionVerdictState.VERIFIED

        # Partial: some features verified, some missing
        if coverage >= 0.3 and missing:
            return DecisionVerdictState.PARTIAL_DOCUMENTATION

        # Nothing in code, only in docs
        if missing and not unsupported:
            return DecisionVerdictState.MISSING_DOCUMENTATION

        return DecisionVerdictState.MISSING_DOCUMENTATION

    def _build_trace(
        self, expected, observed, coverage, consistency,
        missing, unsupported, contradictions, verdict
    ) -> str:
        lines = [
            f"Expected Features  : {expected}",
            f"Observed Features  : {observed}",
            f"Coverage Score     : {coverage:.2%}",
            f"Consistency Score  : {consistency:.2%}",
            f"Missing Features   : {missing}",
            f"Unsupported Feats  : {unsupported}",
            f"Contradictions     : {[f'{a}↔{b}' for a, b in contradictions]}",
            f"Final Verdict      : {verdict.value}",
        ]
        return "\n".join(lines)
