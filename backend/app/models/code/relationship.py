from pydantic import BaseModel, Field
from typing import Dict


class Relationship(BaseModel):
    source_qualname: str
    target_qualname: str
    type: str  # e.g., DEPENDS_ON, CALLS, CONTAINS, IMPLEMENTS, EXTENDS, HAS_ANNOTATION
    properties: Dict[str, str] = Field(default_factory=dict)
    confidence: float = 1.0
