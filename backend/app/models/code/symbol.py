from pydantic import BaseModel, Field
from typing import Dict, Optional


class Symbol(BaseModel):
    name: str
    qualname: str
    type: str  # e.g., Class, Method, Field, Annotation, Import
    file_path: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    content: Optional[str] = None
    properties: Dict[str, str] = Field(default_factory=dict)
