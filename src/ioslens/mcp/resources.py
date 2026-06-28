"""MCP Resources — policies, audit_logs."""

from __future__ import annotations

import logging
import json
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


RESOURCE_DEFINITIONS = [
    {
        "uri": "ioslens://policies/{tenant_id}",
        "name": "Governance Policies",
        "description": "Active governance policies for the tenant",
        "mimeType": "application/json",
    },
    {
        "uri": "ioslens://audit/{tenant_id}",
        "name": "Audit Logs",
        "description": "Recent audit log entries for the tenant",
        "mimeType": "application/json",
    },
]


async def get_resource(uri: str) -> str:
    """Resolve a resource URI and return its content as a string."""
    if uri.startswith("ioslens://policies/"):
        tenant_id = uri.split("/")[-1]
        return await _get_policies(tenant_id)
    elif uri.startswith("ioslens://audit/"):
        parts = uri.split("/")
        tenant_id = parts[-1].split("?")[0]
        return await _get_audit_logs(tenant_id)
    else:
        raise KeyError(f"Unknown resource URI: {uri!r}")


async def _get_policies(tenant_id: str) -> str:
    """Return governance policies for a tenant as JSON string."""
    # In production, query DB with tenant RLS context
    logger.info("MCP resource: policies for tenant=%s", tenant_id)
    stub = {
        "tenant_id": tenant_id,
        "policies": [
            {
                "name": "STUDENT_RECORD_ADVISOR_READ",
                "resource_type": "student_record",
                "allowed_roles": ["ADVISOR", "ADMIN"],
                "allowed_purposes": ["academic_advising", "reporting"],
                "active": True,
            }
        ],
    }
    return json.dumps(stub, indent=2)


async def _get_audit_logs(tenant_id: str) -> str:
    """Return recent audit logs for a tenant as JSON string."""
    logger.info("MCP resource: audit_logs for tenant=%s", tenant_id)
    stub = {
        "tenant_id": tenant_id,
        "audit_logs": [],
        "total": 0,
    }
    return json.dumps(stub, indent=2)
