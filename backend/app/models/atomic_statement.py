from dataclasses import dataclass, field
from typing import Any, Dict
import uuid


@dataclass
class AtomicStatement:
    """
    Represents a single atomic statement extracted from a
    documentation section.

    An atomic statement expresses exactly one verifiable fact.
    It is the fundamental unit used by the verification engine
    to match documentation against repository evidence.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Source information
    document_path: str = ""
    document_type: str = ""
    section_title: str = ""

    # Statement content
    text: str = ""

    # Position within the section
    statement_index: int = 0

    # Confidence assigned by the extraction stage
    confidence: float = 1.0

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)