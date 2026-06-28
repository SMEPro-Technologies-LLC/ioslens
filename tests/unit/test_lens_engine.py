"""Unit tests for LensEngine — 5-layer deterministic narrowing."""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pytest

from ioslens.middleware.lens_engine import LensEngine


@dataclass
class MockContext:
    tenant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    roles: List[str] = field(default_factory=lambda: ["ADVISOR"])
    resource_type: str = "student_record"
    resource_id: Optional[uuid.UUID] = None
    purpose: str = "academic_advising"
    action: str = "read"
    policy_id: Optional[uuid.UUID] = None
    execution_token: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=lambda: {"user_clearance": 0, "required_clearance": 0})


@pytest.mark.asyncio
async def test_lens_passes_all_five_layers():
    engine = LensEngine()
    ctx = MockContext()
    result = await engine.narrow(ctx)
    assert result.passed is True
    assert result.layer_reached == 5
    assert len(result.filters_applied) == 5


@pytest.mark.asyncio
async def test_lens_fails_missing_tenant():
    engine = LensEngine()
    ctx = MockContext()
    ctx.tenant_id = None
    result = await engine.narrow(ctx)
    assert result.passed is False
    assert result.layer_reached == 1


@pytest.mark.asyncio
async def test_lens_fails_no_roles():
    engine = LensEngine()
    ctx = MockContext(roles=[])
    result = await engine.narrow(ctx)
    assert result.passed is False
    assert result.layer_reached == 2


@pytest.mark.asyncio
async def test_lens_fails_no_purpose():
    engine = LensEngine()
    ctx = MockContext(purpose="")
    result = await engine.narrow(ctx)
    assert result.passed is False
    assert result.layer_reached == 3


@pytest.mark.asyncio
async def test_lens_fails_insufficient_clearance():
    engine = LensEngine()
    ctx = MockContext(metadata={"user_clearance": 1, "required_clearance": 3})
    result = await engine.narrow(ctx)
    assert result.passed is False
    assert result.layer_reached == 4


@pytest.mark.asyncio
async def test_lens_evaluate_query_success():
    engine = LensEngine()
    tenant_id = uuid.uuid4()
    result = await engine.evaluate_query(
        query="SELECT * FROM records",
        tenant_id=tenant_id,
        roles=["ADMIN"],
        purpose="reporting",
        clearance=5,
        required_clearance=0,
    )
    assert result["layers_passed"] == 5
    assert result["tenant_filter"] == str(tenant_id)
    assert result["purpose"] == "reporting"


@pytest.mark.asyncio
async def test_lens_evaluate_query_insufficient_clearance():
    engine = LensEngine()
    with pytest.raises(PermissionError, match="insufficient"):
        await engine.evaluate_query(
            query="SELECT *",
            tenant_id=uuid.uuid4(),
            roles=["USER"],
            purpose="read",
            clearance=0,
            required_clearance=5,
        )
