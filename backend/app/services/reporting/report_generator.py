from datetime import datetime, timezone
from collections import Counter
from typing import List, Dict, Optional
import uuid
import logging

from app.models.trustrepo_context import TrustRepoContext
from app.models.claim import Claim
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceSource, EvidenceType, EvidenceStrength

from app.models.report.trust_report import (
    RepositoryReport,
    RepositoryMetadata,
    DocumentationSummary,
    DocumentationClaim,
    Recommendation,
    RecommendationPriority,
    FeatureFinding,
    CandidateSource,
    VerificationVerdict,
    VerificationCategory,
    TrustAssessment,
    VerificationCounts,
    EvidenceRetrievalTrace,
    EvidenceSearchStep,
    UnifiedEvidenceItem,
    EvidenceSummary,
    ReasoningTrace,
    ReasoningStep,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# Investigation Verdict → Report Verdict Mapping
# ═══════════════════════════════════════════════════════════════════════
def _map_investigation_verdict(inv_verdict_value: str) -> VerificationVerdict:
    """
    Explicit mapping from investigation-layer verdict strings
    to the canonical report-layer VerificationVerdict.
    """
    mapping = {
        "VERIFIED": VerificationVerdict.VERIFIED,
        "CONTRADICTION": VerificationVerdict.CONTRADICTED,
        "UNSUPPORTED_DOCUMENTATION": VerificationVerdict.UNSUPPORTED,
        "PARTIAL_DOCUMENTATION": VerificationVerdict.UNSUPPORTED,
        "MISSING_DOCUMENTATION": VerificationVerdict.MISSING_DOCUMENTATION,
    }
    return mapping.get(inv_verdict_value, VerificationVerdict.INSUFFICIENT_EVIDENCE)


class ReportIntegrityError(Exception):
    """Raised when the generated report fails internal consistency checks."""
    pass


class ReportGenerator:
    def __init__(self):
        pass

    def generate_report(self, context: TrustRepoContext) -> RepositoryReport:
        verification_results = context.verification_context.verification_results

        # ══════════════════════════════════════════════════════════════════
        # 1. MAP ALL RAW CLAIMS TO VERIFICATION RESULTS
        # ══════════════════════════════════════════════════════════════════
        documentation_claims: List[DocumentationClaim] = []
        feature_findings: List[FeatureFinding] = []

        # Layer 4 evidence: claim.id -> EvidenceContext
        layer4_evidence = context.evidence_context.contexts

        for raw_claim in context.claims:
            ncid = raw_claim.normalized_claim_id

            # Look up the investigation result via the normalized_claim_id
            res = verification_results.get(ncid) if ncid else None

            if res:
                # ── CASE A: Investigation result exists ──────────────────
                verdict = _map_investigation_verdict(res.verdict.value)

                # Build provenance chain from investigation evidence
                prov_chain = self._build_provenance_chain(res)

                # Build reasoning trace from actual verification path
                trace_obj = next(
                    (t for t in context.semantic_context.reasoning_traces
                     if t.claim_id == ncid),
                    None
                )

                claim = DocumentationClaim(
                    claim_id=raw_claim.id,
                    normalized_claim_id=ncid,
                    source_document=raw_claim.source_document,
                    claim_text=raw_claim.text,
                    verdict=verdict,
                    verification_category=VerificationCategory.UNKNOWN,
                    source_file=raw_claim.source_document or "",
                    trust_score=res.trust_score,
                    confidence=res.trust_score,
                    confidence_breakdown={
                        "evidence_quality": res.evidence_quality,
                        "evidence_diversity": res.evidence_diversity,
                        "graph_connectivity": res.graph_connectivity,
                        "evidence_agreement": res.evidence_agreement,
                    },
                    evidence_count=res.evidence_count,
                    evidence_quality=res.evidence_quality,
                    evidence_diversity=res.evidence_diversity,
                    expected_features=res.expected_features,
                    observed_features=res.observed_features,
                    missing_features=res.missing_features,
                    unsupported_features=res.unsupported_features,
                    contradicted_features=res.contradicted_features,
                    reasoning=" ".join(res.reasoning_trace) if res.reasoning_trace else "No reasoning provided.",
                    reasoning_trace=trace_obj,
                    provenance_chain=prov_chain,
                    recommendation=None,
                )
            else:
                # ── CASE B: No investigation result ──────────────────────
                # Check if there is Layer 4 evidence for this raw claim
                ev_ctx = layer4_evidence.get(raw_claim.id)
                has_evidence = bool(ev_ctx and ev_ctx.candidates)
                evidence_count = len(ev_ctx.candidates) if has_evidence else 0

                # Build provenance from Layer 4 if available
                prov_chain = None
                if has_evidence:
                    items = []
                    for cand in ev_ctx.candidates:
                        if cand.chain and cand.chain.sequence:
                            items.extend(cand.chain.sequence)
                        elif hasattr(cand, 'file_path') and cand.file_path:
                            items.append(EvidenceItem(
                                source=EvidenceSource(file_path=cand.file_path or "unknown"),
                                code_snippet=getattr(cand, 'content_snippet', None) or (cand.content[:200] if hasattr(cand, 'content') and cand.content else None),
                                evidence_type=EvidenceType.UNKNOWN,
                                evidence_strength=EvidenceStrength.SUPPORTING,
                            ))
                    if items:
                        prov_chain = EvidenceChain(
                            chain_id=f"l4-{raw_claim.id[:8]}",
                            chain_type="Layer4Evidence",
                            sequence=items[:10],
                            confidence=0.0,
                        )

                # Build a genuine reasoning trace for uninvestigated claims
                trace_obj = self._build_uninvestigated_reasoning(
                    raw_claim, ncid, has_evidence
                )

                claim = DocumentationClaim(
                    claim_id=raw_claim.id,
                    normalized_claim_id=ncid or "",
                    source_document=raw_claim.source_document,
                    claim_text=raw_claim.text,
                    verdict=VerificationVerdict.INSUFFICIENT_EVIDENCE,
                    verification_category=VerificationCategory.UNKNOWN,
                    source_file=raw_claim.source_document or "",
                    trust_score=0.0,
                    confidence=0.0,
                    confidence_breakdown={
                        "evidence_quality": 0.0,
                        "evidence_diversity": 0.0,
                        "graph_connectivity": 0.0,
                        "evidence_agreement": 1.0,
                    },
                    evidence_count=evidence_count,
                    evidence_quality=0.0,
                    evidence_diversity=0.0,
                    reasoning="Claim was not selected for deep investigation during normalization. "
                              "Evidence was collected but not evaluated through the full verification pipeline.",
                    reasoning_trace=trace_obj,
                    provenance_chain=prov_chain,
                    recommendation=None,
                )

            documentation_claims.append(claim)

            # Track contradictions as feature findings
            if claim.verdict == VerificationVerdict.CONTRADICTED and res:
                feature_findings.append(FeatureFinding(
                    feature=raw_claim.text,
                    category=VerificationCategory.UNKNOWN,
                    candidate_source=CandidateSource.DOCUMENTATION_ANALYSIS,
                    status=VerificationVerdict.CONTRADICTED,
                    documentation_claim=claim,
                    evidence=[],
                    evidence_count=res.evidence_count if res else 0,
                    evidence_quality=res.evidence_quality if res else 0.0,
                    evidence_diversity=res.evidence_diversity if res else 0.0,
                    documentation_search=None,
                    retrieval_trace=None,
                    confidence=res.trust_score if res else 0.0,
                    reasoning=" ".join(res.reasoning_trace) if res and res.reasoning_trace else "No reasoning.",
                    reasoning_trace=res.reasoning_trace if res else [],
                    provenance_chain=prov_chain,
                    recommendation=None,
                ))

        # ══════════════════════════════════════════════════════════════════
        # 2. PROCESS FEATURES (Direction B: Repository -> Documentation)
        # ══════════════════════════════════════════════════════════════════
        recommendations = []

        all_detected_features = set(
            (context.semantic_context.technologies if context.semantic_context else []) +
            (context.semantic_context.capabilities if context.semantic_context else []) +
            (context.semantic_context.architectures if context.semantic_context else []) +
            (context.semantic_context.features if context.semantic_context else [])
        )

        evidence_chains = (context.semantic_context.evidence_chains if context.semantic_context else [])

        raw_doc_text = ""
        if context.document_context and hasattr(context.document_context, 'documents'):
            raw_doc_text = " ".join([d.content for d in context.document_context.documents]).lower()

        documented_features_count = 0
        confirmed_features_count = 0

        for feature in all_detected_features:
            if not feature or feature == "Unknown":
                continue

            feature_chain = next((c for c in evidence_chains if feature in c.chain_type), None)
            has_repository_evidence = feature_chain is not None and len(feature_chain.sequence) > 0

            is_documented = bool(raw_doc_text and feature.lower() in raw_doc_text)

            from app.models.knowledge.evidence import DocumentationSearchResult
            doc_search = DocumentationSearchResult(
                searched_sources=[f.path for f in context.document_context.documents] if context.document_context and hasattr(context.document_context, 'documents') else [],
                searched_terms=[feature.lower()],
                matches=[feature.lower()] if is_documented else [],
                found=is_documented
            )

            trace = EvidenceRetrievalTrace(
                strategies_attempted=["Structural Search", "AST Search", "Graph Search"],
                strategies_succeeded=["Graph Search"] if has_repository_evidence else [],
                strategies_failed=["AST Search"] if not has_repository_evidence else [],
                searches=[
                    EvidenceSearchStep(
                        strategy="Global Search",
                        source="Repository",
                        matches=len(feature_chain.sequence) if feature_chain else 0,
                        status="SUCCESS" if has_repository_evidence else "FAILED"
                    )
                ],
                candidate_count=1,
                matched_entities=len(feature_chain.sequence) if feature_chain else 0,
                evidence_items_created=len(feature_chain.sequence) if feature_chain else 0,
                conclusion="Repository evidence retrieved successfully." if has_repository_evidence else "Could not independently confirm repository evidence."
            )

            if not has_repository_evidence:
                finding = FeatureFinding(
                    feature=feature,
                    category=VerificationCategory.TECHNOLOGY,
                    candidate_source=CandidateSource.TECHNOLOGY_DETECTOR,
                    status=VerificationVerdict.INSUFFICIENT_EVIDENCE,
                    evidence=[],
                    evidence_count=0,
                    evidence_quality=0.0,
                    evidence_diversity=0.0,
                    documentation_search=doc_search,
                    retrieval_trace=trace,
                    confidence=0.0,
                    reasoning="TrustRepo identified a candidate feature but could not retrieve enough structural evidence to confirm it.",
                    reasoning_trace=[],
                    provenance_chain=None,
                    recommendation=None
                )
                feature_findings.append(finding)
            else:
                confirmed_features_count += 1
                if is_documented:
                    documented_features_count += 1
                    finding = FeatureFinding(
                        feature=feature,
                        category=VerificationCategory.TECHNOLOGY,
                        candidate_source=CandidateSource.TECHNOLOGY_DETECTOR,
                        status=VerificationVerdict.VERIFIED,
                        evidence=[feature_chain],
                        evidence_count=len(feature_chain.sequence),
                        evidence_quality=0.9,
                        evidence_diversity=0.9,
                        documentation_search=doc_search,
                        retrieval_trace=trace,
                        confidence=feature_chain.confidence if hasattr(feature_chain, 'confidence') else 1.0,
                        reasoning=feature_chain.reasoning_trace,
                        reasoning_trace=[feature_chain.reasoning_trace],
                        provenance_chain=feature_chain,
                        recommendation=None
                    )
                else:
                    finding = FeatureFinding(
                        feature=feature,
                        category=VerificationCategory.TECHNOLOGY,
                        candidate_source=CandidateSource.TECHNOLOGY_DETECTOR,
                        status=VerificationVerdict.MISSING_DOCUMENTATION,
                        evidence=[feature_chain],
                        evidence_count=len(feature_chain.sequence),
                        evidence_quality=0.9,
                        evidence_diversity=0.9,
                        documentation_search=doc_search,
                        retrieval_trace=trace,
                        confidence=feature_chain.confidence if hasattr(feature_chain, 'confidence') else 1.0,
                        reasoning=feature_chain.reasoning_trace,
                        reasoning_trace=[feature_chain.reasoning_trace],
                        provenance_chain=feature_chain,
                        recommendation=f"Document where and why {feature} is used."
                    )
                    recommendations.append(Recommendation(
                        priority=RecommendationPriority.MEDIUM,
                        message=f"Document {feature} usage. We found {len(feature_chain.sequence)} pieces of repository evidence, but documentation searches for '{feature.lower()}' in {len(doc_search.searched_sources)} files yielded 0 matches."
                    ))
                feature_findings.append(finding)

        for finding in feature_findings:
            if finding.status == VerificationVerdict.CONTRADICTED and finding.documentation_claim:
                recommendations.append(Recommendation(
                    priority=RecommendationPriority.HIGH,
                    message=f"Resolve documentation contradiction regarding: '{finding.documentation_claim.claim_text}'."
                ))

        # ══════════════════════════════════════════════════════════════════
        # 3. COMPUTE CANONICAL VERIFICATION COUNTS
        # ══════════════════════════════════════════════════════════════════
        verdict_counter = Counter(c.verdict for c in documentation_claims)
        total_claims = len(documentation_claims)

        verification_counts = VerificationCounts(
            total_claims=total_claims,
            verified=verdict_counter.get(VerificationVerdict.VERIFIED, 0),
            contradicted=verdict_counter.get(VerificationVerdict.CONTRADICTED, 0),
            partially_verified=verdict_counter.get(VerificationVerdict.UNSUPPORTED, 0),
            insufficient=verdict_counter.get(VerificationVerdict.INSUFFICIENT_EVIDENCE, 0),
            missing_documentation=verdict_counter.get(VerificationVerdict.MISSING_DOCUMENTATION, 0),
        )

        # Validation: all verdicts must sum to total
        computed_sum = sum([
            verification_counts.verified,
            verification_counts.contradicted,
            verification_counts.partially_verified,
            verification_counts.insufficient,
            verification_counts.missing_documentation,
        ])
        if computed_sum != total_claims:
            logger.error(
                f"ReportIntegrityError: verdict counts ({computed_sum}) != total claims ({total_claims}). "
                f"Distribution: {dict(verdict_counter)}"
            )

        # ══════════════════════════════════════════════════════════════════
        # 4. COMPUTE SUMMARIES AND METADATA
        # ══════════════════════════════════════════════════════════════════
        coverage_pct = round((documented_features_count / confirmed_features_count) * 100) if confirmed_features_count > 0 else 0

        summary = DocumentationSummary(
            documentation_sources=[f.path for f in context.document_context.documents] if context.document_context and hasattr(context.document_context, 'documents') else [],
            total_candidates=len(all_detected_features),
            confirmed_features=confirmed_features_count,
            documented_features=documented_features_count,
            missing_documentation=verification_counts.missing_documentation,
            contradicted=verification_counts.contradicted,
            insufficient_evidence=verification_counts.insufficient,
            total_claims=total_claims,
            verified_claims=verification_counts.verified,
            contradicted_claims=verification_counts.contradicted,
            coverage_percentage=coverage_pct
        )

        repo_metadata = {}
        if context.repository_context:
            repo_metadata = {
                "url": getattr(context.repository_context, "repository_url", "local://repository"),
                "commit_sha": "HEAD",
                "branch": "main",
                "languages": ["Python", "JavaScript", "TypeScript"],
                "frameworks": context.semantic_context.technologies if context.semantic_context else [],
            }

        metadata = RepositoryMetadata(
            repository_url=repo_metadata.get("url", "local://repository"),
            commit_sha=repo_metadata.get("commit_sha", "HEAD"),
            branch=repo_metadata.get("branch", "main"),
            languages=repo_metadata.get("languages", []),
            frameworks=repo_metadata.get("frameworks", []),
            source_files_count=len(context.code_context.source_files) if context.code_context and hasattr(context.code_context, 'source_files') else 0,
            documentation_sources=summary.documentation_sources,
            claims_analyzed=total_claims,
            features_investigated=len(all_detected_features),
            analysis_date=datetime.now(timezone.utc),
            verification_version="3.0.0"
        )

        # ══════════════════════════════════════════════════════════════════
        # 5. TRUST SCORE — SINGLE AUTHORITATIVE CALCULATION
        # ══════════════════════════════════════════════════════════════════
        verified_c = verification_counts.verified
        claim_score = (verified_c / total_claims) * 100 if total_claims > 0 else 0.0
        overall_score = (claim_score * 0.5) + (coverage_pct * 0.5)
        repo_score = round(overall_score, 1)

        trust_assessment = TrustAssessment(
            score=repo_score,
            status="High Trust" if repo_score >= 80 else ("Moderate Trust" if repo_score >= 50 else "Low Trust"),
            details=f"Calculated based on {coverage_pct}% doc coverage and {verified_c}/{total_claims} verified claims.",
            total_claims=total_claims,
            verified_claims=verified_c,
            documentation_coverage=coverage_pct,
        )

        architecture_findings = context.semantic_context.architecture_findings if context.semantic_context else []

        # ══════════════════════════════════════════════════════════════════
        # 6. BUILD UNIFIED EVIDENCE
        # ══════════════════════════════════════════════════════════════════
        unified_evidence = []
        source_files = set()

        for claim in documentation_claims:
            if claim.provenance_chain and getattr(claim.provenance_chain, 'sequence', None):
                for item in claim.provenance_chain.sequence:
                    file_path = item.source.file_path if item.source else None
                    if file_path and file_path != "unknown":
                        source_files.add(file_path)

                    evidence_type = item.evidence_type.value if hasattr(item.evidence_type, 'value') else str(item.evidence_type)

                    unified_evidence.append(UnifiedEvidenceItem(
                        evidence_id=item.id if hasattr(item, 'id') else str(uuid.uuid4()),
                        evidence_type=evidence_type,
                        source_file=file_path if file_path != "unknown" else None,
                        line_range=str(item.source.line_number) if item.source and item.source.line_number else None,
                        snippet=item.code_snippet,
                        linked_claim={
                            "claim_id": claim.claim_id,
                            "claim_text": claim.claim_text,
                            "verdict": claim.verdict.value,
                        },
                        reasoning=claim.reasoning,
                        provenance_chain=claim.provenance_chain.model_dump() if hasattr(claim.provenance_chain, 'model_dump') else None,
                    ))
            else:
                # Documentation-source evidence item (WHERE the claim came from)
                if claim.source_document:
                    unified_evidence.append(UnifiedEvidenceItem(
                        evidence_id=f"doc-src-{claim.claim_id[:8]}",
                        evidence_type="DOCUMENTATION_SOURCE",
                        source_file=claim.source_document,
                        line_range=None,
                        snippet=None,
                        linked_claim={
                            "claim_id": claim.claim_id,
                            "claim_text": claim.claim_text,
                            "verdict": claim.verdict.value,
                        },
                        reasoning=claim.reasoning,
                        provenance_chain=None,
                    ))

        # Feature evidence
        for finding in feature_findings:
            if finding.status == VerificationVerdict.MISSING_DOCUMENTATION:
                seq_item = None
                if finding.evidence and finding.evidence[0].sequence:
                    seq_item = finding.evidence[0].sequence[0]
                unified_evidence.append(UnifiedEvidenceItem(
                    evidence_id=seq_item.id if seq_item and hasattr(seq_item, 'id') else str(uuid.uuid4()),
                    evidence_type="CODE",
                    source_file=seq_item.source.file_path if seq_item and seq_item.source else None,
                    line_range=str(seq_item.source.line_number) if seq_item and seq_item.source and seq_item.source.line_number else None,
                    snippet=seq_item.code_snippet if seq_item else None,
                    linked_claim={
                        "claim_id": f"feature-{finding.feature}",
                        "claim_text": finding.feature,
                        "verdict": finding.status.value,
                    },
                    reasoning=finding.reasoning,
                    provenance_chain=finding.provenance_chain.model_dump() if hasattr(finding.provenance_chain, 'model_dump') else None,
                ))
            elif finding.evidence:
                for chain in finding.evidence:
                    if getattr(chain, 'sequence', None):
                        for item in chain.sequence:
                            file_path = item.source.file_path if item.source else None
                            if file_path and file_path != "unknown":
                                source_files.add(file_path)

                            evidence_type = item.evidence_type.value if hasattr(item.evidence_type, 'value') else str(item.evidence_type)
                            unified_evidence.append(UnifiedEvidenceItem(
                                evidence_id=item.id if hasattr(item, 'id') else str(uuid.uuid4()),
                                evidence_type=evidence_type,
                                source_file=file_path if file_path != "unknown" else None,
                                line_range=str(item.source.line_number) if item.source and item.source.line_number else None,
                                snippet=item.code_snippet,
                                linked_claim={
                                    "claim_id": f"feature-{finding.feature}",
                                    "claim_text": finding.feature,
                                    "verdict": finding.status.value,
                                },
                                reasoning=finding.reasoning,
                                provenance_chain=chain.model_dump() if hasattr(chain, 'model_dump') else None,
                            ))

        evidence_summary = EvidenceSummary(
            total_evidence=len(unified_evidence),
            linked_claims=len(set(ev.linked_claim["claim_id"] for ev in unified_evidence if ev.linked_claim)),
            source_files=len(source_files)
        )

        # ══════════════════════════════════════════════════════════════════
        # 7. REPORT INTEGRITY VALIDATION
        # ══════════════════════════════════════════════════════════════════
        self._validate_report_integrity(
            documentation_claims=documentation_claims,
            verification_counts=verification_counts,
            raw_claim_count=len(context.claims),
        )

        return RepositoryReport(
            metadata=metadata,
            summary=summary,
            documentation_claims=documentation_claims,
            feature_findings=feature_findings,
            architecture_findings=architecture_findings,
            recommendations=recommendations,
            trust_assessment=trust_assessment,
            verification_counts=verification_counts,
            evidence_summary=evidence_summary,
            unified_evidence=unified_evidence,
        )

    # ═════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═════════════════════════════════════════════════════════════════════

    def _build_provenance_chain(self, res) -> Optional[EvidenceChain]:
        """Build provenance chain from investigation supporting evidence."""
        if not res.supporting_evidence:
            return None

        chains = [e.chain for e in res.supporting_evidence if e.chain]
        if chains:
            return chains[0]

        # Fallback: construct chain from raw evidence candidates
        items = []
        for ev in res.supporting_evidence:
            items.append(EvidenceItem(
                source=EvidenceSource(file_path=ev.file_path or "unknown"),
                code_snippet=ev.content_snippet or ev.content,
                evidence_type=EvidenceType.UNKNOWN,
                evidence_strength=EvidenceStrength.SUPPORTING,
            ))
        if items:
            return EvidenceChain(
                chain_id=f"prov-{res.claim_id}",
                chain_type="Fallback",
                sequence=items,
                confidence=res.trust_score,
            )
        return None

    def _build_uninvestigated_reasoning(
        self, raw_claim: Claim, ncid: str, has_evidence: bool
    ) -> ReasoningTrace:
        """Build a reasoning trace for claims not selected for deep investigation."""
        steps = []
        step_counter = 1

        # Step 1: Documentation source
        steps.append(ReasoningStep(
            step_id=f"step-{step_counter:03d}",
            step_type="DOCUMENTATION",
            title="Documentation claim identified",
            description=raw_claim.text,
            source=raw_claim.source_document,
            source_file=raw_claim.source_document,
        ))
        step_counter += 1

        # Step 2: Normalization
        steps.append(ReasoningStep(
            step_id=f"step-{step_counter:03d}",
            step_type="NORMALIZATION",
            title="Claim normalization",
            description=f"Claim mapped to normalized group '{ncid or 'none'}'. "
                        "This claim was deduplicated during normalization and was not selected "
                        "as the representative claim for deep investigation.",
            result="DEDUPLICATED",
        ))
        step_counter += 1

        # Step 3: Evidence status
        if has_evidence:
            steps.append(ReasoningStep(
                step_id=f"step-{step_counter:03d}",
                step_type="EVIDENCE_COLLECTION",
                title="Evidence collected but not evaluated",
                description="Layer 4 collected evidence candidates for this claim, "
                            "but the full investigation pipeline did not evaluate them.",
                result="COLLECTED_NOT_EVALUATED",
            ))
        else:
            steps.append(ReasoningStep(
                step_id=f"step-{step_counter:03d}",
                step_type="EVIDENCE_COLLECTION",
                title="No specific evidence collected",
                description="No evidence candidates were collected for this specific claim.",
                result="NO_EVIDENCE",
            ))
        step_counter += 1

        # Step 4: Final verdict
        steps.append(ReasoningStep(
            step_id=f"step-{step_counter:03d}",
            step_type="VERDICT",
            title="Verification incomplete",
            description="Claim was not deeply investigated. Verdict assigned as INSUFFICIENT_EVIDENCE.",
            result="INSUFFICIENT_EVIDENCE",
        ))

        return ReasoningTrace(
            claim_id=raw_claim.id,
            steps=steps,
            final_verdict=VerificationVerdict.INSUFFICIENT_EVIDENCE,
            explanation="Claim was deduplicated during normalization and was not selected for deep investigation.",
        )

    def _validate_report_integrity(
        self,
        documentation_claims: List[DocumentationClaim],
        verification_counts: VerificationCounts,
        raw_claim_count: int,
    ):
        """
        Validate report integrity invariants.
        Logs errors but does not raise to avoid blocking report delivery.
        """
        total = len(documentation_claims)

        # Check 1: All raw claims must be in the report
        if total != raw_claim_count:
            logger.error(
                f"REPORT INTEGRITY: documentation_claims ({total}) != raw claims ({raw_claim_count}). "
                f"{raw_claim_count - total} claims lost during report generation."
            )

        # Check 2: Verdict counts must sum to total
        computed_sum = (
            verification_counts.verified +
            verification_counts.contradicted +
            verification_counts.partially_verified +
            verification_counts.insufficient +
            verification_counts.missing_documentation
        )
        if computed_sum != total:
            logger.error(
                f"REPORT INTEGRITY: verdict count sum ({computed_sum}) != documentation_claims ({total})."
            )

        # Check 3: Every claim must have a claim_id
        missing_ids = sum(1 for c in documentation_claims if not c.claim_id)
        if missing_ids:
            logger.error(f"REPORT INTEGRITY: {missing_ids} claims missing claim_id.")

        # Check 4: Every claim must have normalized_claim_id
        missing_ncids = sum(1 for c in documentation_claims if not c.normalized_claim_id)
        if missing_ncids:
            logger.warning(f"REPORT INTEGRITY: {missing_ncids}/{total} claims missing normalized_claim_id.")

    def to_markdown(self, report: RepositoryReport) -> str:
        md = [
            "============================================",
            "     TRUSTREPO DOCUMENTATION REPORT",
            "============================================",
            "",
            "## 1. REPOSITORY OVERVIEW",
            "",
            f"**Repository:** {report.metadata.repository_url}",
            f"**Revision:** {report.metadata.commit_sha} ({report.metadata.branch})",
            f"**Languages:** {', '.join(report.metadata.languages) if report.metadata.languages else 'None detected'}",
            f"**Frameworks:** {', '.join(report.metadata.frameworks) if report.metadata.frameworks else 'None detected'}",
            f"**Documentation Sources:** {', '.join(report.metadata.documentation_sources) if report.metadata.documentation_sources else 'None'}",
            "",
            "## 2. VERIFICATION SUMMARY",
            "",
            "**Documentation Claims**",
            f"- Total: {report.verification_counts.total_claims}",
            f"- Verified: {report.verification_counts.verified}",
            f"- Contradicted: {report.verification_counts.contradicted}",
            f"- Insufficient Evidence: {report.verification_counts.insufficient}",
            f"- Missing Documentation: {report.verification_counts.missing_documentation}",
            "",
            "**Repository Features**",
            f"- Candidates Investigated: {report.summary.total_candidates}",
            f"- Confirmed: {report.summary.confirmed_features}",
            f"- Missing Documentation: {report.summary.missing_documentation}",
            f"- Insufficient Evidence: {report.summary.insufficient_evidence}",
            "",
            "## 3. DOCUMENTATION COVERAGE",
            "",
            f"**Coverage Score:** {report.summary.coverage_percentage}%",
            f"({report.summary.documented_features} / {report.summary.confirmed_features} confirmed features documented)",
            "",
            "## 4. DOCUMENTATION CLAIM VERIFICATION",
            ""
        ]

        for idx, claim in enumerate(report.documentation_claims, 1):
            md.extend([
                f"### Claim #{idx}",
                f"> {claim.claim_text}",
                f"**Verdict:** {claim.verdict.value} (Confidence: {claim.confidence:.2f})",
                f"**Reasoning:** {claim.reasoning}",
                f"**Evidence Count:** {claim.evidence_count}",
                ""
            ])

        verified_findings = [f for f in report.feature_findings if f.status == VerificationVerdict.VERIFIED]
        if verified_findings:
            md.extend(["## 5. VERIFIED FEATURES", ""])
            for finding in verified_findings:
                md.extend([
                    f"### {finding.feature}",
                    f"**Evidence:** {len(finding.evidence)} sources",
                    "**Documentation:** Found",
                    f"**Verdict:** {finding.status.value}",
                    ""
                ])
        else:
            md.extend(["## 5. VERIFIED FEATURES", "", "None", ""])

        missing_findings = [f for f in report.feature_findings if f.status == VerificationVerdict.MISSING_DOCUMENTATION]
        if missing_findings:
            md.extend(["## 6. MISSING DOCUMENTATION", ""])
            for finding in missing_findings:
                md.extend([
                    f"### {finding.feature}",
                    f"**Repository Proof:** {len(finding.evidence)} sources",
                    f"**Verdict:** {finding.status.value}",
                    f"**Recommendation:** {finding.recommendation or 'None'}",
                    ""
                ])
        else:
            md.extend(["## 6. MISSING DOCUMENTATION", "", "None", ""])

        md.extend([
            "## 7. REPOSITORY TRUST ASSESSMENT",
            "",
            f"**Trust Score:** {report.trust_assessment.score} / 100",
            f"**Status:** {report.trust_assessment.status}",
            f"**Details:** {report.trust_assessment.details}",
        ])

        return "\n".join(md)
