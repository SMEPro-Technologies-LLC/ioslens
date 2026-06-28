"""Main API router — aggregates all v1 routes."""

from fastapi import APIRouter

from ioslens.api.v1 import audit, governance, health, tenants, udm

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(governance.router, prefix="/v1/governance", tags=["governance"])
api_router.include_router(audit.router, prefix="/v1/audit", tags=["audit"])
api_router.include_router(udm.router, prefix="/v1/udm", tags=["udm"])
api_router.include_router(tenants.router, prefix="/v1/tenants", tags=["tenants"])
