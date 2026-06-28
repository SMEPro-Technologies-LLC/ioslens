"""Execution token service — issue, validate, and consume single-use tokens."""

from __future__ import annotations

import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional

from ioslens.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TokenService:
    """Manages execution token lifecycle: DESIGNED → ISSUED → CONSUMED / EXPIRED."""

    def __init__(self, conn_factory, redis_client=None) -> None:
        self._conn_factory = conn_factory
        self._redis = redis_client

    def _generate_token(self) -> tuple[str, str]:
        """Generate a raw token string and its SHA-256 hash."""
        raw = "et_" + secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw.encode()).hexdigest()
        return raw, token_hash

    async def issue(self, ctx) -> str:
        """
        Issue a new execution token for the given context.

        Returns:
            Raw token string (et_...) — stored only client-side.
        """
        raw, token_hash = self._generate_token()

        import asyncpg
        conn: asyncpg.Connection = await self._conn_factory()
        try:
            await conn.fetchval(
                """
                SELECT issue_execution_token($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                ctx.tenant_id,
                ctx.user_id,
                ctx.resource_type,
                ctx.resource_id,
                ctx.purpose,
                ctx.policy_id,
                token_hash,
                settings.execution_token_ttl_seconds,
            )
        finally:
            await conn.close()

        logger.info(
            "Execution token issued: tenant=%s user=%s resource=%s",
            ctx.tenant_id, ctx.user_id, ctx.resource_type,
        )
        return raw

    async def validate(self, raw_token: str, ctx) -> None:
        """
        Validate and consume an execution token.

        Raises:
            PermissionError: if the token is invalid, expired, or replayed
        """
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        import asyncpg
        conn: asyncpg.Connection = await self._conn_factory()
        try:
            row = await conn.fetchrow(
                "SELECT * FROM consume_execution_token($1, $2, $3)",
                token_hash,
                ctx.tenant_id,
                ctx.user_id,
            )
        finally:
            await conn.close()

        if not row["valid"]:
            raise PermissionError(f"Execution token invalid: {row['reason']}")

        logger.info(
            "Execution token consumed: id=%s tenant=%s",
            row["token_id"], ctx.tenant_id,
        )
