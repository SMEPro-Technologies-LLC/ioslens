"""pgvector HNSW similarity search operations."""

import logging
import uuid
from typing import List, Optional, Dict, Any

import asyncpg

logger = logging.getLogger(__name__)


async def vector_search(
    conn: asyncpg.Connection,
    embedding: List[float],
    systems: Optional[List[str]] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Perform cosine similarity search over udm_entities using pgvector HNSW index.

    Args:
        conn: asyncpg connection
        embedding: 1536-dimension float vector
        systems: optional filter on CIP/SOC/NAICS
        limit: max results to return

    Returns:
        List of dicts with id, system, code, title, similarity
    """
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

    if systems:
        rows = await conn.fetch(
            """
            SELECT id, system, code, title,
                   1 - (embedding <=> $1::halfvec) AS similarity
            FROM udm_entities
            WHERE system = ANY($2)
              AND embedding IS NOT NULL
            ORDER BY embedding <=> $1::halfvec
            LIMIT $3
            """,
            embedding_str,
            systems,
            limit,
        )
    else:
        rows = await conn.fetch(
            """
            SELECT id, system, code, title,
                   1 - (embedding <=> $1::halfvec) AS similarity
            FROM udm_entities
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> $1::halfvec
            LIMIT $2
            """,
            embedding_str,
            limit,
        )

    return [dict(r) for r in rows]


async def upsert_embedding(
    conn: asyncpg.Connection,
    system: str,
    code: str,
    embedding: List[float],
) -> None:
    """Update the embedding vector for a UDM entity."""
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
    await conn.execute(
        """
        UPDATE udm_entities
        SET embedding = $1::halfvec
        WHERE system = $2 AND code = $3
        """,
        embedding_str,
        system,
        code,
    )
