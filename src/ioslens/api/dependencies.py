"""FastAPI dependencies — auth, database, and identity extraction."""

from __future__ import annotations

import logging
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Header, status

from ioslens.middleware.auth_service import AuthService, Identity

logger = logging.getLogger(__name__)

_auth_service = AuthService()


async def get_current_identity(
    authorization: Annotated[Optional[str], Header()] = None,
) -> Identity:
    """
    Extract and validate the caller identity from the Authorization header.

    Raises:
        HTTPException 401 if token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        identity = await _auth_service.validate(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    return identity


CurrentIdentity = Annotated[Identity, Depends(get_current_identity)]


def require_role(*roles: str):
    """Dependency factory that requires the caller to have at least one of the given roles."""
    async def _check(identity: CurrentIdentity) -> Identity:
        if not any(r in identity.roles for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {list(roles)}",
            )
        return identity
    return Depends(_check)
