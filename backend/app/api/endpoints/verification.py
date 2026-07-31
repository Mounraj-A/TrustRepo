from fastapi import APIRouter

router = APIRouter(prefix="/verification", tags=["Verification"])


@router.get("/")
def verification_status():
    """
    Placeholder endpoint.
    """
    return {
        "message": "Verification module is under development."
    }