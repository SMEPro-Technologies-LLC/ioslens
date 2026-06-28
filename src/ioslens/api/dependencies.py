"""FastAPI dependencies — auth, database session, tenant context."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from ioslens.middleware.auth_service import AuthenticatedUser, AuthService

_auth_service = AuthService()


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthenticatedUser:
    """Extract and validate the current user from the Authorization header."""
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token authentication required (Authorization: ****** <token>)",
        )

    try:
        return _auth_service.validate_jwt(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
