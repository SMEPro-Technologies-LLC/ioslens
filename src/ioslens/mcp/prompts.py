"""MCP Prompts — standard governance query prompts."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Prompt definitions (MCP prompts/list schema)
PROMPTS = [
    {
        "name": "governance_review",
        "description": "Review a data access decision with full context.",
        "arguments": [
            {
                "name": "subject_name",
                "description": "Display name of the requesting user",
                "required": True,
            },
            {
                "name": "resource_description",
                "description": "Human-readable description of the requested resource",
                "required": True,
            },
            {
                "name": "decision",
                "description": "PERMIT or DENY",
                "required": True,
            },
        ],
    },
    {
        "name": "compliance_summary",
        "description": "Summarize compliance posture for a tenant.",
        "arguments": [
            {
                "name": "tenant_name",
                "description": "Name of the tenant organization",
                "required": True,
            },
        ],
    },
]


async def get_prompt(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Retrieve a prompt with substituted arguments."""
    handlers = {
        "governance_review": _governance_review_prompt,
        "compliance_summary": _compliance_summary_prompt,
    }

    handler = handlers.get(name)
    if handler is None:
        raise ValueError(f"Unknown prompt: {name}")

    return await handler(arguments)


async def _governance_review_prompt(args: dict[str, Any]) -> dict[str, Any]:
    subject = args.get("subject_name", "Unknown User")
    resource = args.get("resource_description", "Unknown Resource")
    decision = args.get("decision", "UNKNOWN")

    return {
        "description": f"Governance review for {subject}",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Review this governance decision:\n\n"
                        f"User: {subject}\n"
                        f"Resource: {resource}\n"
                        f"Decision: {decision}\n\n"
                        f"Please provide an analysis of whether this decision "
                        f"appears appropriate given standard higher-education "
                        f"data governance principles."
                    ),
                },
            }
        ],
    }


async def _compliance_summary_prompt(args: dict[str, Any]) -> dict[str, Any]:
    tenant = args.get("tenant_name", "Unknown Organization")

    return {
        "description": f"Compliance summary for {tenant}",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Provide a compliance posture summary for: {tenant}\n\n"
                        f"Include: active policy count, recent violations, "
                        f"audit chain integrity status, and top recommendations."
                    ),
                },
            }
        ],
    }
