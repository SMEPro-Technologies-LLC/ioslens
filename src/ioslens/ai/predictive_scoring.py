"""Predictive compliance posture scoring."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ComplianceScore:
    """Compliance posture score for a tenant."""
    tenant_id: str
    overall: float  # 0.0 - 1.0
    dimensions: Dict[str, float] = field(default_factory=dict)
    risk_level: str = "low"
    recommendations: List[str] = field(default_factory=list)


class PredictiveScoring:
    """
    Lightweight rule-based compliance scoring.
    In production, this would be replaced with an ML model.
    """

    RISK_THRESHOLDS = {
        "low": 0.8,
        "medium": 0.6,
        "high": 0.0,
    }

    async def score_tenant(
        self,
        tenant_id: str,
        metrics: Dict[str, Any],
    ) -> ComplianceScore:
        """
        Score a tenant's compliance posture from operational metrics.

        Args:
            tenant_id: tenant UUID string
            metrics: dict containing audit_violation_rate, policy_coverage,
                     token_replay_attempts, rls_denials, etc.
        """
        dimensions: Dict[str, float] = {}
        recommendations: List[str] = []

        # Policy coverage
        policy_coverage = float(metrics.get("policy_coverage", 1.0))
        dimensions["policy_coverage"] = policy_coverage
        if policy_coverage < 0.9:
            recommendations.append("Increase governance policy coverage to > 90%")

        # Audit chain integrity
        audit_integrity = float(metrics.get("audit_integrity", 1.0))
        dimensions["audit_integrity"] = audit_integrity
        if audit_integrity < 1.0:
            recommendations.append("Investigate audit chain integrity breach")

        # Token replay rate
        replay_rate = float(metrics.get("token_replay_rate", 0.0))
        token_score = max(0.0, 1.0 - replay_rate * 10)
        dimensions["token_security"] = token_score
        if replay_rate > 0.01:
            recommendations.append("Investigate execution token replay attempts")

        # RLS denial rate (high = unusual access patterns)
        rls_denial_rate = float(metrics.get("rls_denial_rate", 0.0))
        rls_score = max(0.0, 1.0 - rls_denial_rate * 5)
        dimensions["rls_posture"] = rls_score
        if rls_denial_rate > 0.05:
            recommendations.append("Review RLS policy denials for access pattern anomalies")

        overall = sum(dimensions.values()) / max(len(dimensions), 1)

        risk_level = "high"
        for level, threshold in self.RISK_THRESHOLDS.items():
            if overall >= threshold:
                risk_level = level
                break

        return ComplianceScore(
            tenant_id=tenant_id,
            overall=round(overall, 4),
            dimensions=dimensions,
            risk_level=risk_level,
            recommendations=recommendations,
        )
