from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from packages.saas.auth import Principal


@dataclass(frozen=True, slots=True)
class AuditEvent:
    organization_id: str
    action: str
    resource_type: str
    resource_id: str | None
    outcome: str
    metadata: Mapping[str, Any]
    user_id: str | None

    def as_record(self) -> dict[str, Any]:
        return {
            "organization_id": self.organization_id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "outcome": self.outcome,
            "metadata": dict(self.metadata),
        }


def build_audit_event(
    principal: Principal | None,
    *,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    outcome: str = "success",
    metadata: Mapping[str, Any] | None = None,
) -> AuditEvent:
    if not action.strip() or not resource_type.strip():
        raise ValueError("audit action and resource_type must be non-empty")
    if outcome not in {"success", "denied", "failure"}:
        raise ValueError("invalid audit outcome")
    if principal is None:
        raise PermissionError("authenticated principal required for audit event")
    return AuditEvent(
        organization_id=principal.organization_id,
        user_id=principal.user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
        metadata=dict(metadata or {}),
    )


def write_audit_event(connection: Any, event: AuditEvent) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """INSERT INTO audit_logs
               (organization_id, user_id, action, resource_type, resource_id, outcome, metadata)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                event.organization_id,
                event.user_id,
                event.action,
                event.resource_type,
                event.resource_id,
                event.outcome,
                dict(event.metadata),
            ),
        )
    connection.commit()
