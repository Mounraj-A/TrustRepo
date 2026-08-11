"""
Documentation Agent — searches raw documentation for claim evidence.
Specialization: README, docs, comments, docstrings.
"""
from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceSource, EvidenceStrength
from app.services.knowledge.semantic_registry import SEMANTIC_REGISTRY
import re


class DocumentationAgent(BaseAgent):
    """
    Searches the repository documentation (README, wikis, comments)
    for text-level evidence matching the claim's expected features and technologies.
    """
    role = AgentRole.DOCUMENTATION

    def process(self, message: AgentMessage) -> AgentMessage:
        raw_doc = message.payload.get("raw_doc_text", "")
        features = message.expected_features

        self._log(message, f"Scanning documentation for features: {features}")

        evidence_chains = []

        for feat in features:
            feature_def = SEMANTIC_REGISTRY.get_by_id(feat)
            if not feature_def:
                continue

            # Check canonical name and aliases
            search_terms = [feature_def.canonical_name] + feature_def.aliases
            found = False
            for term in search_terms:
                if found:
                    break
                pattern = re.compile(
                    r'.{0,100}' +
                    re.escape(
                        term.lower()) +
                    r'.{0,100}',
                    re.IGNORECASE)
                for match in pattern.finditer(raw_doc.lower()):
                    snippet = match.group(0).strip()

                    chain = EvidenceChain(
                        chain_id=f"doc_feat_{feat}",
                        chain_type="Documentation Match",
                        reasoning_trace=f"Documentation explicitly mentions '{term}' supporting feature '{
                            feature_def.canonical_name}'",
                        sequence=[
                            EvidenceItem(
                                source=EvidenceSource(
                                    file_path="README/Documentation"),
                                context_type="Text",
                                code_snippet=f"...{snippet[:100]}...",
                                evidence_strength=EvidenceStrength.SECONDARY
                            )
                        ]
                    )
                    evidence_chains.append(chain)
                    found = True
                    break  # One match per feature is enough

        message.evidence.extend(evidence_chains)
        message.payload["doc_evidence"] = [e.dict() for e in evidence_chains]
        message.confidence = min(
            0.2 + (len(evidence_chains) * 0.15), 0.85) if evidence_chains else 0.05
        self._log(
            message, f"Found {
                len(evidence_chains)} documentation evidence chains.")

        message.route_to_next()
        return message
