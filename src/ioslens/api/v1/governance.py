"""Governance API endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ioslens.api.dependencies import CurrentUser
from ioslens.middleware.orchestrator import MiddlewareOrchestrator, OrchestratorRequest

router = APIRouter()
_orchestrator = MiddlewareOrchestrator()


class EvaluateRequest(BaseModel):
    resource_type: str
    resource_id: str | None = None
    action: str
    purpose: str = ""


class EvaluateResponse(BaseModel):
    decision: str
    obligations: list[str]
    filtered_fields: list[str]
    audit_id: str | None = None


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_governance(
    body: EvaluateRequest,
    current_user: CurrentUser,
) -> EvaluateResponse:
    """Evaluate a data access request against governance policies."""
    result = await _orchestrator.process(
        OrchestratorRequest(
            tenant_id=current_user.tenant_id,
            subject_id=current_user.user_id,
            action=body.action,
            resource_type=body.resource_type,
            resource_id=body.resource_id,
            purpose=body.purpose,
        )
    )
    return EvaluateResponse(
        decision=result.decision,
        obligations=result.obligations,
        filtered_fields=result.filtered_fields,
        audit_id=result.audit_id,
    )


@router.get("/policies")
async def list_policies(current_user: CurrentUser) -> dict:
    """List active governance policies for the current tenant."""
    return {"policies": [], "tenant_id": current_user.tenant_id}
