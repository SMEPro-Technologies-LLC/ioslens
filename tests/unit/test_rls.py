"""Unit tests for RLS policy helpers."""

import pytest


def test_rls_module_importable() -> None:
    """RLS module should be importable without a database connection."""
    from ioslens.database import rls  # noqa: F401
    assert hasattr(rls, "set_tenant_context")
    assert hasattr(rls, "clear_tenant_context")
    assert hasattr(rls, "RLSSession")


def test_rls_session_class_exists() -> None:
    """RLSSession should be a usable class."""
    from ioslens.database.rls import RLSSession
    assert RLSSession is not None


def test_rls_set_tenant_context_is_coroutine() -> None:
    """set_tenant_context should be an async function."""
    import asyncio
    from ioslens.database.rls import set_tenant_context
    assert asyncio.iscoroutinefunction(set_tenant_context)


def test_rls_clear_tenant_context_is_coroutine() -> None:
    """clear_tenant_context should be an async function."""
    import asyncio
    from ioslens.database.rls import clear_tenant_context
    assert asyncio.iscoroutinefunction(clear_tenant_context)
