from __future__ import annotations

import redis
from fastapi import APIRouter, Depends, Response, status

from packages.monitoring.alerts import AlertTransitionTracker, LoggingAlertNotifier
from packages.monitoring.health import (
    ComponentHealth,
    HealthReport,
    build_report,
    check_database,
    check_queue_depth,
    check_redis,
)

from ..config import settings
from ..dependencies import get_readiness_connection

router = APIRouter()
_alert_tracker = AlertTransitionTracker(LoggingAlertNotifier())


@router.get("/health")
def health():
    """Liveness endpoint: process is running and able to answer requests."""
    return {"status": "ok", "service": "advance-trading-system"}


def _readiness_report(
    database: tuple[object | None, str | None],
) -> HealthReport:
    connection, database_error = database

    if not settings.redis_url:
        return HealthReport(
            (
                ComponentHealth("database", False, "not checked"),
                ComponentHealth("redis", False, "REDIS_URL is not configured"),
                ComponentHealth("queue", False, "REDIS_URL is not configured"),
            )
        )

    if database_error is not None:
        database_component = lambda: ComponentHealth("database", False, database_error)
    else:
        database_component = lambda: check_database(connection)

    try:
        client = redis.Redis.from_url(settings.redis_url, decode_responses=False)
    except Exception as exc:
        detail = f"Redis client configuration failed: {exc}"
        return build_report(
            (
                database_component,
                lambda: ComponentHealth("redis", False, detail),
                lambda: ComponentHealth("queue", False, "Redis client unavailable"),
            )
        )

    queue_key = f"ats:jobs:{settings.queue_name}"
    return build_report(
        (
            database_component,
            lambda: check_redis(client),
            lambda: check_queue_depth(client, queue_key),
        )
    )


@router.get("/health/ready")
def readiness(
    response: Response,
    database=Depends(get_readiness_connection),
):
    """Readiness endpoint covering PostgreSQL, Redis and queue dependencies."""
    report = _readiness_report(database)
    alert, delivery = _alert_tracker.observe(report)
    if not report.healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    body = report.as_dict()
    if not settings.redis_url:
        body["components"]["database"]["status"] = "unknown"
    if alert is not None and delivery is not None:
        body["alert"] = {
            "id": alert.alert_id,
            "status": alert.status,
            "severity": alert.severity,
            "delivery": {
                "status": "delivered" if delivery.delivered else "failed",
                "detail": delivery.detail,
            },
        }
    return body
