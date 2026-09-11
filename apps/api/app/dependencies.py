from __future__ import annotations

from collections.abc import Generator

import psycopg
import redis

from packages.cache.redis_cache import RedisCache

from .config import settings


def get_connection() -> Generator[psycopg.Connection, None, None]:
    """Yield one PostgreSQL connection per API request with a bounded connect timeout."""
    connection = psycopg.connect(
        settings.database_url,
        connect_timeout=settings.database_connect_timeout_seconds,
    )
    try:
        yield connection
    finally:
        connection.close()


def get_cache() -> RedisCache | None:
    """Return the configured Redis cache; development without Redis remains runnable."""
    if not settings.redis_url:
        return None
    return RedisCache(redis.Redis.from_url(settings.redis_url, decode_responses=False))
