"""MCP Resources — policies, audit_logs, UDM taxonomies."""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Resource definitions (MCP resources/list schema)
RESOURCES = [
    {
        "uri": "policies://active",
        "name": "Active Governance Policies",
        "description": "All active governance policies for the current tenant.",
        "mimeType": "application/json",
    },
    {
        "uri": "audit_logs://recent",
        "name": "Recent Audit Logs",
        "description": "The 100 most recent audit log entries.",
        "mimeType": "application/json",
    },
    {
        "uri": "udm://cip_codes",
        "name": "CIP Code Taxonomy",
        "description": "Classification of Instructional Programs codes.",
        "mimeType": "application/json",
    },
    {
        "uri": "udm://soc_codes",
        "name": "SOC Code Taxonomy",
        "description": "Standard Occupational Classification codes.",
        "mimeType": "application/json",
    },
]


async def get_resource(uri: str) -> dict[str, Any]:
    """Retrieve a named resource by URI."""
    handlers: dict[str, Any] = {
        "policies://active": _get_active_policies,
        "audit_logs://recent": _get_recent_audit_logs,
        "udm://cip_codes": _get_cip_codes,
        "udm://soc_codes": _get_soc_codes,
    }

    handler = handlers.get(uri)
    if handler is None:
        raise ValueError(f"Unknown resource URI: {uri}")

    content = await handler()
    return {
        "contents": [
            {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(content, indent=2),
            }
        ]
    }


async def _get_active_policies() -> list[dict]:
    """Return active policies stub."""
    logger.debug("Fetching active policies (stub)")
    return []


async def _get_recent_audit_logs() -> list[dict]:
    """Return recent audit logs stub."""
    logger.debug("Fetching recent audit logs (stub)")
    return []


async def _get_cip_codes() -> list[dict]:
    """Return CIP code taxonomy stub."""
    return [
        {"code": "11.0701", "title": "Computer Science"},
        {"code": "52.0201", "title": "Business Administration"},
        {"code": "51.3801", "title": "Registered Nursing"},
    ]


async def _get_soc_codes() -> list[dict]:
    """Return SOC code taxonomy stub."""
    return [
        {"code": "15-1252", "title": "Software Developers"},
        {"code": "13-2011", "title": "Accountants and Auditors"},
        {"code": "29-1141", "title": "Registered Nurses"},
    ]
