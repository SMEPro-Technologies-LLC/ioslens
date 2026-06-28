"""Tenant management endpoints."""

from fastapi import APIRouter, HTTPException, status

from ioslens.api.dependencies import CurrentIdentity
from ioslens.database.connection import TenantConnection

router = APIRouter()


@router.get("/me")
async def get_current_tenant(identity: CurrentIdentity):
    """Get current tenant details. Requires ADMIN role."""
    if "ADMIN" not in identity.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires ADMIN role",
        )

    async with TenantConnection(
        str(identity.tenant_id), str(identity.user_id), identity.roles
    ) as conn:
        row = await conn.fetchrow(
            "SELECT id, name, domain, tier, features, settings, created_at FROM tenants WHERE id = $1",
            identity.tenant_id,
        )

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    return dict(row)


@router.get("/users")
async def list_tenant_users(identity: CurrentIdentity, page: int = 1, page_size: int = 20):
    """List users in the current tenant. Requires ADMIN role."""
    if "ADMIN" not in identity.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires ADMIN role",
        )

    async with TenantConnection(
        str(identity.tenant_id), str(identity.user_id), identity.roles
    ) as conn:
        rows = await conn.fetch(
            """
            SELECT id, tenant_id, email, display_name, roles, clearance, active, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
            """,
            page_size,
            (page - 1) * page_size,
        )
        total = await conn.fetchval("SELECT COUNT(*) FROM users")

    return {
        "items": [dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
