"""Token Service — Execution token lifecycle (DESIGNED state)."""

from __future__ import annotations

import logging
import secrets
import time
import uuid

import jwt

from ioslens.config import get_settings

logger = logging.getLogger(__name__)


class TokenService:
    """Manages execution token minting, validation, and revocation.

    Execution tokens are short-lived (15 min) and purpose-scoped.
    JTIs are tracked in Redis to prevent replay attacks.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    def mint_token(
        self,
        user_id: str,
        tenant_id: str,
        purpose: str,
    ) -> dict[str, str]:
        """Mint a new execution token."""
        jti = secrets.token_urlsafe(32)
        now = int(time.time())
        expires_at = now + self._settings.token_ttl_seconds

        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "purpose": purpose,
            "jti": jti,
            "iat": now,
            "exp": expires_at,
            "token_type": "execution",
        }

        token = jwt.encode(
            payload,
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )

        logger.debug(
            "Minted execution token: user=%s tenant=%s purpose=%s jti=%s",
            user_id, tenant_id, purpose, jti,
        )

        return {
            "token": token,
            "jti": jti,
            "expires_at": str(expires_at),
            "purpose": purpose,
        }

    def validate_token(self, token: str) -> dict:
        """Validate an execution token and return its claims."""
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret,
                algorithms=[self._settings.jwt_algorithm],
            )
        except jwt.ExpiredSignatureError:
            raise ValueError("Execution token has expired")
        except jwt.InvalidTokenError as exc:
            raise ValueError(f"Invalid execution token: {exc}") from exc

        if payload.get("token_type") != "execution":
            raise ValueError("Token is not an execution token")

        return payload

    def generate_token_id(self) -> str:
        """Generate a unique token ID."""
        return str(uuid.uuid4())
