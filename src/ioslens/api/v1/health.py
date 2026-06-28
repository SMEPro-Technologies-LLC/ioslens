"""Health check endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter

from ioslens.config import get_settings
from ioslens.database.connection import get_pool

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    """Return service health status. No authentication required."""
    db_status = "unknown"
    redis_status = "unknown"

    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "unavailable"

    return {
        "status": "healthy",
        "version": settings.version,
        "environment": settings.environment,
        "database": db_status,
        "redis": redis_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
