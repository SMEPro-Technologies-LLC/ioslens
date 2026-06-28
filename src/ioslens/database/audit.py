"""Audit ledger: write and verify chained-hash audit entries."""

import hashlib
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

import asyncpg

logger = logging.getLogger(__name__)


def compute_chain_hash(
    prev_hash: str,
    entry_id: str,
    tenant_id: str,
    user_id: Optional[str],
    resource_type: str,
    action: str,
    created_at: datetime,
) -> str:
    """Compute SHA-256 chain hash for an audit entry."""
    data = "|".join([
        prev_hash,
        entry_id,
        tenant_id,
        user_id or "null",
        resource_type,
        action,
        created_at.isoformat(),
    ])
    return hashlib.sha256(data.encode()).hexdigest()


async def write_audit_entry(
    conn: asyncpg.Connection,
    tenant_id: uuid.UUID,
    user_id: Optional[uuid.UUID],
    resource_type: str,
    action: str,
    purpose: Optional[str] = None,
    resource_id: Optional[uuid.UUID] = None,
    outcome: str = "success",
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> uuid.UUID:
    """Insert an audit entry; chain hash is computed by DB trigger."""
    entry_id = await conn.fetchval(
        """
        INSERT INTO audit_ledger (
            tenant_id, user_id, resource_type, resource_id,
            action, purpose, outcome, metadata, ip_address, user_agent
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING id
        """,
        tenant_id,
        user_id,
        resource_type,
        resource_id,
        action,
        purpose,
        outcome,
        metadata or {},
        ip_address,
        user_agent,
    )
    return entry_id


async def verify_audit_chain(
    conn: asyncpg.Connection,
    tenant_id: uuid.UUID,
) -> Dict[str, Any]:
    """Verify the audit chain integrity for a tenant."""
    row = await conn.fetchrow(
        "SELECT * FROM verify_audit_chain($1)",
        tenant_id,
    )
    return {
        "valid": row["valid"],
        "records_checked": row["records_checked"],
        "broken_at": str(row["broken_at"]) if row["broken_at"] else None,
    }
