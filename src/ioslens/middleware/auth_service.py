"""Auth Service — SAML/OIDC/JWT validation."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import jwt

from ioslens.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class AuthenticatedUser:
    """Represents a validated, authenticated user."""

    user_id: str
    tenant_id: str
    email: str
    role: str
    clearance: int


class AuthService:
    """Validates JWT tokens and returns an AuthenticatedUser.

    Supports:
      - HS256 signed JWTs (development)
      - RS256 signed JWTs from OIDC providers (production)
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    def validate_jwt(self, token: str) -> AuthenticatedUser:
        """Validate a JWT and return the authenticated user."""
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret,
                algorithms=[self._settings.jwt_algorithm],
            )
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as exc:
            raise ValueError(f"Invalid token: {exc}") from exc

        return AuthenticatedUser(
            user_id=payload["sub"],
            tenant_id=payload["tenant_id"],
            email=payload.get("email", ""),
            role=payload.get("role", "viewer"),
            clearance=int(payload.get("clearance", 1)),
        )

    def create_jwt(
        self,
        user_id: str,
        tenant_id: str,
        email: str,
        role: str = "viewer",
        clearance: int = 1,
    ) -> str:
        """Create a signed JWT for development/testing purposes."""
        import time

        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "email": email,
            "role": role,
            "clearance": clearance,
            "iat": int(time.time()),
            "exp": int(time.time()) + self._settings.token_ttl_seconds,
        }
        return jwt.encode(
            payload,
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )
