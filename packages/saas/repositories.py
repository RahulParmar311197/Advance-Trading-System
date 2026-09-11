from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .auth import APIKeyRecord, Role


@dataclass(frozen=True, slots=True)
class OrganizationRecord:
    organization_id: str
    name: str


@dataclass(frozen=True, slots=True)
class UserRecord:
    user_id: str
    organization_id: str
    email: str
    role: Role
    active: bool


class OrganizationRepository:
    """Parameterized PostgreSQL persistence for organization identities."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def create(self, organization_id: str, name: str) -> OrganizationRecord:
        if not organization_id.strip() or not name.strip():
            raise ValueError("organization_id and name must be non-empty")
        with self._connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO organizations (organization_id, name) VALUES (%s, %s)",
                (organization_id, name),
            )
        self._connection.commit()
        return OrganizationRecord(organization_id, name)

    def get(self, organization_id: str) -> OrganizationRecord | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT organization_id, name FROM organizations WHERE organization_id=%s",
                (organization_id,),
            )
            row = cursor.fetchone()
        return None if row is None else OrganizationRecord(str(row[0]), str(row[1]))


class UserRepository:
    """Parameterized PostgreSQL persistence for organization-scoped users."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def create(
        self,
        user_id: str,
        organization_id: str,
        email: str,
        role: Role,
    ) -> UserRecord:
        if not user_id.strip() or not organization_id.strip() or not email.strip():
            raise ValueError("user_id, organization_id and email must be non-empty")
        with self._connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO users (user_id, organization_id, email, role)
                   VALUES (%s, %s, %s, %s)""",
                (user_id, organization_id, email, role.value),
            )
        self._connection.commit()
        return UserRecord(user_id, organization_id, email, role, True)

    def get(self, user_id: str) -> UserRecord | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """SELECT user_id, organization_id, email, role, active
                   FROM users WHERE user_id=%s""",
                (user_id,),
            )
            row = cursor.fetchone()
        return None if row is None else UserRecord(
            str(row[0]), str(row[1]), str(row[2]), Role(row[3]), bool(row[4])
        )


class APIKeyRepository:
    """Persistent API-key metadata access; plaintext secrets never enter this repository."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def create(
        self,
        key_id: str,
        organization_id: str,
        user_id: str,
        role: Role,
        secret_digest: str,
    ) -> APIKeyRecord:
        record = APIKeyRecord(key_id, organization_id, user_id, role, secret_digest)
        with self._connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO api_keys
                   (key_id, organization_id, user_id, role, secret_digest)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    record.key_id,
                    record.organization_id,
                    record.user_id,
                    record.role.value,
                    record.secret_digest,
                ),
            )
        self._connection.commit()
        return record

    def get(self, key_id: str) -> APIKeyRecord | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """SELECT key_id, organization_id, user_id, role, secret_digest, active
                   FROM api_keys WHERE key_id=%s""",
                (key_id,),
            )
            row = cursor.fetchone()
        return None if row is None else APIKeyRecord(
            str(row[0]), str(row[1]), str(row[2]), Role(row[3]), str(row[4]), bool(row[5])
        )

    def revoke(self, key_id: str) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """UPDATE api_keys
                   SET active=FALSE, revoked_at=now()
                   WHERE key_id=%s""",
                (key_id,),
            )
        self._connection.commit()
