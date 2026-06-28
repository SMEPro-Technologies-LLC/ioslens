"""RLS policy helpers — set/clear tenant context."""

import logging
import uuid
from typing import List

import asyncpg

logger = logging.getLogger(__name__)


async def set_tenant_rls(
    conn: asyncpg.Connection,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    roles: List[str],
) -> None:
    """Set PostgreSQL session variables for RLS policy evaluation."""
    await conn.execute(
        """
        SELECT
            set_config('app.tenant_id', $1, true),
            set_config('app.user_id',   $2, true),
            set_config('app.roles',     $3, true)
        """,
        str(tenant_id),
        str(user_id),
        ",".join(roles),
    )


async def clear_tenant_rls(conn: asyncpg.Connection) -> None:
    """Clear tenant context (e.g., before returning connection to pool)."""
    await conn.execute(
        """
        SELECT
            set_config('app.tenant_id', '', true),
            set_config('app.user_id',   '', true),
            set_config('app.roles',     '', true)
        """
    )


def assert_rls_configured(tenant_id: str, user_id: str) -> None:
    """Raise if tenant context appears unconfigured (defensive check)."""
    if not tenant_id or tenant_id == "":
        raise RuntimeError("RLS context not set: app.tenant_id is empty")
    if not user_id or user_id == "":
        raise RuntimeError("RLS context not set: app.user_id is empty")
