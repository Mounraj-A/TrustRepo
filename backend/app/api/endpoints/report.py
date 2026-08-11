from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/")
def reports():
    """
    Placeholder endpoint.
    """
    return {
        "message": "Report module is under development."
    }
