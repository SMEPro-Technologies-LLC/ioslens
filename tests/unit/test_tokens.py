"""Unit tests for the Token Service."""

import time

import pytest

from ioslens.middleware.token_service import TokenService


@pytest.fixture
def service() -> TokenService:
    return TokenService()


def test_mint_token_returns_dict(service: TokenService) -> None:
    """mint_token() should return a dict with token fields."""
    result = service.mint_token(
        user_id="user-1",
        tenant_id="tenant-1",
        purpose="academic_advising",
    )
    assert "token" in result
    assert "jti" in result
    assert "expires_at" in result
    assert "purpose" in result


def test_mint_token_purpose_preserved(service: TokenService) -> None:
    """Minted token should preserve the purpose."""
    result = service.mint_token("u1", "t1", "financial_aid")
    assert result["purpose"] == "financial_aid"


def test_validate_token_returns_claims(service: TokenService) -> None:
    """validate_token() should return the token payload."""
    minted = service.mint_token("user-1", "tenant-1", "test_purpose")
    claims = service.validate_token(minted["token"])
    assert claims["sub"] == "user-1"
    assert claims["tenant_id"] == "tenant-1"
    assert claims["purpose"] == "test_purpose"
    assert claims["token_type"] == "execution"


def test_validate_token_rejects_wrong_type(service: TokenService) -> None:
    """validate_token() should reject non-execution tokens."""
    import jwt
    from ioslens.config import get_settings

    settings = get_settings()
    payload = {
        "sub": "user-1",
        "tenant_id": "t1",
        "token_type": "access",  # not "execution"
        "iat": int(time.time()),
        "exp": int(time.time()) + 900,
    }
    bad_token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    with pytest.raises(ValueError, match="not an execution token"):
        service.validate_token(bad_token)


def test_validate_token_rejects_expired(service: TokenService) -> None:
    """validate_token() should raise on expired tokens."""
    import jwt
    from ioslens.config import get_settings

    settings = get_settings()
    payload = {
        "sub": "u1",
        "tenant_id": "t1",
        "purpose": "test",
        "jti": "test-jti",
        "token_type": "execution",
        "iat": int(time.time()) - 1000,
        "exp": int(time.time()) - 500,  # expired
    }
    expired_token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    with pytest.raises(ValueError, match="expired"):
        service.validate_token(expired_token)


def test_generate_token_id_is_unique(service: TokenService) -> None:
    """generate_token_id() should produce unique IDs."""
    ids = {service.generate_token_id() for _ in range(10)}
    assert len(ids) == 10
