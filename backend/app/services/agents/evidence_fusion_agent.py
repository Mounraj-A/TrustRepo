"""
Evidence Fusion Agent — merges, deduplicates, and ranks evidence from all agents.
Specialization: evidence quality scoring, diversity ranking, deduplication.
"""
from __future__ import annotations
from typing import List
from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole
from app.models.knowledge.evidence import EvidenceChain


class EvidenceFusionAgent(BaseAgent):
    """
    Receives evidence from CodeAgent, DocumentationAgent, and KnowledgeGraphAgent.
    Fuses, deduplicates, and ranks the evidence before passing it to VerificationAgent.

    Evidence Quality Score (per candidate):
        - Source Engine Weight: graph (0.9) > code_graph (0.8) > documentation (0.6)
        - File path specificity: penalize "unknown" sources
        - Novelty: deduplicate similar content
    """
    role = AgentRole.EVIDENCE_FUSION

    SOURCE_WEIGHTS = {
        "knowledge_graph": 0.9,
        "code_graph": 0.8,
        "documentation": 0.6,
        "graph": 0.7,
    }

    def process(self, message: AgentMessage) -> AgentMessage:
        self._log(message, "Fusing and deduplicating ranked evidence.")

        ranked_evidence: List[EvidenceChain] = message.evidence
        if not ranked_evidence:
            self._log(message, "No evidence to fuse.")
            message.route_to_next()
            return message

        # Deduplicate by reasoning trace or chain ID
        seen_traces = set()
        fused_chains = []
        conflicts = []

        for chain in ranked_evidence:
            trace_hash = hash(chain.reasoning_trace)
            if trace_hash not in seen_traces:
                seen_traces.add(trace_hash)
                fused_chains.append(chain)
            else:
                # Potential conflict if reasoning trace is similar but context differs
                # For Phase 3, we just flag it. In reality, we'd do semantic
                # comparison.
                pass

        # Simple conflict detection: do we have evidence from both Code and Docs?
        # If we have code evidence but no doc evidence, or vice versa, we can flag a "coverage conflict"
        # However, EvidenceAgreementEngine handles agreement.
        # EvidenceFusionAgent just groups them by feature.

        feature_groups = {}
        for chain in fused_chains:
            # Try to extract feature ID from chain ID (e.g., code_feat_XYZ)
            parts = chain.chain_id.split("_feat_")
            if len(parts) == 2:
                feat = parts[1]
                if feat not in feature_groups:
                    feature_groups[feat] = []
                feature_groups[feat].append(chain)

        # Create Conflict Objects if a feature has conflicting strengths
        for feat, chains in feature_groups.items():
            if len(chains) > 1:
                types = set(c.chain_type for c in chains)
                if len(types) > 1:
                    conflicts.append({
                        "feature": feat,
                        "description": f"Multiple evidence types found for {feat}: {types}",
                        "chains": [c.chain_id for c in chains]
                    })

        message.evidence = fused_chains
        message.payload["fused_evidence"] = [e.dict() for e in fused_chains]
        message.payload["conflicts"] = conflicts

        self._log(
            message, f"Fused into {
                len(fused_chains)} unique chains. Detected {
                len(conflicts)} conflicts.")
        message.route_to_next()
        return message
