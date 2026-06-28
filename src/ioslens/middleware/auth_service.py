"""Auth service — SAML/OIDC/JWT validation and identity extraction."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import List

import jwt as pyjwt

from ioslens.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class Identity:
    """Resolved identity extracted from a validated JWT."""
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    roles: List[str] = field(default_factory=list)
    clearance: int = 0
    external_id: str = ""


class AuthService:
    """Validate JWTs and extract caller identity."""

    def __init__(self, secret: str = None, algorithm: str = None) -> None:
        self._secret = secret or settings.jwt_secret
        self._algorithm = algorithm or settings.jwt_algorithm

    async def validate(self, token: str) -> Identity:
        """
        Decode and validate a JWT, returning the resolved Identity.

        Raises:
            ValueError: if the token is invalid or missing required claims
        """
        try:
            payload = pyjwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                options={"verify_exp": True},
            )
        except pyjwt.ExpiredSignatureError as e:
            raise ValueError("JWT token has expired") from e
        except pyjwt.InvalidTokenError as e:
            raise ValueError(f"Invalid JWT token: {e}") from e

        try:
            tenant_id = uuid.UUID(payload["tenant_id"])
            user_id = uuid.UUID(payload["sub"])
            email = payload.get("email", "")
            roles = payload.get("roles", [])
            clearance = int(payload.get("clearance", 0))
            external_id = payload.get("external_id", str(user_id))
        except (KeyError, ValueError) as e:
            raise ValueError(f"JWT missing required claim: {e}") from e

        return Identity(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            roles=roles,
            clearance=clearance,
            external_id=external_id,
        )

    def create_token(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        email: str,
        roles: List[str],
        clearance: int = 0,
    ) -> str:
        """Issue a signed JWT (for testing / internal use)."""
        import time
        payload = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "email": email,
            "roles": roles,
            "clearance": clearance,
            "iat": int(time.time()),
            "exp": int(time.time()) + settings.jwt_expiry_seconds,
        }
        return pyjwt.encode(payload, self._secret, algorithm=self._algorithm)
