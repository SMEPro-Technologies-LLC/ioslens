"""Row-Level Security helper functions for iOSLENS."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)


async def set_tenant_context(session: AsyncSession, tenant_id: str) -> None:
    """Set the PostgreSQL session variable for RLS tenant isolation.

    Must be called at the start of every transaction before any query
    that touches tenant-scoped tables.
    """
    await session.execute(
        text("SELECT set_tenant_context(:tenant_id)"),
        {"tenant_id": tenant_id},
    )
    logger.debug("RLS tenant context set: tenant=%s", tenant_id)


async def clear_tenant_context(session: AsyncSession) -> None:
    """Clear the tenant context variable from the PostgreSQL session."""
    await session.execute(
        text("SELECT set_config('app.tenant_id', '', true)")
    )


class RLSSession:
    """Context manager that sets and clears RLS tenant context."""

    def __init__(self, session: AsyncSession, tenant_id: str) -> None:
        self._session = session
        self._tenant_id = tenant_id

    async def __aenter__(self) -> AsyncSession:
        await set_tenant_context(self._session, self._tenant_id)
        return self._session

    async def __aexit__(self, *args: object) -> None:
        await clear_tenant_context(self._session)
