"""Unit tests for the LENS Engine narrowing logic."""

import pytest
from ioslens.middleware.lens_engine import LensContext, LensEngine


@pytest.fixture
def engine() -> LensEngine:
    return LensEngine()


@pytest.fixture
def base_context() -> LensContext:
    return LensContext(
        tenant_id="tenant-1",
        user_id="user-1",
        role="viewer",
        clearance=2,
        purpose="academic_advising",
        resource_type="student_record",
        data=[
            {"id": "r1", "name": "Alice", "ssn": "123-45-6789", "clearance_level": 1},
            {"id": "r2", "name": "Bob", "ssn": "987-65-4321", "clearance_level": 3},
            {"id": "r3", "name": "Carol", "salary": 75000, "clearance_level": 2},
        ],
    )


def test_lens_engine_returns_context(engine: LensEngine, base_context: LensContext) -> None:
    """narrow() should return a LensContext."""
    result = engine.narrow(base_context)
    assert isinstance(result, LensContext)


def test_layer1_tenant_passthrough(engine: LensEngine, base_context: LensContext) -> None:
    """L1 tenant context should not alter the data (RLS handles this at DB layer)."""
    result = engine._layer1_tenant(base_context)
    assert result.tenant_id == "tenant-1"


def test_layer2_role_viewer_excludes_ssn(engine: LensEngine, base_context: LensContext) -> None:
    """L2 should add 'ssn' to excluded_fields for 'viewer' role."""
    result = engine._layer2_role(base_context)
    assert "ssn" in result.excluded_fields


def test_layer2_role_admin_no_exclusions(engine: LensEngine, base_context: LensContext) -> None:
    """L2 should not add exclusions for 'admin' role."""
    base_context.role = "admin"
    result = engine._layer2_role(base_context)
    assert "ssn" not in result.excluded_fields


def test_layer3_clearance_filters_records(engine: LensEngine, base_context: LensContext) -> None:
    """L3 should remove records with clearance_level > user's clearance."""
    result = engine._layer3_clearance(base_context)
    # clearance=2, so records with clearance_level=3 should be removed
    assert len(result.data) == 2
    ids = [r["id"] for r in result.data]
    assert "r2" not in ids  # clearance_level=3 > 2


def test_layer4_purpose_academic_advising(engine: LensEngine, base_context: LensContext) -> None:
    """L4 should restrict fields for academic_advising purpose."""
    result = engine._layer4_purpose(base_context)
    assert "medical_record_id" in result.excluded_fields


def test_full_narrowing_pipeline(engine: LensEngine, base_context: LensContext) -> None:
    """Full pipeline should produce a narrowed context."""
    result = engine.narrow(base_context)
    # Should have removed high-clearance records
    assert len(result.data) < 3
    # Should have excluded SSN for viewer role
    assert "ssn" in result.excluded_fields


def test_empty_data_passthrough(engine: LensEngine) -> None:
    """Empty data should pass through all layers cleanly."""
    ctx = LensContext(
        tenant_id="t1", user_id="u1", role="admin",
        clearance=4, purpose="general", resource_type="test", data=[],
    )
    result = engine.narrow(ctx)
    assert result.data == []
