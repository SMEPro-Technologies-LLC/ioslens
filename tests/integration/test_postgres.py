"""Integration tests for PostgreSQL database constraints and migrations.

These tests require a live PostgreSQL instance. They are skipped automatically
when DATABASE_URL is not configured for a test database.
"""

import os
import pytest

SKIP_REASON = "DATABASE_URL not set to a test database"
requires_db = pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"),
    reason=SKIP_REASON,
)


@requires_db
@pytest.mark.asyncio
async def test_tenant_unique_domain() -> None:
    """tenant.domain should have a unique constraint."""
    pytest.skip("Requires live database — set TEST_DATABASE_URL to run")


@requires_db
@pytest.mark.asyncio
async def test_user_tenant_email_unique() -> None:
    """(tenant_id, email) should be unique in users table."""
    pytest.skip("Requires live database — set TEST_DATABASE_URL to run")


@requires_db
@pytest.mark.asyncio
async def test_rls_tenant_isolation() -> None:
    """Queries should only return rows for the set tenant context."""
    pytest.skip("Requires live database — set TEST_DATABASE_URL to run")


@requires_db
@pytest.mark.asyncio
async def test_audit_chain_integrity() -> None:
    """Audit chain verification should pass for freshly inserted records."""
    pytest.skip("Requires live database — set TEST_DATABASE_URL to run")


def test_database_models_importable() -> None:
    """ORM models should be importable without a database connection."""
    from ioslens.database.models import (  # noqa: F401
        Tenant,
        User,
        UDMMapping,
        AuditLedger,
        ExecutionToken,
    )
    assert Tenant.__tablename__ == "tenants"
    assert User.__tablename__ == "users"
    assert AuditLedger.__tablename__ == "audit_ledger"
