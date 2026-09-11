from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
import redis

from packages.monitoring.health import build_report, check_database, check_queue_depth, check_redis

from ..config import settings
from ..dependencies import get_connection

router = APIRouter()


@router.get("/health")
def health():
    """Liveness endpoint: process is running and able to answer requests."""
    return {"status": "ok", "service": "advance-trading-system"}


@router.get("/health/ready")
def readiness(response: Response, connection=Depends(get_connection)):
    """Readiness endpoint covering PostgreSQL and Redis dependencies."""
    client = redis.Redis.from_url(settings.redis_url, decode_responses=False)
    queue_key = "ats:jobs:default"
    report = build_report(
        (
            lambda: check_database(connection),
            lambda: check_redis(client),
            lambda: check_queue_depth(client, queue_key),
        )
    )
    if not report.healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return report.as_dict()
