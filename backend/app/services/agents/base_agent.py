"""
Multi-Agent System — Explicit Agent Communication Model

Architecture:
                     Claim
                       │
                       ▼
              Task Planner Agent
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
     Code Agent   Docs Agent   Graph Agent
         └─────────────┼─────────────┘
                       ▼
              Evidence Fusion Agent
                       │
                       ▼
              Evidence Validation Agent  (NEW)
                       │
                       ▼
              Reasoning Agent            (NEW)
                       │
                       ▼
              Verification Agent
                       │
                       ▼
              Report Agent

Each agent receives a typed AgentMessage, performs its single responsibility,
and routes the enriched message to the next agent in the workflow.
Agents do NOT share mutable state — all communication is via AgentMessage.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Type
from enum import Enum
import uuid
from datetime import datetime
from app.models.knowledge.evidence import EvidenceChain

class AgentRole(str, Enum):
    TASK_PLANNER       = "TaskPlannerAgent"
    CODE               = "CodeAgent"
    DOCUMENTATION      = "DocumentationAgent"
    KNOWLEDGE_GRAPH    = "KnowledgeGraphAgent"
    EVIDENCE_RANKING   = "EvidenceRankingAgent"    # NEW
    EVIDENCE_FUSION    = "EvidenceFusionAgent"
    EVIDENCE_AGREEMENT = "EvidenceAgreementEngine" # NEW
    EVIDENCE_VALIDATION = "EvidenceValidationAgent"
    COVERAGE           = "CoverageAgent"           # NEW
    CONTRADICTION      = "ContradictionAgent"      # NEW
    REASONING          = "ReasoningAgent"
    DECISION_MATRIX    = "DecisionMatrix"          # NEW
    VERIFICATION       = "VerificationAgent"
    RECOMMENDATION     = "RecommendationEngine"    # NEW
    LLM_EXPLANATION    = "LLMExplanationAgent"     # NEW
    REPORT             = "ReportAgent"

class MessageType(str, Enum):
    REQUEST  = "REQUEST"
    RESPONSE = "RESPONSE"
    ERROR    = "ERROR"
    BROADCAST = "BROADCAST"

# Explicit workflow routing table
# Defines the exact sequence each agent must hand off to
AGENT_WORKFLOW: Dict[AgentRole, AgentRole] = {
    AgentRole.TASK_PLANNER:        AgentRole.CODE,
    AgentRole.CODE:                AgentRole.EVIDENCE_RANKING,
    AgentRole.DOCUMENTATION:       AgentRole.EVIDENCE_RANKING,
    AgentRole.KNOWLEDGE_GRAPH:     AgentRole.EVIDENCE_RANKING,
    AgentRole.EVIDENCE_RANKING:    AgentRole.EVIDENCE_FUSION,
    AgentRole.EVIDENCE_FUSION:     AgentRole.EVIDENCE_AGREEMENT,
    AgentRole.EVIDENCE_AGREEMENT:  AgentRole.COVERAGE,
    AgentRole.COVERAGE:            AgentRole.CONTRADICTION,
    AgentRole.CONTRADICTION:       AgentRole.REASONING,
    AgentRole.REASONING:           AgentRole.DECISION_MATRIX,
    AgentRole.DECISION_MATRIX:     AgentRole.VERIFICATION,
    AgentRole.VERIFICATION:        AgentRole.RECOMMENDATION,
    AgentRole.RECOMMENDATION:      AgentRole.LLM_EXPLANATION,
    AgentRole.LLM_EXPLANATION:     AgentRole.REPORT,
}


@dataclass
class AgentMessage:
    """
    Structured message exchanged between agents.
    Agents do NOT share mutable state — they communicate only via AgentMessage.

    Payload keys (standardized):
        code_evidence      : List[dict]   - Raw code evidence dicts
        doc_evidence       : List[dict]   - Documentation evidence dicts
        graph_evidence     : List[dict]   - KG graph evidence dicts
        evidence_chains    : List[dict]   - Serialised EvidenceChain objects
        fused_evidence     : List[dict]   - Post-fusion evidence candidates
        validated_chains   : List[dict]   - Post-validation chains
        evidence_quality   : float        - Aggregate quality score
        evidence_diversity : float        - Stream diversity score (0.0–1.0)
        decision_matrix    : dict         - Serialised DecisionMatrixResult
        expected_features  : List[str]    - From Ontology normalization
        observed_features  : List[str]    - From Evidence Validation
    """
    message_type: MessageType = MessageType.REQUEST
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    claim_id: str = ""
    sender: AgentRole = AgentRole.TASK_PLANNER
    recipient: AgentRole = AgentRole.TASK_PLANNER
    status: str = "PENDING"
    expected_features: List[str] = field(default_factory=list)
    evidence: List[EvidenceChain] = field(default_factory=list)
    confidence: float = 0.0
    payload: Dict[str, Any] = field(default_factory=dict)
    trace: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    parent_message_id: Optional[str] = None

    def route_to_next(self) -> "AgentMessage":
        """
        Automatically routes the message to the next agent in the workflow.
        Raises ValueError if no routing rule is defined for the current recipient.
        """
        next_agent = AGENT_WORKFLOW.get(self.recipient)
        if next_agent is None:
            raise ValueError(f"No workflow route defined from {self.recipient.value}")
        self.sender = self.recipient
        self.recipient = next_agent
        return self


class BaseAgent:
    """
    Foundation for all specialized TrustRepo agents.
    Each agent receives an AgentMessage, performs its specialized task,
    and returns an enriched AgentMessage for the next agent.
    """
    role: AgentRole = None

    def process(self, message: AgentMessage) -> AgentMessage:
        raise NotImplementedError

    def _log(self, message: AgentMessage, entry: str):
        message.trace.append(f"[{self.role.value}] {entry}")

    def _forward(self, message: AgentMessage) -> AgentMessage:
        """Forward to next agent in the explicit workflow."""
        message.route_to_next()
        return message

