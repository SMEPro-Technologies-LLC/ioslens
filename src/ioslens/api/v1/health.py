"""Health check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from ioslens.config import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return service health status."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
    )
