"""Policy engine — evaluate role + clearance + purpose against governance policies."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PolicyResult:
    allowed: bool
    policy_id: Optional[uuid.UUID] = None
    reason: Optional[str] = None
    rationale: Optional[str] = None


class PolicyEngine:
    """Evaluate governance policies for a given request context."""

    def __init__(self, conn_factory) -> None:
        self._conn_factory = conn_factory

    async def evaluate(self, ctx) -> PolicyResult:
        """
        Evaluate whether the context satisfies at least one active policy
        for the given tenant, resource_type, role, and purpose.
        """
        import asyncpg
        conn: asyncpg.Connection = await self._conn_factory()
        try:
            row = await conn.fetchrow(
                """
                SELECT id, name, min_clearance
                FROM governance_policies
                WHERE tenant_id        = $1
                  AND resource_type    = $2
                  AND allowed_roles    && $3::text[]
                  AND allowed_purposes && ARRAY[$4]::text[]
                  AND active           = true
                ORDER BY min_clearance DESC
                LIMIT 1
                """,
                ctx.tenant_id,
                ctx.resource_type,
                ctx.roles,
                ctx.purpose,
            )
        finally:
            await conn.close()

        if not row:
            return PolicyResult(
                allowed=False,
                reason=f"No active policy for resource_type={ctx.resource_type!r} "
                       f"with roles={ctx.roles!r} and purpose={ctx.purpose!r}",
            )

        user_clearance = ctx.metadata.get("user_clearance", 0)
        if user_clearance < row["min_clearance"]:
            return PolicyResult(
                allowed=False,
                policy_id=row["id"],
                reason=f"Clearance {user_clearance} below policy minimum {row['min_clearance']}",
            )

        return PolicyResult(
            allowed=True,
            policy_id=row["id"],
            rationale=f"Policy '{row['name']}' grants access for roles {ctx.roles!r} "
                      f"and purpose {ctx.purpose!r}",
        )

    async def list_policies(
        self,
        tenant_id: uuid.UUID,
        resource_type: Optional[str] = None,
        role: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[dict]:
        """List governance policies for a tenant."""
        import asyncpg
        conn: asyncpg.Connection = await self._conn_factory()
        try:
            filters = ["tenant_id = $1", "active = true"]
            params: list = [tenant_id]
            i = 2
            if resource_type:
                filters.append(f"resource_type = ${i}")
                params.append(resource_type)
                i += 1
            if role:
                filters.append(f"${ i}::text = ANY(allowed_roles)")
                params.append(role)
                i += 1

            params.extend([page_size, (page - 1) * page_size])
            query = f"""
                SELECT id, name, resource_type, allowed_roles, allowed_purposes,
                       min_clearance, created_at
                FROM governance_policies
                WHERE {' AND '.join(filters)}
                ORDER BY created_at DESC
                LIMIT ${i} OFFSET ${i + 1}
            """
            rows = await conn.fetch(query, *params)
            return [dict(r) for r in rows]
        finally:
            await conn.close()
