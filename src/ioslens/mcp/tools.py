"""MCP Tools — compliance_check, enforce_policy, udm_resolve."""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict

logger = logging.getLogger(__name__)


TOOL_DEFINITIONS = [
    {
        "name": "compliance_check",
        "description": "Check whether a proposed data access is compliant with governance policies.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "resource_type": {"type": "string", "description": "Type of resource (e.g. student_record)"},
                "resource_id": {"type": "string", "description": "UUID of the resource"},
                "purpose": {"type": "string", "description": "Declared access purpose"},
                "user_id": {"type": "string", "description": "User UUID"},
                "tenant_id": {"type": "string", "description": "Tenant UUID"},
            },
            "required": ["resource_type", "purpose", "user_id", "tenant_id"],
        },
    },
    {
        "name": "enforce_policy",
        "description": "Execute a governance policy decision and write to the audit ledger.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "execution_token": {"type": "string", "description": "Execution token (et_...)"},
                "action": {"type": "string", "description": "Action being performed"},
                "resource_type": {"type": "string"},
                "resource_id": {"type": "string"},
                "tenant_id": {"type": "string"},
                "user_id": {"type": "string"},
            },
            "required": ["execution_token", "action", "resource_type", "tenant_id", "user_id"],
        },
    },
    {
        "name": "udm_resolve",
        "description": "Resolve a query through the Universal Decoding Matrix.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "systems": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["CIP", "SOC", "NAICS"]},
                    "description": "Classification systems to search",
                },
                "tenant_id": {"type": "string"},
            },
            "required": ["query", "tenant_id"],
        },
    },
]

TOOL_REGISTRY: Dict[str, Any] = {t["name"]: t for t in TOOL_DEFINITIONS}


async def dispatch_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Dispatch a tool call to its handler."""
    if name not in TOOL_REGISTRY:
        raise KeyError(f"Unknown tool: {name!r}")

    if name == "compliance_check":
        return await _compliance_check(arguments)
    elif name == "enforce_policy":
        return await _enforce_policy(arguments)
    elif name == "udm_resolve":
        return await _udm_resolve(arguments)
    else:
        raise KeyError(f"Handler not implemented for tool: {name!r}")


async def _compliance_check(args: Dict[str, Any]) -> Dict[str, Any]:
    """Check compliance — stub that returns a structured response."""
    resource_type = args["resource_type"]
    purpose = args["purpose"]
    tenant_id = args["tenant_id"]
    user_id = args["user_id"]

    logger.info(
        "MCP compliance_check: tenant=%s user=%s resource=%s purpose=%s",
        tenant_id, user_id, resource_type, purpose,
    )

    # In production, connect to policy_engine and RLS-scoped DB
    return {
        "compliant": True,
        "policy_applied": f"POLICY_{resource_type.upper()}_{purpose.upper()}",
        "rationale": f"Access to {resource_type!r} for purpose {purpose!r} permitted.",
        "execution_token": "et_stub_" + secrets_token(),
    }


async def _enforce_policy(args: Dict[str, Any]) -> Dict[str, Any]:
    """Enforce policy — validate token and write audit entry."""
    execution_token = args["execution_token"]
    action = args["action"]
    resource_type = args["resource_type"]
    tenant_id = args["tenant_id"]
    user_id = args["user_id"]

    if not execution_token.startswith("et_"):
        raise PermissionError("Invalid execution token format")

    logger.info(
        "MCP enforce_policy: tenant=%s user=%s action=%s resource=%s",
        tenant_id, user_id, action, resource_type,
    )

    import hashlib, time
    audit_id = str(uuid.uuid4())
    chain_hash = hashlib.sha256(f"{tenant_id}|{audit_id}|{time.time()}".encode()).hexdigest()

    return {
        "enforced": True,
        "audit_id": audit_id,
        "chain_hash": chain_hash,
    }


async def _udm_resolve(args: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve via UDM — stub returns sample results."""
    query = args["query"]
    systems = args.get("systems", ["CIP", "SOC", "NAICS"])
    tenant_id = args["tenant_id"]

    logger.info("MCP udm_resolve: tenant=%s query=%r systems=%s", tenant_id, query, systems)

    # In production, connect to DB and use UDMResolver
    return {
        "query": query,
        "systems": systems,
        "results": [
            {"system": "CIP", "code": "11.0701", "title": "Computer Science", "score": 0.95},
            {"system": "SOC", "code": "15-1252", "title": "Software Developers", "score": 0.91},
        ],
    }


def secrets_token() -> str:
    import secrets
    return secrets.token_urlsafe(16)
