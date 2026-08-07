from pydantic import BaseModel, Field
from typing import List, Dict, Any

class GraphNode(BaseModel):
    label: str
    properties: Dict[str, Any]

class GraphEdge(BaseModel):
    source_qualname: str
    target_qualname: str
    rel_type: str
    properties: Dict[str, Any] = {}

class RepositoryKnowledgeGraph(BaseModel):
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)
