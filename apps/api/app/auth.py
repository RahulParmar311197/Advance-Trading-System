from __future__ import annotations

from typing import Any

from fastapi import Depends, Header, HTTPException, status

from packages.saas.auth import APIKeyAuthenticator, Principal
from packages.saas.repositories import APIKeyRepository

from .dependencies import get_connection


def _authenticate(key_id: str, secret: str, connection: Any) -> Principal:
    """Authenticate from persistent API-key metadata; plaintext secrets never reach storage."""
    record = APIKeyRepository(connection).get(key_id)
    if record is None or not record.active:
        raise PermissionError("invalid API key")
    return APIKeyAuthenticator({key_id: record}).authenticate(key_id, secret)


def get_principal(
    api_key_id: str | None = Header(default=None, alias="X-API-Key-ID"),
    api_key_secret: str | None = Header(default=None, alias="X-API-Key-Secret"),
    connection: Any = Depends(get_connection),
) -> Principal:
    """Authenticate every protected request and fail closed on missing/invalid credentials."""
    if not api_key_id or not api_key_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
            headers={"WWW-Authenticate": "API-Key"},
        )
    try:
        return _authenticate(api_key_id, api_key_secret, connection)
    except (PermissionError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid API key",
            headers={"WWW-Authenticate": "API-Key"},
        ) from None


def require_permission(permission: str):
    """Return a FastAPI dependency enforcing a role permission after authentication."""

    def dependency(principal: Principal = Depends(get_principal)) -> Principal:
        if not principal.can(permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
        return principal

    return dependency
