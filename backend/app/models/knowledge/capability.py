from dataclasses import dataclass, field
from typing import List


@dataclass
class Capability:
    """
    Represents a high-level business or functional capability.
    Technologies map to Categories, which in turn map to Capabilities.
    """
    id: str
    display_name: str
    category_triggers: List[str] = field(default_factory=list)
    description: str = ""
