"""Policy Engine — Role, clearance, and purpose evaluation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PolicyEffect(str, Enum):
    PERMIT = "PERMIT"
    DENY = "DENY"
    FILTER = "FILTER"


@dataclass
class PolicyEvaluationRequest:
    tenant_id: str
    subject_id: str
    role: str
    clearance: int
    action: str
    resource_type: str
    resource_id: str | None = None
    purpose: str = ""


@dataclass
class PolicyEvaluationResult:
    effect: PolicyEffect
    matched_policy_id: str | None = None
    obligations: list[str] = field(default_factory=list)
    reason: str = ""


class PolicyEngine:
    """Evaluates governance policies for a given access request.

    Policies are evaluated in priority order:
      1. DENY policies (RESTRICTIVE) — checked first
      2. PERMIT policies — checked if no DENY matched
      3. Default: DENY if no PERMIT matched
    """

    async def evaluate(
        self,
        request: PolicyEvaluationRequest,
    ) -> PolicyEvaluationResult:
        """Evaluate all applicable policies and return a decision."""
        logger.debug(
            "PolicyEngine evaluate: tenant=%s role=%s action=%s resource=%s",
            request.tenant_id,
            request.role,
            request.action,
            request.resource_type,
        )

        # Stub: PERMIT all in scaffold
        return PolicyEvaluationResult(
            effect=PolicyEffect.PERMIT,
            reason="Default permit (stub implementation)",
        )

    async def load_policies(self, tenant_id: str) -> list[dict]:
        """Load active policies for a tenant from the database."""
        logger.debug("Loading policies for tenant=%s", tenant_id)
        return []
