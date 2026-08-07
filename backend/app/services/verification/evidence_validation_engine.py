"""
Evidence Validation Engine

Validates EvidenceChains before they enter the Reasoning Engine.
Implements structured validation rules, policies, validation scoring,
false positive detection, and completeness checks.

Architecture position: Evidence Retrieval → Evidence Validation → Evidence Fusion → Reasoning

Key principle: A single 'import jwt' is NOT sufficient to claim JWT Authentication.
Validation rules enforce topological completeness requirements.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

from app.models.knowledge.evidence import EvidenceChain, EvidenceItem


class ValidationOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"


@dataclass
class ValidationRuleResult:
    rule_id: str
    rule_name: str
    outcome: ValidationOutcome
    message: str
    penalty: float = 0.0    # Subtracted from validation score


@dataclass
class EvidenceValidationResult:
    chain_id: str
    validation_score: float          # 0.0 – 1.0
    is_valid: bool
    is_false_positive: bool
    is_complete: bool
    rule_results: List[ValidationRuleResult] = field(default_factory=list)
    false_positive_reason: str = ""


# ─── Validation Rules ────────────────────────────────────────────────────────

# Topological completeness policies:
# Each policy defines what OTHER evidence must co-exist with a primary signal
# to prevent single-node false positives.
COMPLETENESS_POLICIES: Dict[str, Dict] = {
    "jwt": {
        "description": "JWT Authentication requires Import + Filter/Provider",
        "required_symbols": ["JwtFilter", "JwtProvider", "JwtUtil", "JwtTokenUtil"],
        "required_min": 1,
    },
    "spring security": {
        "description": "Spring Security requires WebSecurityConfigurer or SecurityFilterChain",
        "required_symbols": ["WebSecurityConfigurerAdapter", "SecurityFilterChain", "WebSecurityConfigurer"],
        "required_min": 1,
    },
    "oauth2": {
        "description": "OAuth2 requires OAuth2LoginConfigurer or ResourceServer",
        "required_symbols": ["OAuth2Login", "ResourceServer", "OAuth2AuthorizedClient"],
        "required_min": 1,
    },
    "jpa": {
        "description": "JPA requires at least one @Entity and one Repository",
        "required_symbols": ["Entity", "Repository", "JpaRepository"],
        "required_min": 2,
    },
}

# False positive patterns: if ONLY these are present without corroborating evidence,
# the chain is likely a false positive
FALSE_POSITIVE_PATTERNS: List[Dict] = [
    {
        "trigger_snippet": "import jwt",
        "requires_corroboration": ["JwtFilter", "JwtProvider", "AuthenticationManager"],
        "reason": "Bare 'import jwt' without a filter or provider is insufficient evidence."
    },
    {
        "trigger_snippet": "import redis",
        "requires_corroboration": ["RedisTemplate", "CacheManager", "@Cacheable"],
        "reason": "Bare 'import redis' without caching configuration is insufficient."
    },
]


class EvidenceValidationEngine:
    """
    Validates EvidenceChains against defined policies before they reach the Reasoning Engine.
    """

    def validate(self, chain: EvidenceChain, technology_context: str = "") -> EvidenceValidationResult:
        """Validate a single EvidenceChain, returning a structured validation result."""
        rule_results: List[ValidationRuleResult] = []
        total_penalty = 0.0

        # Rule 1: Chain must have at least one item
        r1 = self._rule_non_empty(chain)
        rule_results.append(r1)
        if r1.outcome == ValidationOutcome.FAIL:
            total_penalty += r1.penalty

        # Rule 2: Provenance check — file path must be known
        r2 = self._rule_known_source(chain)
        rule_results.append(r2)
        if r2.outcome == ValidationOutcome.FAIL:
            total_penalty += r2.penalty

        # Rule 3: Ranking score must be above minimum threshold
        r3 = self._rule_ranking_threshold(chain)
        rule_results.append(r3)
        if r3.outcome == ValidationOutcome.FAIL:
            total_penalty += r3.penalty

        # Rule 4: False positive detection
        r4, fp_reason = self._rule_false_positive_check(chain)
        rule_results.append(r4)
        is_false_positive = r4.outcome == ValidationOutcome.FAIL
        if is_false_positive:
            total_penalty += r4.penalty

        # Rule 5: Completeness policy check (technology-specific)
        r5, is_complete = self._rule_completeness_policy(chain, technology_context)
        rule_results.append(r5)
        if r5.outcome == ValidationOutcome.WARN:
            total_penalty += r5.penalty

        # Validation Score
        validation_score = round(max(1.0 - total_penalty, 0.0), 4)
        is_valid = validation_score >= 0.4 and not is_false_positive

        return EvidenceValidationResult(
            chain_id=chain.chain_id,
            validation_score=validation_score,
            is_valid=is_valid,
            is_false_positive=is_false_positive,
            is_complete=is_complete,
            rule_results=rule_results,
            false_positive_reason=fp_reason,
        )

    def validate_all(self, chains: List[EvidenceChain], technology_context: str = "") -> List[EvidenceValidationResult]:
        return [self.validate(chain, technology_context) for chain in chains]

    def filter_valid(self, chains: List[EvidenceChain], technology_context: str = "") -> List[EvidenceChain]:
        """Return only chains that pass validation."""
        results = self.validate_all(chains, technology_context)
        valid_ids = {r.chain_id for r in results if r.is_valid}
        return [c for c in chains if c.chain_id in valid_ids]

    # ─── Individual Rules ─────────────────────────────────────────────────────

    def _rule_non_empty(self, chain: EvidenceChain) -> ValidationRuleResult:
        if chain.sequence:
            return ValidationRuleResult("R1", "NonEmpty", ValidationOutcome.PASS, "Chain has items.")
        return ValidationRuleResult("R1", "NonEmpty", ValidationOutcome.FAIL,
                                    "Chain has no evidence items — cannot validate.", penalty=0.8)

    def _rule_known_source(self, chain: EvidenceChain) -> ValidationRuleResult:
        unknown_sources = [
            item for item in chain.sequence
            if item.source.file_path in ("", "Unknown", "unknown")
        ]
        if not unknown_sources:
            return ValidationRuleResult("R2", "KnownSource", ValidationOutcome.PASS, "All items have known file paths.")
        return ValidationRuleResult("R2", "KnownSource", ValidationOutcome.WARN,
                                    f"{len(unknown_sources)} items have unknown source paths.", penalty=0.15)

    def _rule_ranking_threshold(self, chain: EvidenceChain) -> ValidationRuleResult:
        if chain.ranking_score >= 0.5:
            return ValidationRuleResult("R3", "RankingThreshold", ValidationOutcome.PASS,
                                        f"Ranking score {chain.ranking_score} meets threshold.")
        return ValidationRuleResult("R3", "RankingThreshold", ValidationOutcome.FAIL,
                                    f"Ranking score {chain.ranking_score} below threshold 0.5.", penalty=0.3)

    def _rule_false_positive_check(self, chain: EvidenceChain) -> tuple:
        all_snippets = " ".join(item.code_snippet.lower() for item in chain.sequence)
        all_symbols = " ".join(item.symbol.lower() for item in chain.sequence)

        for pattern in FALSE_POSITIVE_PATTERNS:
            trigger = pattern["trigger_snippet"].lower()
            if trigger in all_snippets:
                # Check if ANY corroborating symbol is present
                corroborated = any(
                    corr.lower() in all_symbols
                    for corr in pattern["requires_corroboration"]
                )
                if not corroborated:
                    rule = ValidationRuleResult(
                        "R4", "FalsePositiveDetection", ValidationOutcome.FAIL,
                        pattern["reason"], penalty=1.0
                    )
                    return rule, pattern["reason"]

        return ValidationRuleResult("R4", "FalsePositiveDetection", ValidationOutcome.PASS,
                                    "No false positive patterns detected."), ""

    def _rule_completeness_policy(self, chain: EvidenceChain, tech_context: str) -> tuple:
        tech_lower = tech_context.lower()
        policy = None
        for key, p in COMPLETENESS_POLICIES.items():
            if key in tech_lower:
                policy = p
                break

        if not policy:
            return ValidationRuleResult("R5", "CompletenessPolicy", ValidationOutcome.PASS,
                                        "No specific completeness policy for this technology."), True

        all_symbols = " ".join(item.symbol.lower() for item in chain.sequence)
        matched = [sym for sym in policy["required_symbols"] if sym.lower() in all_symbols]

        if len(matched) >= policy["required_min"]:
            return ValidationRuleResult("R5", "CompletenessPolicy", ValidationOutcome.PASS,
                                        f"Completeness satisfied: {matched}"), True

        return ValidationRuleResult(
            "R5", "CompletenessPolicy", ValidationOutcome.WARN,
            f"{policy['description']}. Found {matched}, required {policy['required_symbols'][:policy['required_min']]}.",
            penalty=0.2
        ), False
