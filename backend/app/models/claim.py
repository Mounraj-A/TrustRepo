from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.models.claim_type import ClaimType
from app.models.verification_status import VerificationStatus


@dataclass
class Claim:
    """
    Represents a single documentation claim extracted from a repository.
    """

    id: str

    text: str

    source_document: str

    source_section: str

    claim_type: ClaimType = ClaimType.UNKNOWN

    confidence: float = 0.0

    verification_status: VerificationStatus = VerificationStatus.PENDING

    supporting_evidence: List[str] = field(default_factory=list)

    contradicting_evidence: List[str] = field(default_factory=list)

    # Removed redundant metadata property (Phase 3 SSO refactor)