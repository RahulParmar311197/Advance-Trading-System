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
from ..dependencies import get_connection

router = APIRouter()
_alert_tracker = AlertTransitionTracker(LoggingAlertNotifier())


@router.get("/health")
def health():
    """Liveness endpoint: process is running and able to answer requests."""
    return {"status": "ok", "service": "advance-trading-system"}


def _readiness_report(connection) -> HealthReport:
    if not settings.redis_url:
        return HealthReport(
            (
                ComponentHealth("database", False, "not checked"),
                ComponentHealth("redis", False, "REDIS_URL is not configured"),
                ComponentHealth("queue", False, "REDIS_URL is not configured"),
            )
        )

    client = redis.Redis.from_url(settings.redis_url, decode_responses=False)
    queue_key = f"ats:jobs:{settings.queue_name}"
    return build_report(
        (
            lambda: check_database(connection),
            lambda: check_redis(client),
            lambda: check_queue_depth(client, queue_key),
        )
    )


@router.get("/health/ready")
def readiness(response: Response, connection=Depends(get_connection)):
    """Readiness endpoint covering PostgreSQL, Redis and queue dependencies."""
    report = _readiness_report(connection)
    alert, delivery = _alert_tracker.observe(report)
    if not report.healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    body = report.as_dict()
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
