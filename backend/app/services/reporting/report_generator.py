from typing import List, Dict, Any
from datetime import datetime, timezone
from app.models.knowledge.investigation import VerificationResult, VerificationVerdict
from app.models.report.trust_report import (
    RepositoryTrustReport, 
    RepositorySummary, 
    ClaimReport, 
    UndocumentedFeature, 
    DocumentationCoverage,
    Recommendation,
    RecommendationPriority,
    VerificationCategory
)
from app.services.reporting.explanation_generator import ExplanationGenerator
from app.models.trustrepo_context import TrustRepoContext
from app.models.knowledge.evidence import EvidenceChain

class ReportGenerator:
    def __init__(self):
        self.explanation_gen = ExplanationGenerator()
        
    def generate_report(self, context: TrustRepoContext) -> RepositoryTrustReport:
        results = list(context.verification_context.verification_results.values())
        claim_texts = {c.id: c.text for c in context.claims}
        
        claim_reports = []
        verified_count = 0
        refuted_count = 0
        insufficient_count = 0
        total_trust = 0.0
        
        for res in results:
            text = claim_texts.get(res.claim_id, "Unknown Claim")
            report = self.explanation_gen.generate(res, text)
            claim_reports.append(report)
            
            if res.verdict == VerificationVerdict.VERIFIED:
                verified_count += 1
            elif res.verdict == VerificationVerdict.REFUTED:
                refuted_count += 1
            else:
                insufficient_count += 1
                
            total_trust += res.trust_score
            
        total_claims = len(results)
        
        raw_doc_text = ""
        if context.document_context and hasattr(context.document_context, 'documents'):
            raw_doc_text = " ".join([d.content for d in context.document_context.documents]).lower()
            
        repo_metadata = {}
        if context.repository_context:
            repo_metadata = {
                "url": getattr(context.repository_context, "repository_url", "local://repository"),
                "commit_sha": "HEAD",
                "branch": "main",

                "technologies": context.semantic_context.technologies if context.semantic_context else [],
                "architecture": context.semantic_context.architectures if context.semantic_context else [],
                "capabilities": context.semantic_context.capabilities if context.semantic_context else []
            }
            
        undocumented_features = []
        recommendations = []
        
        detected_techs = context.semantic_context.technologies
        detected_caps = context.semantic_context.capabilities
        detected_arch = context.semantic_context.architectures
        detected_features_list = context.semantic_context.features
        
        # Combine all features detected in code to check against documentation
        all_detected_features = []
        all_detected_features.extend(detected_techs)
        all_detected_features.extend(detected_caps)
        all_detected_features.extend(detected_arch)
        all_detected_features.extend(detected_features_list)
        all_detected_features = list(set(all_detected_features))
        
        # Pull evidence chains from canonical location
        evidence_chains = context.semantic_context.evidence_chains or []
        
        documented_features_count = 0
        
        for feature in all_detected_features:
            if not feature or feature == "Unknown":
                continue
                
            # Find evidence chain for this feature
            feature_chain = None
            for chain in evidence_chains:
                if feature in chain.chain_type:
                    feature_chain = chain
                    break
                    
            # CODE INTELLIGENCE MODE: If there's no documentation OR the feature isn't in it, it's missing.
            if not raw_doc_text or feature.lower() not in raw_doc_text:
                reason = "AST parser identified evidence in code. Knowledge Graph links this to feature. Documentation lacks mention."
                if feature_chain:
                    reason = feature_chain.reasoning_trace
                elif not raw_doc_text:
                    reason = "No repository documentation found. Feature was reverse-engineered from source code (Code Intelligence Mode)."
                    
                undoc = UndocumentedFeature(
                    feature_name=feature,
                    evidence_chain=feature_chain,
                    reason=reason,
                    documentation_analysis=f"- Expected: {feature}\n- Observed: Missing in Docs",
                    verdict="Missing Documentation",
                    confidence=feature_chain.confidence if feature_chain else 0.8,
                    recommendation=f"Document the usage of {feature}."
                )
                undocumented_features.append(undoc)
                
                recommendations.append(Recommendation(
                    priority=RecommendationPriority.MEDIUM,
                    message=f"Missing Documentation: {feature} is detected in code but not documented."
                ))
            else:
                documented_features_count += 1
                
        for cr in claim_reports:
            if cr.verdict == VerificationVerdict.REFUTED:
                recommendations.append(Recommendation(
                    priority=RecommendationPriority.HIGH,
                    message=f"Contradiction: Update documentation stating '{cr.claim_text}' to reflect actual implementation."
                ))
        
        detected_count = len(all_detected_features)
        coverage_pct = round((documented_features_count / detected_count) * 100) if detected_count > 0 else 0
        
        doc_coverage = DocumentationCoverage(
            detected_features=detected_count,
            documented_features=documented_features_count,
            verified_features=verified_count,
            contradicted_features=refuted_count,
            missing_features=len(undocumented_features),
            coverage_percentage=coverage_pct
        )
        
        from app.services.verification.trust_scorer import TrustScorer
        scorer = TrustScorer()
        
        all_quality = [r.trust_score / 100.0 for r in results if r.trust_score > 0]
        avg_evidence_quality = sum(all_quality) / len(all_quality) if all_quality else 0.0
        
        claim_coverage_pct = (len(results) / max(total_claims, 1)) * 100.0
        
        # Compute multi-dimensional scores for TrustScorer
        doc_score = coverage_pct
        tech_score = 100.0 if detected_techs else 0.0
        feature_score = min(len(detected_features_list) * 10.0, 100.0)
        capability_score = min(len(detected_caps) * 20.0, 100.0)
        architecture_score = 100.0 if detected_arch and "Unknown" not in detected_arch else 50.0
        evidence_score = avg_evidence_quality * 100.0
        verification_score = (verified_count / max(total_claims, 1)) * 100.0
        
        # Graph score based on graph analytics
        graph_analytics = context.graph_context.analytics
        graph_score = 50.0
        if graph_analytics:
            has_cycles = graph_analytics.get("cycle_detected", True)
            graph_score = 50.0 if has_cycles else 100.0
        
        global_score = scorer.calculate_repository_score(
            doc_score=doc_score,
            tech_score=tech_score,
            feature_score=feature_score,
            capability_score=capability_score,
            architecture_score=architecture_score,
            evidence_score=evidence_score,
            verification_score=verification_score,
            graph_score=graph_score
        )
        
        status = "Highly Consistent"
        if global_score < 50:
            status = "Inconsistent"
        elif global_score < 80:
            status = "Needs Improvement"
            
        summary = RepositorySummary(
            repository_url=repo_metadata.get("url", "local://repository"),
            commit_sha=repo_metadata.get("commit_sha", "HEAD"),
            branch=repo_metadata.get("branch", "main"),
            technologies=repo_metadata.get("technologies", []),
            architecture=repo_metadata.get("architecture", []),
            capabilities=repo_metadata.get("capabilities", []),
            total_claims=total_claims,
            verified_claims=verified_count,
            refuted_claims=refuted_count,
            insufficient_claims=insufficient_count,
            repository_trust_score=global_score,
            status=status,
            verification_version="2.0.0",
            verification_timestamp=datetime.now(timezone.utc)
        )
        
        return RepositoryTrustReport(
            summary=summary, 
            claim_reports=claim_reports,
            undocumented_features=undocumented_features,
            coverage=doc_coverage,
            recommendations=recommendations
        )
        
    def to_markdown(self, report: RepositoryTrustReport) -> str:
        md = [
            "# TrustRepo Verification Report",
            "",
            "## Repository Information",
            "",
            "```",
            f"Repository URL    : {report.summary.repository_url}",
            f"Branch            : {report.summary.branch}",
            f"Commit            : {report.summary.commit_sha}",
            f"Verification Date : {report.summary.verification_timestamp.strftime('%d-%b-%Y %H:%M:%S')}",
            "```",
            "",
            "---",
            "",
            "## Technology Stack Detected",
            ""
        ]
        
        if report.summary.architecture:
            md.extend(["Architecture", "------------", *report.summary.architecture, ""])
        if report.summary.technologies:
            md.extend(["Technologies", "------------", *report.summary.technologies, ""])
        if getattr(report.summary, 'capabilities', []):
            md.extend(["Detected Capabilities", "---------------------", *report.summary.capabilities, ""])
            
        md.extend([
            "---",
            "",
            "# Repository Trust Score",
            "",
            "```",
            "Overall Trust Score",
            "",
            f"{report.summary.repository_trust_score} / 100",
            "",
            "Status",
            "",
            f"{report.summary.status}",
            "```",
            "",
            "---",
            "",
            "# Repository Summary",
            "",
            "```",
            f"Total Claims Extracted          : {report.summary.total_claims}",
            "",
            f"Verified Claims                 : {report.summary.verified_claims}",
            "",
            f"Contradicted Claims             : {report.summary.refuted_claims}",
            "",
            f"Missing Documentation           : {report.coverage.missing_features}",
            "",
            f"Unsupported Claims              : {report.summary.insufficient_claims}",
            "```",
            "",
            "---"
        ])
        
        verified_claims = [c for c in report.claim_reports if c.verdict == VerificationVerdict.VERIFIED]
        refuted_claims = [c for c in report.claim_reports if c.verdict == VerificationVerdict.REFUTED]
        unsupported_claims = [c for c in report.claim_reports if c.verdict == VerificationVerdict.INSUFFICIENT_EVIDENCE]
        
        def format_chain(chain: EvidenceChain) -> str:
            if not chain: return "No explicit evidence chain available."
            res = [f"- Graph Path: {chain.graph_path}"]
            for item in chain.sequence:
                res.append(f"- File: `{item.source.file_path}`")
                if item.source.line_number:
                    res.append(f"  Line: {item.source.line_number}")
                res.append(f"  Qualified Name: `{item.qualified_name}`")
                res.append(f"  Snippet: `{item.code_snippet}`")
                res.append(f"  Strength: {item.evidence_strength.value}")
            return "\n".join(res)
        
        if verified_claims:
            md.extend(["", "# Verified Claims", ""])
            for idx, c in enumerate(verified_claims, 1):
                md.extend([
                    f"## Claim {idx}",
                    "",
                    f"> {c.claim_text}",
                    "",
                    "### Evidence Trace",
                    "README → Claim → Intent → Expected Features → Evidence Query → Evidence Nodes → Reasoning → Verdict",
                    "",
                    "### Detailed Evidence",
                    format_chain(c.provenance_chain) if getattr(c, 'provenance_chain', None) else "Evidence analyzed by multi-agent reasoning.",
                    "",
                    "### Documentation Analysis",
                    "- Expected: Present",
                    "- Observed: Matched in Code",
                    "",
                    "### Verdict & Category",
                    f"✅ **{c.verdict.value}** | {c.verification_category.value}",
                    "",
                    "### Reasoning",
                    c.explanation,
                    "",
                    "Confidence",
                    "```",
                    f"{c.trust_score} / 100",
                    "```",
                    "---"
                ])
                
        if refuted_claims:
            md.extend(["", "# Contradicted Claims", ""])
            for idx, c in enumerate(refuted_claims, 1):
                md.extend([
                    f"## Contradiction {idx}",
                    "",
                    f"> {c.claim_text}",
                    "",
                    "### Evidence Trace",
                    "README → Claim → Intent → Expected Features → Evidence Query → Evidence Nodes → Reasoning → Verdict",
                    "",
                    "### Detailed Evidence",
                    format_chain(c.provenance_chain) if getattr(c, 'provenance_chain', None) else "Evidence analyzed by multi-agent reasoning.",
                    "",
                    "### Documentation Analysis",
                    "- Expected: Required by documentation",
                    "- Observed: Contradicting implementation found",
                    "",
                    "### Verdict & Category",
                    f"❌ **{c.verdict.value}** | {c.verification_category.value}",
                    "",
                    "### Reasoning",
                    c.explanation,
                    "",
                    "Confidence",
                    "```",
                    f"{c.trust_score} / 100",
                    "```",
                    "---"
                ])
                
        if report.undocumented_features:
            md.extend(["", "# Undocumented Code Features", ""])
            for uf in report.undocumented_features:
                md.extend([
                    f"### Feature: {uf.feature_name}",
                    "",
                    "#### Evidence Trace",
                    "AST → Semantic Symbols → Knowledge Graph → Evidence Retrieval → Evidence Validation → Reasoning → Verdict",
                    "",
                    "#### Detailed Evidence",
                    format_chain(uf.evidence_chain) if uf.evidence_chain else "Evidence analyzed by graph traversal.",
                    "",
                    "#### Documentation Analysis",
                    uf.documentation_analysis,
                    "",
                    "#### Verdict & Category",
                    f"**{uf.verdict}** | Structural",
                    "",
                    "#### Reasoning",
                    uf.reason,
                    "",
                    "#### Confidence",
                    f"{uf.confidence * 100}%",
                    "",
                    "#### Recommendation",
                    "```",
                    uf.recommendation,
                    "```",
                    "---"
                ])
                
        if unsupported_claims:
            md.extend(["", "# Unsupported Documentation", ""])
            for idx, c in enumerate(unsupported_claims, 1):
                md.extend([
                    f"## Unsupported {idx}",
                    f"> {c.claim_text}",
                    "",
                    "### Documentation Analysis",
                    "- Expected: Required by documentation",
                    "- Observed: Missing in implementation",
                    "",
                    "### Verdict & Category",
                    f"**Unsupported Documentation** | {c.verification_category.value}",
                    "",
                    "### Reasoning",
                    c.explanation,
                    "---"
                ])
                
        md.extend([
            "",
            "# Documentation Coverage",
            "",
            "```",
            f"Detected Features in Code    : {report.coverage.detected_features}",
            "",
            f"Documented Features          : {report.coverage.documented_features}",
            "",
            f"Verified Features            : {report.coverage.verified_features}",
            "",
            f"Contradicted Features        : {report.coverage.contradicted_features}",
            "",
            f"Missing Features             : {report.coverage.missing_features}",
            "",
            f"Coverage                     : {report.coverage.coverage_percentage}%",
            "```",
            "",
            "---",
            "",
            "# Recommendations",
            ""
        ])
        
        if report.recommendations:
            priorities = [RecommendationPriority.CRITICAL, RecommendationPriority.HIGH, RecommendationPriority.MEDIUM, RecommendationPriority.LOW]
            for p in priorities:
                recs = [r for r in report.recommendations if r.priority == p]
                if recs:
                    md.extend([f"### {p.value} Priority", ""])
                    for r in recs:
                        md.append(f"• {r.message}")
                    md.append("")
        else:
            md.append("No recommendations at this time. Repository is well-documented.")
            
        return "\n".join(md)
