from enum import Enum
from typing import List

class EvidenceType(str, Enum):
    SOURCE_CODE = "Source Code"
    CONFIGURATION = "Configuration"
    DOCUMENTATION = "Documentation"
    NETWORKX_GRAPH = "Networkx Graph"
    AST_NODE = "AST Node"
    DEPENDENCY_TREE = "Dependency Tree"
    RUNTIME_TRACE = "Runtime Trace"

class EvidenceRegistry:
    """Central registry for standard evidence types."""
    
    @classmethod
    def all_types(cls) -> List[str]:
        return [e.value for e in EvidenceType]
