"""Unit tests for UDMResolver."""

import uuid
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ioslens.middleware.udm_resolver import UDMResolver


def _make_mock_conn(rows: List[Dict[str, Any]] = None):
    """Build a mock asyncpg connection that returns `rows` for any fetch."""
    conn = AsyncMock()
    if rows is None:
        rows = []
    conn.fetch = AsyncMock(return_value=[MagicMock(**r) for r in rows])
    conn.fetchrow = AsyncMock(return_value=MagicMock(**rows[0]) if rows else None)
    conn.close = AsyncMock()
    return conn


@pytest.mark.asyncio
async def test_resolve_by_id_found():
    mock_row = {"id": str(uuid.uuid4()), "system": "CIP", "code": "11.0701", "title": "Computer Science", "description": ""}
    mock_conn = AsyncMock()
    mock_conn.fetchrow = AsyncMock(return_value=mock_row)
    mock_conn.close = AsyncMock()

    async def _factory():
        return mock_conn

    resolver = UDMResolver(_factory)
    result = await resolver.resolve_by_id(str(uuid.uuid4()))
    assert result.resolved is True
    assert len(result.entities) == 1
    assert result.entities[0]["system"] == "CIP"


@pytest.mark.asyncio
async def test_resolve_by_id_not_found():
    mock_conn = AsyncMock()
    mock_conn.fetchrow = AsyncMock(return_value=None)
    mock_conn.close = AsyncMock()

    async def _factory():
        return mock_conn

    resolver = UDMResolver(_factory)
    result = await resolver.resolve_by_id(str(uuid.uuid4()))
    assert result.resolved is False
    assert result.entities == []


@pytest.mark.asyncio
async def test_search_returns_results():
    mock_row = {"id": str(uuid.uuid4()), "system": "SOC", "code": "15-1252", "title": "Software Developers", "score": 0.91}
    mock_conn = AsyncMock()
    mock_conn.fetch = AsyncMock(return_value=[mock_row])
    mock_conn.close = AsyncMock()

    async def _factory():
        return mock_conn

    resolver = UDMResolver(_factory)
    results = await resolver.search("software", systems=["SOC"], limit=5)
    assert isinstance(results, list)
    mock_conn.fetch.assert_called_once()


@pytest.mark.asyncio
async def test_crosswalk_returns_mappings():
    mock_row = {"to_code": "15-1252", "title": "Software Developers", "confidence": 0.92, "source": "NCES"}
    mock_conn = AsyncMock()
    mock_conn.fetch = AsyncMock(return_value=[mock_row])
    mock_conn.close = AsyncMock()

    async def _factory():
        return mock_conn

    resolver = UDMResolver(_factory)
    results = await resolver.crosswalk("CIP", "11.0701", "SOC")
    assert isinstance(results, list)
