"""MCP Prompts — standard query templates."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

from ioslens.mcp.tools import TOOL_DEFINITIONS
from ioslens.mcp.resources import RESOURCE_DEFINITIONS


PROMPT_DEFINITIONS = [
    {
        "name": "compliance_review",
        "description": "Review the compliance status for a tenant over a time period.",
        "arguments": [
            {"name": "tenant_id", "description": "Tenant UUID", "required": True},
            {"name": "start", "description": "Start date (ISO 8601)", "required": True},
            {"name": "end", "description": "End date (ISO 8601)", "required": True},
            {"name": "focus_areas", "description": "Comma-separated compliance focus areas", "required": False},
        ],
    },
    {
        "name": "policy_explanation",
        "description": "Explain a governance policy to an end user.",
        "arguments": [
            {"name": "policy_name", "description": "Policy name", "required": True},
            {"name": "user_role", "description": "User's role", "required": True},
        ],
    },
    {
        "name": "udm_exploration",
        "description": "Explore cross-domain classification mappings.",
        "arguments": [
            {"name": "domain", "description": "Domain or discipline to explore", "required": True},
        ],
    },
]


def list_tools() -> List[Dict[str, Any]]:
    return TOOL_DEFINITIONS


def list_resources() -> List[Dict[str, Any]]:
    return RESOURCE_DEFINITIONS


def list_prompts() -> List[Dict[str, Any]]:
    return PROMPT_DEFINITIONS


def get_prompt(name: str, arguments: Dict[str, str]) -> List[Dict[str, str]]:
    """Render a prompt template with the given arguments."""
    templates = {p["name"]: p for p in PROMPT_DEFINITIONS}
    if name not in templates:
        raise KeyError(f"Unknown prompt: {name!r}")

    if name == "compliance_review":
        tenant_id = arguments.get("tenant_id", "{{tenant_id}}")
        start = arguments.get("start", "{{start}}")
        end = arguments.get("end", "{{end}}")
        focus = arguments.get("focus_areas", "policy coverage, audit integrity, token security")
        return [
            {
                "role": "user",
                "content": (
                    f"Review the compliance status for tenant {tenant_id} "
                    f"covering the period {start} to {end}. "
                    f"Focus on: {focus}. "
                    "Summarize key findings, risk areas, and recommendations."
                ),
            }
        ]

    elif name == "policy_explanation":
        policy_name = arguments.get("policy_name", "{{policy_name}}")
        user_role = arguments.get("user_role", "{{user_role}}")
        return [
            {
                "role": "user",
                "content": (
                    f"Explain the governance policy '{policy_name}' "
                    f"to a user with the role '{user_role}'. "
                    "Use plain language and explain what data they can access, under what conditions, "
                    "and why this policy exists."
                ),
            }
        ]

    elif name == "udm_exploration":
        domain = arguments.get("domain", "{{domain}}")
        return [
            {
                "role": "user",
                "content": (
                    f"Using the Universal Decoding Matrix, explore all classification codes "
                    f"related to '{domain}'. "
                    "Show CIP (educational programs), SOC (occupations), and NAICS (industries) codes "
                    "and explain how they are interconnected."
                ),
            }
        ]

    return []
