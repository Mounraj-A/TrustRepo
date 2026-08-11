from dataclasses import dataclass, field
from typing import Dict


@dataclass
class DocumentSection:
    """
    Represents one semantic section extracted
    from repository documentation.
    """

    document_path: str

    document_type: str

    title: str

    content: str

    level: int

    metadata: Dict = field(default_factory=dict)
