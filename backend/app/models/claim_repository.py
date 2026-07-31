from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List

from app.models.claim import Claim


@dataclass
class ClaimRepository:
    """
    Represents the final repository of documentation claims.

    This is the output of the Document Understanding pipeline
    and the input to the Claim–Evidence Matching Engine.
    """

    claims: List[Claim] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def add(
        self,
        claim: Claim,
    ) -> None:
        """
        Add a single claim.
        """
        self.claims.append(claim)

    def extend(
        self,
        claims: List[Claim],
    ) -> None:
        """
        Add multiple claims.
        """
        self.claims.extend(claims)

    def clear(self) -> None:
        """
        Remove all claims.
        """
        self.claims.clear()

    def __len__(self) -> int:
        return len(self.claims)

    def __iter__(self) -> Iterator[Claim]:
        return iter(self.claims)

    def __getitem__(
        self,
        index: int,
    ) -> Claim:
        return self.claims[index]