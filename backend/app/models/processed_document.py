from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ProcessedDocument:
    """
    Represents a cleaned repository document.
    """

    path: str
    document_type: str

    original_content: str

    cleaned_content: str

    headings: List[str] = field(default_factory=list)

    code_blocks: List[str] = field(default_factory=list)

    metadata: Dict = field(default_factory=dict)
