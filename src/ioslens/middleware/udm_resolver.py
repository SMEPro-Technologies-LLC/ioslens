"""Universal Decoding Matrix resolver — cross-domain taxonomy traversal."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import asyncpg

logger = logging.getLogger(__name__)


class UDMResult:
    """Result of a UDM resolution pass."""

    def __init__(self, entities: List[Dict[str, Any]], query: str) -> None:
        self.entities = entities
        self.query = query
        self.resolved = len(entities) > 0


class UDMResolver:
    """Resolve entities across CIP, SOC, and NAICS classification systems."""

    def __init__(self, conn_factory) -> None:
        """
        Args:
            conn_factory: callable returning an asyncpg connection
        """
        self._conn_factory = conn_factory

    async def resolve(self, ctx) -> UDMResult:
        """Resolve entity referenced in context via UDM."""
        if not ctx.resource_id:
            return UDMResult([], "")
        return await self.resolve_by_id(str(ctx.resource_id))

    async def resolve_by_id(self, entity_id: str) -> UDMResult:
        """Look up a UDM entity by UUID."""
        conn: asyncpg.Connection = await self._conn_factory()
        try:
            row = await conn.fetchrow(
                "SELECT id, system, code, title, description FROM udm_entities WHERE id = $1::uuid",
                entity_id,
            )
            entities = [dict(row)] if row else []
            return UDMResult(entities, f"id={entity_id}")
        finally:
            await conn.close()

    async def search(
        self,
        query: str,
        systems: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Full-text search over UDM entities using trigram similarity.
        Falls back gracefully if pgvector embedding is unavailable.
        """
        conn: asyncpg.Connection = await self._conn_factory()
        try:
            if systems:
                rows = await conn.fetch(
                    """
                    SELECT id, system, code, title,
                           similarity(title, $1) AS score
                    FROM udm_entities
                    WHERE system = ANY($2)
                      AND title % $1
                    ORDER BY score DESC
                    LIMIT $3
                    """,
                    query,
                    systems,
                    limit,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT id, system, code, title,
                           similarity(title, $1) AS score
                    FROM udm_entities
                    WHERE title % $1
                    ORDER BY score DESC
                    LIMIT $2
                    """,
                    query,
                    limit,
                )
            return [dict(r) for r in rows]
        finally:
            await conn.close()

    async def crosswalk(
        self,
        from_system: str,
        from_code: str,
        to_system: str,
    ) -> List[Dict[str, Any]]:
        """Return crosswalk mappings from one classification system to another."""
        conn: asyncpg.Connection = await self._conn_factory()
        try:
            rows = await conn.fetch(
                """
                SELECT c.to_code, e.title, c.confidence, c.source
                FROM udm_crosswalk c
                JOIN udm_entities e ON e.system = c.to_system AND e.code = c.to_code
                WHERE c.from_system = $1
                  AND c.from_code   = $2
                  AND c.to_system   = $3
                ORDER BY c.confidence DESC
                """,
                from_system,
                from_code,
                to_system,
            )
            return [dict(r) for r in rows]
        finally:
            await conn.close()
