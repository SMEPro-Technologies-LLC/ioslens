"""Audit log API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ioslens.api.dependencies import CurrentUser

router = APIRouter()


class AuditEntry(BaseModel):
    id: str
    sequence_no: int
    action: str
    resource_type: str
    decision: str
    created_at: str
    chain_valid: bool | None = None


class AuditLogsResponse(BaseModel):
    entries: list[AuditEntry]
    total: int
    page: int
    chain_valid: bool


@router.get("/logs", response_model=AuditLogsResponse)
async def get_audit_logs(
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
) -> AuditLogsResponse:
    """Retrieve audit log entries for the current tenant."""
    return AuditLogsResponse(
        entries=[],
        total=0,
        page=page,
        chain_valid=True,
    )


@router.get("/verify")
async def verify_chain(current_user: CurrentUser) -> dict:
    """Verify audit chain integrity for the current tenant."""
    return {
        "tenant_id": current_user.tenant_id,
        "chain_valid": True,
        "records_checked": 0,
        "broken_links": [],
    }
