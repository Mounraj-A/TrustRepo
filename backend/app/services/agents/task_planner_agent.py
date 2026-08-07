"""
Task Planner Agent — the central coordinator of the multi-agent system.

Architecture:
                     Claim (NormalizedClaim)
                           │
                           ▼
                 Task Planner Agent
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      Code Agent    Docs Agent       Graph Agent
          └────────────────┼────────────────┘
                           ▼
                 Evidence Fusion Agent
                           ▼
               (message returned to pipeline)

The planner:
1. Decomposes the claim into sub-tasks for each specialized agent.
2. Dispatches tasks to agents concurrently (or sequentially here for reliability).
3. Aggregates all agent responses into a single fused message.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole, MessageType
from app.services.agents.code_agent import CodeAgent
from app.services.agents.documentation_agent import DocumentationAgent
from app.services.agents.knowledge_graph_agent import KnowledgeGraphAgent
from app.services.agents.evidence_ranking_agent import EvidenceRankingAgent
from app.services.agents.evidence_fusion_agent import EvidenceFusionAgent
from app.services.agents.evidence_validation_agent import EvidenceValidationAgent
from app.services.agents.evidence_agreement_engine import EvidenceAgreementEngine
from app.services.agents.coverage_agent import CoverageAgent
from app.services.agents.contradiction_agent import ContradictionAgent
from app.services.agents.reasoning_agent import ReasoningAgent
from app.services.agents.decision_matrix import DecisionMatrix
from app.services.agents.verification_agent import VerificationAgent
from app.services.agents.recommendation_engine import RecommendationEngine
from app.services.agents.llm_explanation_agent import LLMExplanationAgent
from app.services.verification.intent_resolver import IntentResolver

if TYPE_CHECKING:
    from app.models.claim import Claim


class TaskPlannerAgent(BaseAgent):
    """
    Central coordinator. Receives a NormalizedClaim, dispatches to 3 specialized
    agents in parallel, then fuses results via EvidenceFusionAgent.
    
    Returns a single enriched AgentMessage ready for the VerificationEngine.
    """
    role = AgentRole.TASK_PLANNER

    def __init__(self, raw_doc_text: str = ""):
        self.intent_resolver = IntentResolver()
        self.code_agent = CodeAgent()
        self.docs_agent = DocumentationAgent()
        self.graph_agent = KnowledgeGraphAgent()
        
        self.ranking_agent = EvidenceRankingAgent()
        self.fusion_agent = EvidenceFusionAgent()
        self.validation_agent = EvidenceValidationAgent()
        self.agreement_engine = EvidenceAgreementEngine()
        self.coverage_agent = CoverageAgent()
        self.contradiction_agent = ContradictionAgent()
        self.reasoning_agent = ReasoningAgent()
        self.decision_matrix = DecisionMatrix()
        self.verification_agent = VerificationAgent()
        self.recommendation_engine = RecommendationEngine()
        self.llm_agent = LLMExplanationAgent()
        
        self.raw_doc_text = raw_doc_text
        
        # Agent Memory
        self.memory = {
            "retrieved_evidence": [],
            "previous_decisions": [],
            "remaining_tasks": [],
            "visited_features": set(),
            "visited_graph_nodes": set(),
            "visited_claims": set(),
        }

    def plan_and_execute(self, raw_claim: "Claim") -> AgentMessage:
        """
        Main entry point. Executes the full multi-agent investigation for one claim.
        """
        # ── Step 0: Agent Memory & Intent Resolution ────────────────────────
        if raw_claim.id in self.memory["visited_claims"]:
            self._log(None, f"Claim {raw_claim.id} already processed. Skipping.")
            return None
            
        self.memory["visited_claims"].add(raw_claim.id)
        
        resolved_intent = self.intent_resolver.resolve(raw_claim.text)
        for feat in resolved_intent.expected_features:
            self.memory["visited_features"].add(feat)

        # Create the shared initial message
        base_message = AgentMessage(
            message_type=MessageType.REQUEST,
            sender=AgentRole.TASK_PLANNER,
            recipient=AgentRole.CODE,
            claim_id=raw_claim.id,
            expected_features=resolved_intent.expected_features,
            payload={
                "intent": resolved_intent.intent,
                "expected_capabilities": resolved_intent.expected_capabilities,
                "expected_architecture": resolved_intent.expected_architecture,
                "claim_text": raw_claim.text,
                "raw_doc_text": self.raw_doc_text,
            },
            confidence=0.0
        )
        
        self._log(base_message, f"Planning investigation for intent='{resolved_intent.intent}', features={resolved_intent.expected_features}")
        
        # ── Step 1: Dispatch to 3 specialized agents independently ──────────
        code_msg = self._clone_message(base_message, AgentRole.CODE)
        code_result = self.code_agent.process(code_msg)
        
        doc_msg = self._clone_message(base_message, AgentRole.DOCUMENTATION)
        doc_result = self.docs_agent.process(doc_msg)
        
        graph_msg = self._clone_message(base_message, AgentRole.KNOWLEDGE_GRAPH)
        graph_result = self.graph_agent.process(graph_msg)
        
        # ── Step 2: Aggregate results into ranking message ─────────────────
        ranking_message = AgentMessage(
            message_type=MessageType.REQUEST,
            sender=AgentRole.TASK_PLANNER,
            recipient=AgentRole.EVIDENCE_RANKING,
            claim_id=raw_claim.id,
            expected_features=resolved_intent.expected_features,
            payload={
                "intent": resolved_intent.intent,
                "code_evidence": code_result.payload.get("code_evidence", []),
                "doc_evidence": doc_result.payload.get("doc_evidence", []),
                "graph_evidence": graph_result.payload.get("graph_evidence", []),
                "code_confidence": code_result.confidence,
                "doc_confidence": doc_result.confidence,
                "graph_confidence": graph_result.confidence,
            },
            trace=code_result.trace + doc_result.trace + graph_result.trace,
            confidence=0.0
        )
        
        self._log(ranking_message, "Aggregating evidence from specialized agents for ranking.")
        
        # ── Step 3: Run Remaining Pipeline (Linear) ─────────────────────────
        ranked_result = self.ranking_agent.process(ranking_message)
        fused_result = self.fusion_agent.process(ranked_result)
        validated_result = self.validation_agent.process(fused_result)
        agreement_result = self.agreement_engine.process(validated_result)
        coverage_result = self.coverage_agent.process(agreement_result)
        contradiction_result = self.contradiction_agent.process(coverage_result)
        reasoning_result = self.reasoning_agent.process(contradiction_result)
        decision_result = self.decision_matrix.process(reasoning_result)
        recommendation_result = self.recommendation_engine.process(decision_result)
        verification_result = self.verification_agent.process(recommendation_result)
        final_result = self.llm_agent.process(verification_result)
        
        # Update Memory
        self.memory["retrieved_evidence"].extend(final_result.evidence)
        self.memory["previous_decisions"].append({
            "claim_id": raw_claim.id,
            "verdict": final_result.payload.get("verdict")
        })
        
        self._log(final_result, f"Investigation complete. Final confidence={final_result.confidence:.2f}")
        return final_result

    def _clone_message(self, base: AgentMessage, recipient: AgentRole) -> AgentMessage:
        """Creates a fresh copy of the base message for a specific recipient."""
        return AgentMessage(
            message_type=MessageType.REQUEST,
            sender=AgentRole.TASK_PLANNER,
            recipient=recipient,
            claim_id=base.claim_id,
            expected_features=list(base.expected_features),
            payload=dict(base.payload),
            trace=[],
            confidence=0.0
        )
