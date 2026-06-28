"""Unit tests for the Audit Writer module."""

import pytest


def test_audit_module_importable() -> None:
    """Audit module should be importable without a database connection."""
    from ioslens.database import audit  # noqa: F401
    assert hasattr(audit, "AuditWriter")


def test_audit_writer_constructor() -> None:
    """AuditWriter should instantiate with a mock session."""
    from unittest.mock import MagicMock
    from ioslens.database.audit import AuditWriter

    mock_session = MagicMock()
    writer = AuditWriter(mock_session)
    assert writer is not None


def test_audit_writer_record_is_coroutine() -> None:
    """AuditWriter.record should be an async method."""
    import asyncio
    from ioslens.database.audit import AuditWriter
    assert asyncio.iscoroutinefunction(AuditWriter.record)


def test_audit_writer_verify_chain_is_coroutine() -> None:
    """AuditWriter.verify_chain should be an async method."""
    import asyncio
    from ioslens.database.audit import AuditWriter
    assert asyncio.iscoroutinefunction(AuditWriter.verify_chain)
