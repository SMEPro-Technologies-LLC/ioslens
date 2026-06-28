"""UDM (Universal Decoding Matrix) endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ioslens.api.dependencies import CurrentIdentity
from ioslens.database.connection import get_pool
from ioslens.middleware.udm_resolver import UDMResolver

router = APIRouter()


class UDMResolveRequest(BaseModel):
    query: str
    systems: Optional[List[str]] = None
    limit: int = 10


@router.post("/resolve")
async def resolve_udm(
    body: UDMResolveRequest,
    identity: CurrentIdentity,
):
    """Resolve a query through the Universal Decoding Matrix."""
    async def _conn_factory():
        pool = get_pool()
        return await pool.acquire()

    resolver = UDMResolver(_conn_factory)
    results = await resolver.search(
        query=body.query,
        systems=body.systems,
        limit=body.limit,
    )
    return {"results": results}


@router.get("/crosswalk")
async def crosswalk(
    identity: CurrentIdentity,
    from_system: str = Query(...),
    from_code: str = Query(...),
    to_system: str = Query(...),
):
    """Get crosswalk mappings between classification systems."""
    async def _conn_factory():
        pool = get_pool()
        return await pool.acquire()

    resolver = UDMResolver(_conn_factory)
    results = await resolver.crosswalk(from_system, from_code, to_system)
    return {
        "from_system": from_system,
        "from_code": from_code,
        "to_system": to_system,
        "mappings": results,
    }
