"""pgvector HNSW search operations for iOSLENS."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)


class VectorSearch:
    """Performs semantic search using pgvector HNSW indexes."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search_udm(
        self,
        embedding: list[float],
        limit: int = 10,
        min_similarity: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Search UDM mappings by semantic similarity.

        Args:
            embedding: Query vector (1536-dimensional).
            limit: Maximum number of results to return.
            min_similarity: Minimum cosine similarity threshold (0–1).

        Returns:
            List of UDM mappings with similarity scores.
        """
        # Validate embedding values to prevent injection before formatting
        validated = [float(v) for v in embedding]
        vec_literal = "[" + ",".join(repr(v) for v in validated) + "]"

        result = await self._session.execute(
            text(
                "SELECT id, cip_code, soc_code, naics_code, label, similarity "
                "FROM search_udm_semantic(:embedding::halfvec(1536), :limit, :min_sim)"
            ),
            {
                "embedding": vec_literal,
                "limit": limit,
                "min_sim": min_similarity,
            },
        )
        rows = result.mappings().all()
        return [dict(r) for r in rows]

    async def upsert_embedding(
        self,
        mapping_id: str,
        embedding: list[float],
    ) -> None:
        """Update the embedding vector for a UDM mapping."""
        # Validate embedding values before formatting as SQL literal
        validated = [float(v) for v in embedding]
        vec_literal = "[" + ",".join(repr(v) for v in validated) + "]"
        await self._session.execute(
            text(
                "UPDATE udm_mappings SET embedding = :embedding::halfvec(1536) "
                "WHERE id = :id::uuid"
            ),
            {"id": mapping_id, "embedding": vec_literal},
        )
        logger.debug("Updated embedding for UDM mapping: id=%s", mapping_id)
