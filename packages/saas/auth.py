from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import hmac
import secrets
from typing import Mapping


class Role(StrEnum):
    OWNER = "owner"
    RESEARCHER = "researcher"
    TRADER = "trader"
    VIEWER = "viewer"


_ROLE_PERMISSIONS: dict[Role, frozenset[str]] = {
    Role.OWNER: frozenset({"read", "research", "trade", "admin"}),
    Role.RESEARCHER: frozenset({"read", "research"}),
    Role.TRADER: frozenset({"read", "research", "trade"}),
    Role.VIEWER: frozenset({"read"}),
}


@dataclass(frozen=True, slots=True)
class Principal:
    """Authenticated identity scoped to one organization."""

    user_id: str
    organization_id: str
    role: Role

    def __post_init__(self) -> None:
        if not self.user_id.strip() or not self.organization_id.strip():
            raise ValueError("principal identifiers must be non-empty")

    def can(self, permission: str) -> bool:
        return permission in _ROLE_PERMISSIONS[self.role]


@dataclass(frozen=True, slots=True)
class APIKeyRecord:
    """Stored API-key metadata; only a digest is persisted, never the secret."""

    key_id: str
    organization_id: str
    user_id: str
    role: Role
    secret_digest: str
    active: bool = True

    def __post_init__(self) -> None:
        if not self.key_id or not self.organization_id or not self.user_id:
            raise ValueError("API key identifiers must be non-empty")
        if len(self.secret_digest) != 64:
            raise ValueError("secret_digest must be a SHA-256 hex digest")


class APIKeyAuthenticator:
    """Deterministic verification boundary with fail-closed organization scoping."""

    def __init__(self, records: Mapping[str, APIKeyRecord]) -> None:
        self._records = dict(records)

    @staticmethod
    def generate_secret() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def digest_secret(secret: str) -> str:
        if not secret:
            raise ValueError("API key secret must be non-empty")
        return hashlib.sha256(secret.encode("utf-8")).hexdigest()

    def authenticate(self, key_id: str, secret: str) -> Principal:
        record = self._records.get(key_id)
        if record is None or not record.active:
            raise PermissionError("invalid API key")
        supplied = self.digest_secret(secret)
        if not hmac.compare_digest(supplied, record.secret_digest):
            raise PermissionError("invalid API key")
        return Principal(record.user_id, record.organization_id, record.role)


def authorize(principal: Principal, permission: str, organization_id: str) -> None:
    if principal.organization_id != organization_id:
        raise PermissionError("organization scope violation")
    if not principal.can(permission):
        raise PermissionError("permission denied")
