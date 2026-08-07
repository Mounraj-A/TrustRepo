from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.repositories.graph_repository import GraphRepository

router = APIRouter()

# DTOs
class EvidenceSourceDTO(BaseModel):
    repository_id: str
    file_path: str
    line_number: Optional[int]
    commit_sha: str
    parser_used: str

class EvidenceItemDTO(BaseModel):
    id: str
    node_type: str
    symbol: str
    evidence_type: str
    evidence_strength: str
    source: EvidenceSourceDTO

class EvidenceChainDTO(BaseModel):
    chain_id: str
    chain_type: str
    confidence: float
    reasoning_trace: str
    sequence: List[EvidenceItemDTO]

@router.get("/evidence/technology/{technology}", response_model=List[EvidenceChainDTO])
def get_evidence_by_technology(technology: str, repo: GraphRepository = Depends()):
    """Get all evidence chains that led to the detection of a specific technology."""
    # This would normally query the TrustRepoContext or database for evidence chains
    # related to the technology. For now, returning a mocked structure based on graph.
    return []

@router.get("/evidence/claim/{claim_id}", response_model=Dict[str, Any])
def get_evidence_by_claim(claim_id: str):
    """Get all evidence gathered to verify a specific claim."""
    # In a full implementation, this queries the EvidencePipeline results
    return {
        "claim_id": claim_id,
        "evidence_chains": []
    }

@router.get("/evidence/file/{file_id}", response_model=List[EvidenceItemDTO])
def get_evidence_by_file(file_id: str):
    """Get all raw evidence items extracted from a specific file."""
    # Returns evidence items with source.file_path matching file_id
    return []
