"""Anomaly detection — baseline deviation detection for governance events."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AnomalyEvent:
    """Represents a detected anomaly in access patterns."""

    event_id: str
    tenant_id: str
    subject_id: str
    anomaly_type: str
    severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    description: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)


class AnomalyDetector:
    """Detects baseline deviations in governance and access patterns.

    Detection strategies:
      - Unusual access hours (outside established patterns)
      - Rapid clearance escalation attempts
      - Bulk data access (> N records in short window)
      - Geographic impossibility
      - Policy violation clustering
    """

    # Thresholds (configurable via settings in production)
    BULK_ACCESS_THRESHOLD = 100  # records per 5 minutes
    VIOLATION_CLUSTER_THRESHOLD = 5  # violations per hour

    async def analyze_request(
        self,
        tenant_id: str,
        subject_id: str,
        action: str,
        resource_type: str,
        metadata: dict | None = None,
    ) -> list[AnomalyEvent]:
        """Analyze a request for anomalies and return any detected events."""
        logger.debug(
            "Anomaly analysis: tenant=%s subject=%s action=%s",
            tenant_id,
            subject_id,
            action,
        )
        # Stub: no anomalies detected in scaffold
        return []

    async def get_recent_anomalies(
        self,
        tenant_id: str,
        limit: int = 20,
    ) -> list[AnomalyEvent]:
        """Retrieve recent anomaly events for a tenant."""
        return []
