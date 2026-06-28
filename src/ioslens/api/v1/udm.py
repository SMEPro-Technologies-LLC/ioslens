"""UDM (Universal Decoding Matrix) API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ioslens.api.dependencies import CurrentUser
from ioslens.middleware.udm_resolver import UDMResolver

router = APIRouter()
_resolver = UDMResolver()


class UDMResolveResponse(BaseModel):
    cip_code: str | None = None
    soc_code: str | None = None
    naics_code: str | None = None
    mappings: list[dict] = []


@router.get("/resolve", response_model=UDMResolveResponse)
async def resolve_udm(
    current_user: CurrentUser,
    cip_code: str | None = Query(default=None),
    soc_code: str | None = Query(default=None),
    naics_code: str | None = Query(default=None),
) -> UDMResolveResponse:
    """Resolve cross-domain UDM mappings."""
    mappings = await _resolver.resolve(
        cip_code=cip_code,
        soc_code=soc_code,
        naics_code=naics_code,
    )
    return UDMResolveResponse(
        cip_code=cip_code,
        soc_code=soc_code,
        naics_code=naics_code,
        mappings=[
            {"id": str(m.id), "label": m.label, "description": m.description}
            for m in mappings
        ],
    )


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


@router.post("/search")
async def search_udm(
    body: SearchRequest,
    current_user: CurrentUser,
) -> dict:
    """Semantic search across UDM using vector embeddings."""
    results = await _resolver.search_semantic(body.query, limit=body.limit)
    return {"results": results, "query": body.query}
