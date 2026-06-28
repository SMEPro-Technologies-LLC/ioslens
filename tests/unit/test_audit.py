"""Unit tests for audit chain hash computation."""

import hashlib
import uuid
from datetime import datetime

import pytest

from ioslens.database.audit import compute_chain_hash


def test_compute_chain_hash_is_deterministic():
    entry_id = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    created_at = datetime(2025, 1, 1, 0, 0, 0)

    h1 = compute_chain_hash("genesis", entry_id, tenant_id, user_id, "student_record", "read", created_at)
    h2 = compute_chain_hash("genesis", entry_id, tenant_id, user_id, "student_record", "read", created_at)

    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex


def test_compute_chain_hash_changes_with_different_inputs():
    entry_id = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())
    created_at = datetime(2025, 1, 1, 0, 0, 0)

    h1 = compute_chain_hash("genesis", entry_id, tenant_id, None, "student_record", "read", created_at)
    h2 = compute_chain_hash("genesis", entry_id, tenant_id, None, "student_record", "write", created_at)

    assert h1 != h2


def test_compute_chain_hash_null_user():
    entry_id = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())
    created_at = datetime(2025, 1, 1, 0, 0, 0)

    # Should not raise with None user_id
    h = compute_chain_hash("genesis", entry_id, tenant_id, None, "student_record", "read", created_at)
    assert isinstance(h, str)
    assert len(h) == 64


def test_chain_propagation():
    """Simulate a two-record chain."""
    t = str(uuid.uuid4())
    at = datetime(2025, 1, 1)

    id0 = str(uuid.uuid4())
    h0 = compute_chain_hash("genesis", id0, t, None, "resource", "read", at)
    assert h0 != "genesis"

    id1 = str(uuid.uuid4())
    h1 = compute_chain_hash(h0, id1, t, None, "resource", "write", at)
    assert h1 != h0

    # Breaking the chain: different prev_hash gives different result
    h1_tampered = compute_chain_hash("tampered", id1, t, None, "resource", "write", at)
    assert h1_tampered != h1
