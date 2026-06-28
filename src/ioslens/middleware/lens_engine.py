"""LENS Engine — 5-layer deterministic data narrowing."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class LensContext:
    """Context object passed through each LENS narrowing layer."""

    tenant_id: str
    user_id: str
    role: str
    clearance: int
    purpose: str
    resource_type: str
    data: list[dict[str, Any]] = field(default_factory=list)
    excluded_fields: set[str] = field(default_factory=set)


class LensEngine:
    """Five-layer deterministic narrowing engine.

    Layers:
      L1 — Tenant context: restrict to tenant's own data
      L2 — Role filter: apply role-based field restrictions
      L3 — Clearance filter: remove records above user clearance
      L4 — Purpose binding: limit fields to purpose-allowed set
      L5 — Temporal scope: apply recency or retention constraints
    """

    def narrow(self, ctx: LensContext) -> LensContext:
        """Apply all 5 narrowing layers sequentially."""
        ctx = self._layer1_tenant(ctx)
        ctx = self._layer2_role(ctx)
        ctx = self._layer3_clearance(ctx)
        ctx = self._layer4_purpose(ctx)
        ctx = self._layer5_temporal(ctx)
        return ctx

    def _layer1_tenant(self, ctx: LensContext) -> LensContext:
        """L1: Tenant context — data already RLS-filtered at DB layer."""
        logger.debug("L1 tenant context: tenant=%s", ctx.tenant_id)
        return ctx

    def _layer2_role(self, ctx: LensContext) -> LensContext:
        """L2: Role-based field restrictions."""
        if ctx.role == "viewer":
            ctx.excluded_fields.update({"ssn", "salary", "medical_record_id"})
        elif ctx.role == "analyst":
            ctx.excluded_fields.update({"ssn", "medical_record_id"})
        logger.debug("L2 role filter: role=%s excluded=%s", ctx.role, ctx.excluded_fields)
        return ctx

    def _layer3_clearance(self, ctx: LensContext) -> LensContext:
        """L3: Clearance-based record removal."""
        # Remove records whose clearance_level > user's clearance
        ctx.data = [
            r for r in ctx.data
            if r.get("clearance_level", 1) <= ctx.clearance
        ]
        logger.debug("L3 clearance filter: clearance=%d remaining=%d", ctx.clearance, len(ctx.data))
        return ctx

    def _layer4_purpose(self, ctx: LensContext) -> LensContext:
        """L4: Purpose binding — restrict fields not allowed for purpose."""
        purpose_restrictions: dict[str, set[str]] = {
            "academic_advising": {"medical_record_id", "financial_aid_details"},
            "financial_aid": {"medical_record_id"},
            "general": {"ssn", "medical_record_id", "financial_aid_details"},
        }
        restricted = purpose_restrictions.get(ctx.purpose, purpose_restrictions["general"])
        ctx.excluded_fields.update(restricted)
        logger.debug("L4 purpose filter: purpose=%s", ctx.purpose)
        return ctx

    def _layer5_temporal(self, ctx: LensContext) -> LensContext:
        """L5: Temporal scope — placeholder for recency constraints."""
        logger.debug("L5 temporal scope: (stub)")
        return ctx
