from fastapi import APIRouter

from app.api.endpoints.health import router as health_router
from app.api.endpoints.repository import router as repository_router
from app.api.endpoints.verification import router as verification_router
from app.api.endpoints.report import router as report_router
from app.api.endpoints.evidence import router as evidence_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(repository_router)
api_router.include_router(verification_router)
api_router.include_router(report_router)
api_router.include_router(evidence_router)