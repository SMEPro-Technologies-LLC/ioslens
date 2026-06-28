"""Audit ledger writer with chained-hash integrity."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)


class AuditWriter:
    """Appends records to the audit ledger with chained SHA-256 hashing.

    Uses the `append_audit_record` database function defined in
    database/migrations/005_audit_ledger.sql for atomicity.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        tenant_id: str,
        subject_id: str | None,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        decision: str = "PERMIT",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Append an audit record and return its UUID."""
        result = await self._session.execute(
            text(
                "SELECT append_audit_record("
                "  :tenant_id::uuid, :subject_id::uuid, :action, "
                "  :resource_type, :resource_id::uuid, :decision, :metadata::jsonb"
                ")"
            ),
            {
                "tenant_id": tenant_id,
                "subject_id": subject_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "decision": decision,
                "metadata": json.dumps(metadata or {}),
            },
        )
        audit_id = str(result.scalar())
        logger.debug(
            "Audit recorded: id=%s tenant=%s action=%s decision=%s",
            audit_id, tenant_id, action, decision,
        )
        return audit_id

    async def verify_chain(
        self,
        tenant_id: str,
        from_seq: int = 1,
        to_seq: int | None = None,
    ) -> list[dict]:
        """Verify audit chain integrity for a tenant."""
        result = await self._session.execute(
            text(
                "SELECT * FROM verify_audit_chain("
                "  :tenant_id::uuid, :from_seq, :to_seq"
                ")"
            ),
            {"tenant_id": tenant_id, "from_seq": from_seq, "to_seq": to_seq},
        )
        rows = result.mappings().all()
        return [dict(r) for r in rows]
