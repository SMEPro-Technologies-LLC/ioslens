"""Unit tests for AuthService token creation and validation."""

import time
import uuid

import jwt as pyjwt
import pytest

from ioslens.middleware.auth_service import AuthService, Identity

SECRET = "test-secret-key"
ALGORITHM = "HS256"


def _make_service() -> AuthService:
    return AuthService(secret=SECRET, algorithm=ALGORITHM)


def test_create_and_validate_token():
    svc = _make_service()
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    token = svc.create_token(
        user_id=user_id,
        tenant_id=tenant_id,
        email="test@example.com",
        roles=["ADMIN"],
        clearance=2,
    )
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_validate_returns_identity():
    svc = _make_service()
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    token = svc.create_token(
        user_id=user_id,
        tenant_id=tenant_id,
        email="test@example.com",
        roles=["ADVISOR"],
        clearance=1,
    )
    identity = await svc.validate(token)
    assert isinstance(identity, Identity)
    assert identity.tenant_id == tenant_id
    assert identity.user_id == user_id
    assert "ADVISOR" in identity.roles
    assert identity.clearance == 1


@pytest.mark.asyncio
async def test_validate_expired_token():
    svc = _make_service()
    payload = {
        "sub": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "email": "x@x.com",
        "roles": [],
        "clearance": 0,
        "iat": int(time.time()) - 7200,
        "exp": int(time.time()) - 3600,  # expired
    }
    token = pyjwt.encode(payload, SECRET, algorithm=ALGORITHM)
    with pytest.raises(ValueError, match="expired"):
        await svc.validate(token)


@pytest.mark.asyncio
async def test_validate_invalid_signature():
    svc = _make_service()
    payload = {
        "sub": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "email": "x@x.com",
        "roles": [],
        "clearance": 0,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    token = pyjwt.encode(payload, "wrong-secret", algorithm=ALGORITHM)
    with pytest.raises(ValueError, match="Invalid"):
        await svc.validate(token)


@pytest.mark.asyncio
async def test_validate_missing_tenant_claim():
    svc = _make_service()
    payload = {
        "sub": str(uuid.uuid4()),
        # tenant_id missing
        "email": "x@x.com",
        "roles": [],
        "clearance": 0,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    token = pyjwt.encode(payload, SECRET, algorithm=ALGORITHM)
    with pytest.raises(ValueError, match="claim"):
        await svc.validate(token)
