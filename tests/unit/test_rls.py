"""Unit tests for RLS helpers."""

import uuid
from unittest.mock import AsyncMock, call

import pytest

from ioslens.database.rls import assert_rls_configured, clear_tenant_rls, set_tenant_rls


@pytest.mark.asyncio
async def test_set_tenant_rls_calls_set_config():
    mock_conn = AsyncMock()
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    roles = ["ADMIN", "ADVISOR"]

    await set_tenant_rls(mock_conn, tenant_id, user_id, roles)
    mock_conn.execute.assert_called_once()
    call_args = mock_conn.execute.call_args
    # Verify the SQL contains set_config calls
    assert "set_config" in call_args[0][0]
    # Verify tenant_id, user_id, and comma-joined roles were passed
    assert str(tenant_id) in call_args[0]
    assert str(user_id) in call_args[0]
    assert "ADMIN,ADVISOR" in call_args[0]


@pytest.mark.asyncio
async def test_clear_tenant_rls_clears_settings():
    mock_conn = AsyncMock()
    await clear_tenant_rls(mock_conn)
    mock_conn.execute.assert_called_once()
    call_args = mock_conn.execute.call_args[0][0]
    assert "set_config" in call_args


def test_assert_rls_configured_raises_on_empty_tenant():
    with pytest.raises(RuntimeError, match="tenant_id"):
        assert_rls_configured("", "some-user-id")


def test_assert_rls_configured_raises_on_empty_user():
    with pytest.raises(RuntimeError, match="user_id"):
        assert_rls_configured("some-tenant-id", "")


def test_assert_rls_configured_passes_with_valid_ids():
    # Should not raise
    assert_rls_configured("abc-123", "def-456")
