"""Unit tests for the UDM Resolver."""

import pytest
from ioslens.middleware.udm_resolver import UDMResolver


@pytest.fixture
def resolver() -> UDMResolver:
    return UDMResolver()


@pytest.mark.asyncio
async def test_resolve_returns_list(resolver: UDMResolver) -> None:
    """resolve() should return a list."""
    result = await resolver.resolve(cip_code="11.0701")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_resolve_raises_without_codes(resolver: UDMResolver) -> None:
    """resolve() should raise ValueError if no codes provided."""
    with pytest.raises(ValueError, match="At least one code parameter"):
        await resolver.resolve()


@pytest.mark.asyncio
async def test_resolve_with_soc_code(resolver: UDMResolver) -> None:
    """resolve() should accept soc_code parameter."""
    result = await resolver.resolve(soc_code="15-1252")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_resolve_with_naics_code(resolver: UDMResolver) -> None:
    """resolve() should accept naics_code parameter."""
    result = await resolver.resolve(naics_code="541511")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_search_semantic_returns_list(resolver: UDMResolver) -> None:
    """search_semantic() should return a list."""
    result = await resolver.search_semantic("computer science career paths")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_search_semantic_with_limit(resolver: UDMResolver) -> None:
    """search_semantic() should accept a limit parameter."""
    result = await resolver.search_semantic("engineering", limit=5)
    assert isinstance(result, list)
    assert len(result) <= 5
