"""Tenant management API endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ioslens.api.dependencies import CurrentUser

router = APIRouter()


class TenantResponse(BaseModel):
    id: str
    name: str
    domain: str
    active: bool


@router.get("/me", response_model=TenantResponse)
async def get_current_tenant(current_user: CurrentUser) -> TenantResponse:
    """Get current tenant information."""
    return TenantResponse(
        id=current_user.tenant_id,
        name="Demo Tenant",
        domain="demo.ioslens.ai",
        active=True,
    )


@router.get("/me/users")
async def list_tenant_users(current_user: CurrentUser) -> dict:
    """List users in the current tenant (admin only)."""
    if current_user.role != "admin":
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return {"users": [], "tenant_id": current_user.tenant_id}
