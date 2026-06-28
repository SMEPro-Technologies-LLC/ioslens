"""Anomaly detection — baseline deviation analysis for access patterns."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Anomaly:
    """A detected anomaly in access patterns."""
    anomaly_type: str
    severity: str  # low, medium, high, critical
    description: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AnomalyDetector:
    """
    Baseline deviation detection for tenant access patterns.
    Uses simple statistical thresholds; production would use ML models.
    """

    def __init__(self, z_score_threshold: float = 3.0) -> None:
        self.z_score_threshold = z_score_threshold

    def _z_score(self, value: float, mean: float, std: float) -> float:
        if std == 0:
            return 0.0
        return abs(value - mean) / std

    async def detect(
        self,
        tenant_id: str,
        current_metrics: Dict[str, float],
        baseline_metrics: Dict[str, float],
        baseline_std: Optional[Dict[str, float]] = None,
    ) -> List[Anomaly]:
        """
        Compare current metrics against baseline and return detected anomalies.

        Args:
            tenant_id: tenant identifier
            current_metrics: current period metrics (request_count, error_rate, etc.)
            baseline_metrics: historical mean for same metrics
            baseline_std: historical standard deviation (optional)
        """
        anomalies: List[Anomaly] = []
        std = baseline_std or {}

        checks = {
            "request_volume": ("Volume spike detected", 2.0),
            "error_rate": ("Error rate elevated", 2.0),
            "rls_denial_rate": ("Unusual RLS denial rate", 1.5),
            "token_replay_attempts": ("Token replay attempts detected", 1.0),
            "off_hours_access": ("Off-hours access spike", 2.0),
        }

        for metric, (description, sensitivity) in checks.items():
            current = current_metrics.get(metric, 0.0)
            baseline = baseline_metrics.get(metric, 0.0)
            metric_std = std.get(metric, max(baseline * 0.2, 0.001))

            z = self._z_score(current, baseline, metric_std)
            threshold = self.z_score_threshold / sensitivity

            if z > threshold:
                severity = "critical" if z > threshold * 2 else "high" if z > threshold * 1.5 else "medium"
                anomalies.append(Anomaly(
                    anomaly_type=metric,
                    severity=severity,
                    description=f"{description} (z={z:.2f}, current={current:.4f}, baseline={baseline:.4f})",
                    metadata={"tenant_id": tenant_id, "z_score": z, "metric": metric},
                ))
                logger.warning(
                    "Anomaly detected: tenant=%s metric=%s z=%.2f severity=%s",
                    tenant_id, metric, z, severity,
                )

        return anomalies
