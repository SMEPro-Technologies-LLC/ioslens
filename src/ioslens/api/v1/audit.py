"""Audit log endpoints."""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from ioslens.api.dependencies import CurrentIdentity
from ioslens.database.audit import verify_audit_chain
from ioslens.database.connection import TenantConnection

router = APIRouter()


@router.get("/logs")
async def get_audit_logs(
    identity: CurrentIdentity,
    start: Optional[datetime] = Query(default=None),
    end: Optional[datetime] = Query(default=None),
    user_id: Optional[uuid.UUID] = Query(default=None),
    action: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """Retrieve audit log entries for the current tenant."""
    if "ADMIN" not in identity.roles and "AUDITOR" not in identity.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires ADMIN or AUDITOR role")

    async with TenantConnection(
        str(identity.tenant_id), str(identity.user_id), identity.roles
    ) as conn:
        conditions = ["tenant_id = $1"]
        params = [identity.tenant_id]
        i = 2

        if start:
            conditions.append(f"created_at >= ${i}")
            params.append(start)
            i += 1
        if end:
            conditions.append(f"created_at <= ${i}")
            params.append(end)
            i += 1
        if user_id:
            conditions.append(f"user_id = ${i}")
            params.append(user_id)
            i += 1
        if action:
            conditions.append(f"action = ${i}")
            params.append(action)
            i += 1

        params.extend([page_size, (page - 1) * page_size])
        query = f"""
            SELECT id, tenant_id, user_id, resource_type, resource_id,
                   action, purpose, outcome, chain_hash, created_at
            FROM audit_ledger
            WHERE {' AND '.join(conditions)}
            ORDER BY created_at DESC
            LIMIT ${i} OFFSET ${i+1}
        """
        rows = await conn.fetch(query, *params)
        count_row = await conn.fetchval(
            f"SELECT COUNT(*) FROM audit_ledger WHERE {' AND '.join(conditions)}",
            *params[:-2],
        )

    return {
        "items": [dict(r) for r in rows],
        "total": count_row,
        "page": page,
        "page_size": page_size,
    }


@router.get("/verify")
async def verify_chain(identity: CurrentIdentity):
    """Verify the audit chain integrity for the current tenant."""
    if "ADMIN" not in identity.roles and "AUDITOR" not in identity.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires ADMIN or AUDITOR role")

    async with TenantConnection(
        str(identity.tenant_id), str(identity.user_id), identity.roles
    ) as conn:
        result = await verify_audit_chain(conn, identity.tenant_id)

    return result
