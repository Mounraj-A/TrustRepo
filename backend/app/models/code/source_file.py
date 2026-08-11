from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class SourceFile:
    """
    Represents a single source code file
    within a repository.
    """

    path: str

    language: str

    content: str

    extension: str

    size: int

    metadata: Dict[str, Any] = field(default_factory=dict)
