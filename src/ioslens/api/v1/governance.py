"""Governance endpoints — policy check and list."""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from ioslens.api.dependencies import CurrentIdentity
from ioslens.database.connection import TenantConnection
from ioslens.middleware.policy_engine import PolicyEngine

router = APIRouter()


class GovernanceCheckRequest(BaseModel):
    resource_type: str
    resource_id: Optional[uuid.UUID] = None
    purpose: str
    action: str = "read"


class GovernanceCheckResponse(BaseModel):
    allowed: bool
    policy_id: Optional[uuid.UUID] = None
    rationale: Optional[str] = None
    reason: Optional[str] = None
    execution_token: Optional[str] = None


@router.post("/check", response_model=GovernanceCheckResponse)
async def governance_check(
    body: GovernanceCheckRequest,
    identity: CurrentIdentity,
) -> GovernanceCheckResponse:
    """Evaluate a governance policy against a data access request."""
    from ioslens.middleware.orchestrator import OrchestratorContext

    ctx = OrchestratorContext(
        tenant_id=identity.tenant_id,
        user_id=identity.user_id,
        roles=identity.roles,
        resource_type=body.resource_type,
        resource_id=body.resource_id,
        purpose=body.purpose,
        action=body.action,
        metadata={"user_clearance": identity.clearance},
    )

    async def _conn_factory():
        pool_conn = await TenantConnection(
            str(identity.tenant_id),
            str(identity.user_id),
            identity.roles,
        ).__aenter__()
        return pool_conn

    engine = PolicyEngine(_conn_factory)
    result = await engine.evaluate(ctx)

    if result.allowed:
        return GovernanceCheckResponse(
            allowed=True,
            policy_id=result.policy_id,
            rationale=result.rationale,
        )
    else:
        return GovernanceCheckResponse(
            allowed=False,
            policy_id=result.policy_id,
            reason=result.reason,
        )


@router.get("/policies")
async def list_policies(
    identity: CurrentIdentity,
    resource_type: Optional[str] = Query(default=None),
    role: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """List governance policies for the current tenant."""
    async def _conn_factory():
        from ioslens.database.connection import get_pool
        pool = get_pool()
        return await pool.acquire()

    engine = PolicyEngine(_conn_factory)
    policies = await engine.list_policies(
        tenant_id=identity.tenant_id,
        resource_type=resource_type,
        role=role,
        page=page,
        page_size=page_size,
    )
    return {"items": policies, "page": page, "page_size": page_size}
