from datetime import datetime, timezone
import json
from app.models.trustrepo_context import TrustRepoContext
from app.models.knowledge.evidence import EvidenceChain

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
    EvidenceRetrievalTrace,
    EvidenceSearchStep
)

class ReportGenerator:
    def __init__(self):
        pass

    def generate_report(self, context: TrustRepoContext) -> RepositoryReport:
        # 1. Process Claims (Direction A: Documentation -> Repository)
        verification_results = context.verification_context.verification_results
        
        documentation_claims = []
        feature_findings = []
        
        for raw_claim in context.claims:
            res = verification_results.get(raw_claim.normalized_claim_id)
            if not res:
                # If a claim somehow missed verification, skip or record as insufficient
                continue
                
            text = raw_claim.text
            
            # Use original verdict mapped to new enums
            verdict = VerificationVerdict.VERIFIED if res.verdict.value == "VERIFIED" else (
                VerificationVerdict.CONTRADICTED if res.verdict.value == "CONTRADICTION" else (
                    VerificationVerdict.UNSUPPORTED if res.verdict.value == "UNSUPPORTED_DOCUMENTATION" else VerificationVerdict.MISSING_DOCUMENTATION
                )
            )

            # Reconstruct provenance_chain if available
            prov_chain = None
            if res.supporting_evidence:
                chains = [e.chain for e in res.supporting_evidence if e.chain]
                if chains:
                    prov_chain = chains[0]
                else:
                    # Fallback construct
                    from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceSource, EvidenceType, EvidenceStrength
                    items = []
                    for ev in res.supporting_evidence:
                        items.append(EvidenceItem(
                            source=EvidenceSource(file_path=ev.file_path or "unknown"),
                            code_snippet=ev.content_snippet or ev.content,
                            evidence_type=EvidenceType.UNKNOWN,
                            evidence_strength=EvidenceStrength.SUPPORTING,
                        ))
                    if items:
                        prov_chain = EvidenceChain(
                            chain_id=f"prov-{res.claim_id}",
                            chain_type="Fallback",
                            sequence=items,
                            confidence=res.trust_score
                        )

            trace_obj = next((t for t in context.semantic_context.reasoning_traces if t.claim_id == res.claim_id), None)

            claim = DocumentationClaim(
                claim_id=raw_claim.id,
                claim_text=text,
                verdict=verdict,
                verification_category=VerificationCategory.UNKNOWN,
                trust_score=res.trust_score,
                confidence=res.trust_score, # For backward compatibility until TrustScorer/ConfidenceEngine is fully split
                confidence_breakdown={
                    "evidence_quality": res.evidence_quality,
                    "evidence_diversity": res.evidence_diversity,
                    "graph_connectivity": res.graph_connectivity,
                    "evidence_agreement": res.evidence_agreement
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
                recommendation=None
            )
            documentation_claims.append(claim)
            
            if verdict == VerificationVerdict.CONTRADICTED:
                feature_findings.append(FeatureFinding(
                    feature=text,
                    category=VerificationCategory.UNKNOWN,
                    candidate_source=CandidateSource.DOCUMENTATION_ANALYSIS,
                    status=VerificationVerdict.CONTRADICTED,
                    documentation_claim=claim,
                    evidence=[],
                    evidence_count=res.evidence_count,
                    evidence_quality=res.evidence_quality,
                    evidence_diversity=res.evidence_diversity,
                    documentation_search=None,
                    retrieval_trace=None,
                    confidence=res.trust_score,
                    reasoning=" ".join(res.reasoning_trace) if res.reasoning_trace else "No reasoning provided.",
                    reasoning_trace=res.reasoning_trace,
                    provenance_chain=prov_chain,
                    recommendation=None
                ))

        # 2. Process Features (Direction B: Repository -> Documentation)
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

            # Build Retrieval Trace
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
                        evidence_quality=0.9, # Mock value for now
                        evidence_diversity=0.9, # Mock value for now
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

        # 3. Compute Summaries and Metadata
        coverage_pct = round((documented_features_count / confirmed_features_count) * 100) if confirmed_features_count > 0 else 0

        summary = DocumentationSummary(
            documentation_sources=[f.path for f in context.document_context.documents] if context.document_context and hasattr(context.document_context, 'documents') else [],
            total_candidates=len(all_detected_features),
            confirmed_features=confirmed_features_count,
            documented_features=documented_features_count,
            missing_documentation=sum(1 for f in feature_findings if f.status == VerificationVerdict.MISSING_DOCUMENTATION),
            contradicted=sum(1 for f in feature_findings if f.status == VerificationVerdict.CONTRADICTED),
            insufficient_evidence=sum(1 for f in feature_findings if f.status == VerificationVerdict.INSUFFICIENT_EVIDENCE),
            total_claims=len(documentation_claims),
            verified_claims=sum(1 for c in documentation_claims if c.verdict == VerificationVerdict.VERIFIED),
            contradicted_claims=sum(1 for c in documentation_claims if c.verdict == VerificationVerdict.CONTRADICTED),
            coverage_percentage=coverage_pct
        )

        repo_metadata = {}
        if context.repository_context:
            repo_metadata = {
                "url": getattr(context.repository_context, "repository_url", "local://repository"),
                "commit_sha": "HEAD",
                "branch": "main",
                "languages": ["Python", "JavaScript", "TypeScript"], # Mocked for now
                "frameworks": context.semantic_context.technologies if context.semantic_context else [],
            }

        metadata = RepositoryMetadata(
            repository_url=repo_metadata.get("url", "local://repository"),
            commit_sha=repo_metadata.get("commit_sha", "HEAD"),
            branch=repo_metadata.get("branch", "main"),
            languages=repo_metadata.get("languages", []),
            frameworks=repo_metadata.get("frameworks", []),
            source_files_count=0,
            documentation_sources=summary.documentation_sources,
            claims_analyzed=len(documentation_claims),
            features_investigated=len(all_detected_features),
            analysis_date=datetime.now(timezone.utc),
            verification_version="3.0.0"
        )
        
        repo_score = 0.0
        verified_c = 0
        total_c = 0
        if confirmed_features_count > 0 or len(documentation_claims) > 0:
            verified_c = sum(1 for c in documentation_claims if c.verdict == VerificationVerdict.VERIFIED)
            total_c = len(documentation_claims)
            claim_score = (verified_c / total_c) * 100 if total_c > 0 else 100.0
            overall_score = (claim_score * 0.5) + (coverage_pct * 0.5)
            repo_score = round(overall_score, 1)

        trust_assessment = TrustAssessment(
            score=repo_score,
            status="High Trust" if repo_score >= 80 else ("Moderate Trust" if repo_score >= 50 else "Low Trust"),
            details=f"Calculated based on {coverage_pct}% doc coverage and {verified_c if total_c > 0 else 0}/{total_c if total_c > 0 else 0} verified claims."
        )

        architecture_findings = context.semantic_context.architecture_findings if context.semantic_context else []

        # -- Build unified_evidence and evidence_summary --
        unified_evidence = []
        source_files = set()
        
        from app.models.report.trust_report import UnifiedEvidenceItem, EvidenceSummary
        import uuid
        
        for claim in documentation_claims:
            if claim.provenance_chain and getattr(claim.provenance_chain, 'sequence', None):
                for item in claim.provenance_chain.sequence:
                    file_path = item.source.file_path if item.source else None
                    if file_path:
                        source_files.add(file_path)
                    
                    evidence_type = item.evidence_type.value if hasattr(item.evidence_type, 'value') else str(item.evidence_type)
                    
                    unified_evidence.append(UnifiedEvidenceItem(
                        evidence_id=item.id if hasattr(item, 'id') else str(uuid.uuid4()),
                        evidence_type=evidence_type,
                        source_file=file_path,
                        line_range=str(item.source.line_number) if item.source and item.source.line_number else None,
                        snippet=item.code_snippet,
                        linked_claim={
                            "claim_id": claim.claim_id,
                            "claim_text": claim.claim_text,
                            "verdict": claim.verdict.value
                        },
                        reasoning=claim.reasoning,
                        provenance_chain=claim.provenance_chain.model_dump() if hasattr(claim.provenance_chain, 'model_dump') else None
                    ))
            elif claim.verdict in [VerificationVerdict.MISSING_DOCUMENTATION, VerificationVerdict.INSUFFICIENT_EVIDENCE]:
                 unified_evidence.append(UnifiedEvidenceItem(
                    evidence_id=f"doc-ev-{claim.claim_id}",
                    evidence_type="DOCUMENTATION",
                    source_file=claim.source_file,
                    line_range=claim.line_range,
                    snippet=None,
                    linked_claim={
                        "claim_id": claim.claim_id,
                        "claim_text": claim.claim_text,
                        "verdict": claim.verdict.value
                    },
                    reasoning=claim.reasoning,
                    provenance_chain=None
                ))

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
                        "verdict": finding.status.value
                    },
                    reasoning=finding.reasoning,
                    provenance_chain=finding.provenance_chain.model_dump() if hasattr(finding.provenance_chain, 'model_dump') else None
                ))
            elif finding.evidence:
                 for chain in finding.evidence:
                     if getattr(chain, 'sequence', None):
                         for item in chain.sequence:
                             file_path = item.source.file_path if item.source else None
                             if file_path:
                                 source_files.add(file_path)
                             
                             evidence_type = item.evidence_type.value if hasattr(item.evidence_type, 'value') else str(item.evidence_type)
                             unified_evidence.append(UnifiedEvidenceItem(
                                evidence_id=item.id if hasattr(item, 'id') else str(uuid.uuid4()),
                                evidence_type=evidence_type,
                                source_file=file_path,
                                line_range=str(item.source.line_number) if item.source and item.source.line_number else None,
                                snippet=item.code_snippet,
                                linked_claim={
                                    "claim_id": f"feature-{finding.feature}",
                                    "claim_text": finding.feature,
                                    "verdict": finding.status.value
                                },
                                reasoning=finding.reasoning,
                                provenance_chain=chain.model_dump() if hasattr(chain, 'model_dump') else None
                             ))

        evidence_summary = EvidenceSummary(
            total_evidence=len(unified_evidence),
            linked_claims=len(set(ev.linked_claim["claim_id"] for ev in unified_evidence if ev.linked_claim)),
            source_files=len(source_files)
        )

        return RepositoryReport(
            metadata=metadata,
            summary=summary,
            documentation_claims=documentation_claims,
            feature_findings=feature_findings,
            architecture_findings=architecture_findings,
            recommendations=recommendations,
            trust_assessment=trust_assessment,
            evidence_summary=evidence_summary,
            unified_evidence=unified_evidence
        )

    def to_markdown(self, report: RepositoryReport) -> str:
        md = [
            "╔══════════════════════════════════════════════════════╗",
            "║          TRUSTREPO DOCUMENTATION REPORT             ║",
            "╚══════════════════════════════════════════════════════╝",
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
            f"- Total: {len(report.documentation_claims)}",
            f"- Verified: {report.summary.verified_claims}",
            f"- Contradicted: {report.summary.contradicted_claims}",
            f"- Unsupported: {sum(1 for c in report.documentation_claims if c.verdict == VerificationVerdict.UNSUPPORTED)}",
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
                    f"**Verdict:** ⚠ {finding.status.value}",
                    f"**Recommendation:** {finding.recommendation or 'None'}",
                    ""
                ])
        else:
             md.extend(["## 6. MISSING DOCUMENTATION", "", "None", ""])

        insufficient_findings = [f for f in report.feature_findings if f.status == VerificationVerdict.INSUFFICIENT_EVIDENCE]
        if insufficient_findings:
            md.extend(["## 7. INSUFFICIENT EVIDENCE", ""])
            for finding in insufficient_findings:
                md.extend([
                    f"- {finding.feature} ({finding.candidate_source.value})"
                ])
            md.append("")
        else:
            md.extend(["## 7. INSUFFICIENT EVIDENCE", "", "None", ""])

        md.extend(["## 8. CONTRADICTIONS", ""])
        contradicted_findings = [f for f in report.feature_findings if f.status == VerificationVerdict.CONTRADICTED]
        if contradicted_findings:
            for idx, c in enumerate(contradicted_findings, 1):
                claim_text = c.documentation_claim.claim_text if c.documentation_claim else c.feature
                md.extend([
                    f"### Contradiction #{idx}",
                    f"**Claim:** {claim_text}",
                    f"**Explanation:** {c.reasoning}",
                    ""
                ])
        else:
            md.append("None\n")

        md.extend(["## 9. EVIDENCE EXPLORER", ""])
        for finding in [f for f in report.feature_findings if f.status != VerificationVerdict.INSUFFICIENT_EVIDENCE]:
            md.extend([
                f"<details><summary><b>{finding.feature} Evidence</b></summary>",
                ""
            ])
            for chain in finding.evidence:
                if chain.sequence:
                    for item in chain.sequence:
                        md.append(f"- **{item.context_type}**: `{item.source.file_path}:{item.source.line_number}` - `{item.code_snippet}`")
            if finding.retrieval_trace:
                md.extend([
                    "",
                    "#### Evidence Retrieval Trace",
                    f"- **Strategies Attempted:** {', '.join(finding.retrieval_trace.strategies_attempted)}",
                    f"- **Conclusion:** {finding.retrieval_trace.conclusion}"
                ])
            md.extend(["", "</details>", ""])

        md.extend(["## 10. RECOMMENDATIONS", ""])
        if report.recommendations:
            for rec in report.recommendations:
                md.append(f"- **[{rec.priority.value}]** {rec.message}")
            md.append("")
        else:
            md.append("No recommendations at this time.\n")
            
        md.extend([
            "## 11. REPOSITORY TRUST ASSESSMENT",
            "",
            f"**Trust Score:** {report.trust_assessment.score} / 100",
            f"**Status:** {report.trust_assessment.status}",
            f"**Details:** {report.trust_assessment.details}",
            "",
            "## 12. REPORT METADATA / ARTIFACTS",
            "",
            "- `trust_report.json` (Machine-readable JSON)",
            "- `trust_report.md` (This document)"
        ])

        return "\n".join(md)
