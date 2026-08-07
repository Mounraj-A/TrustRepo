from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class IRNode:
    """
    A generic node in the Unified Intermediate Representation (UIR).
    Represents semantic structures like Classes, Functions, and Variables.
    """
    type: str  # e.g., 'class', 'function', 'method', 'variable'
    name: str
    qualname: str
    file_path: str
    start_line: int
    end_line: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List['IRNode'] = field(default_factory=list)

@dataclass
class IntermediateRepresentation:
    """
    Root of the Unified Intermediate Representation for a file.
    """
    file_path: str
    language: str
    nodes: List[IRNode] = field(default_factory=list)
