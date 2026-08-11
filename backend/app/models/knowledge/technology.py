from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Technology:
    """
    Represents a technology entity in the Knowledge Base.
    Used for multi-evidence, hierarchical detection.
    """
    id: str
    display_name: str
    aliases: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    category: str = "Unknown"
    parent: Optional[str] = None
    detection_rules: Dict[str, Any] = field(default_factory=dict)
    evidence_rules: Dict[str, Any] = field(default_factory=dict)
    homepage: str = ""
    description: str = ""
