from fastapi import APIRouter

router = APIRouter(prefix="/repositories", tags=["Repositories"])


@router.get("/")
def list_repositories():
    """
    Placeholder endpoint.
    Actual implementation will be added later.
    """
    return {
        "message": "Repository module is under development."
    }