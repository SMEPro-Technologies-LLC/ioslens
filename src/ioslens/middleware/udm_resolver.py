"""UDM Resolver — Universal Decoding Matrix traversal."""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class UDMMapping:
    """A single cross-domain UDM mapping."""

    id: str
    cip_code: str | None
    soc_code: str | None
    naics_code: str | None
    label: str
    description: str = ""


class UDMResolver:
    """Traverses the Universal Decoding Matrix to resolve cross-domain mappings.

    Supports resolution from any code type (CIP, SOC, or NAICS) to related codes.
    """

    async def resolve(
        self,
        cip_code: str | None = None,
        soc_code: str | None = None,
        naics_code: str | None = None,
    ) -> list[UDMMapping]:
        """Resolve UDM mappings for the provided code(s).

        In production, queries the udm_mappings table via the database layer.
        This stub returns empty results.
        """
        if not any([cip_code, soc_code, naics_code]):
            raise ValueError("At least one code parameter is required")

        logger.debug(
            "UDM resolve: cip=%s soc=%s naics=%s",
            cip_code,
            soc_code,
            naics_code,
        )
        # Stub: return empty — database layer would populate this
        return []

    async def search_semantic(
        self,
        query: str,
        limit: int = 10,
    ) -> list[UDMMapping]:
        """Semantic search across UDM using vector embeddings.

        In production, uses pgvector HNSW index via vector.py.
        """
        logger.debug("UDM semantic search: query='%s' limit=%d", query, limit)
        return []
