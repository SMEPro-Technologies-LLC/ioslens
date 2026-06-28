"""Database connection pool management."""

import logging
from typing import Optional

import asyncpg

from ioslens.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_pool: Optional[asyncpg.Pool] = None


async def init_pool() -> asyncpg.Pool:
    """Initialize the asyncpg connection pool."""
    global _pool

    # Convert SQLAlchemy-style URL to asyncpg-compatible URL
    url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")

    _pool = await asyncpg.create_pool(
        dsn=url,
        min_size=settings.database_pool_min,
        max_size=settings.database_pool_max,
        command_timeout=30,
    )
    logger.info("Database pool created (min=%d max=%d)", settings.database_pool_min, settings.database_pool_max)
    return _pool


async def close_pool() -> None:
    """Close the connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database pool closed")


def get_pool() -> asyncpg.Pool:
    """Return the active pool or raise if not initialized."""
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_pool() first.")
    return _pool


class TenantConnection:
    """
    Async context manager that acquires a pool connection and sets tenant
    context (RLS) for the duration of the block.
    """

    def __init__(self, tenant_id: str, user_id: str, roles: list[str]) -> None:
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.roles = roles
        self._conn: Optional[asyncpg.Connection] = None

    async def __aenter__(self) -> asyncpg.Connection:
        pool = get_pool()
        self._conn = await pool.acquire()
        await _set_tenant_context(self._conn, self.tenant_id, self.user_id, self.roles)
        return self._conn

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._conn:
            pool = get_pool()
            await pool.release(self._conn)
            self._conn = None


async def _set_tenant_context(
    conn: asyncpg.Connection,
    tenant_id: str,
    user_id: str,
    roles: list[str],
) -> None:
    """Set PostgreSQL session variables used by RLS policies."""
    roles_str = ",".join(roles)
    await conn.execute(
        """
        SELECT
            set_config('app.tenant_id', $1, true),
            set_config('app.user_id',   $2, true),
            set_config('app.roles',     $3, true)
        """,
        str(tenant_id),
        str(user_id),
        roles_str,
    )
