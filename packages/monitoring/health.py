from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class ComponentHealth:
    name: str
    healthy: bool
    detail: str


@dataclass(frozen=True, slots=True)
class HealthReport:
    components: tuple[ComponentHealth, ...]

    @property
    def healthy(self) -> bool:
        return all(component.healthy for component in self.components)

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": "ok" if self.healthy else "degraded",
            "components": {
                component.name: {"status": "ok" if component.healthy else "error", "detail": component.detail}
                for component in self.components
            },
        }


def check_database(connection: Any) -> ComponentHealth:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return ComponentHealth("database", True, "reachable")
    except Exception as exc:
        return ComponentHealth("database", False, type(exc).__name__)


def check_redis(client: Any) -> ComponentHealth:
    try:
        if not client.ping():
            return ComponentHealth("redis", False, "ping returned false")
        return ComponentHealth("redis", True, "reachable")
    except Exception as exc:
        return ComponentHealth("redis", False, type(exc).__name__)


def check_queue_depth(client: Any, queue_key: str) -> ComponentHealth:
    try:
        depth = int(client.llen(queue_key))
        return ComponentHealth("queue", True, f"depth={depth}")
    except Exception as exc:
        return ComponentHealth("queue", False, type(exc).__name__)


def build_report(checks: tuple[Callable[[], ComponentHealth], ...]) -> HealthReport:
    return HealthReport(tuple(check() for check in checks))
