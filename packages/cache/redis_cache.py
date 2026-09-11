from __future__ import annotations

import json
from typing import Any, Protocol


class RedisClient(Protocol):
    def get(self, key: str) -> bytes | str | None: ...
    def setex(self, key: str, time: int, value: str) -> Any: ...
    def delete(self, key: str) -> Any: ...


class CacheError(RuntimeError):
    """Raised when a cache operation fails and the caller requests strict handling."""


class RedisCache:
    """Small JSON cache adapter with explicit namespaces and bounded TTLs.

    Cached values are never authoritative: callers should fall back to their
    source of truth when Redis is unavailable.
    """

    def __init__(self, client: RedisClient, *, namespace: str = "ats") -> None:
        if not namespace.strip():
            raise ValueError("namespace must not be empty")
        self._client = client
        self._namespace = namespace.strip()

    def key(self, resource: str, **parts: object) -> str:
        if not resource.strip():
            raise ValueError("resource must not be empty")
        normalized = json.dumps(parts, sort_keys=True, separators=(",", ":"), default=str)
        return f"{self._namespace}:{resource.strip()}:{normalized}"

    def get_json(self, key: str) -> Any | None:
        try:
            value = self._client.get(key)
            if value is None:
                return None
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            return json.loads(value)
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise CacheError("redis get failed") from exc

    def set_json(self, key: str, value: Any, *, ttl_seconds: int) -> None:
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be >= 1")
        try:
            payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
            self._client.setex(key, ttl_seconds, payload)
        except (OSError, TypeError, ValueError) as exc:
            raise CacheError("redis set failed") from exc

    def delete(self, key: str) -> None:
        try:
            self._client.delete(key)
        except OSError as exc:
            raise CacheError("redis delete failed") from exc
