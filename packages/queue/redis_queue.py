from __future__ import annotations

import json
import time
from dataclasses import dataclass
from uuid import uuid4
from typing import Any, Protocol


class QueueClient(Protocol):
    def rpush(self, key: str, value: str) -> Any: ...
    def blpop(self, keys: str | list[str], timeout: int = 0) -> Any: ...


class QueueError(RuntimeError):
    """Raised when a queue operation cannot be completed safely."""


@dataclass(frozen=True, slots=True)
class Job:
    id: str
    name: str
    payload: dict[str, Any]
    attempts: int = 0

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.name.strip():
            raise ValueError("job id and name must not be empty")
        if self.attempts < 0:
            raise ValueError("attempts must be >= 0")

    def encode(self) -> str:
        return json.dumps({"id": self.id, "name": self.name, "payload": self.payload,
                           "attempts": self.attempts}, sort_keys=True, separators=(",", ":"))

    @classmethod
    def decode(cls, value: bytes | str) -> "Job":
        try:
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            data = json.loads(value)
            return cls(str(data["id"]), str(data["name"]), dict(data["payload"]), int(data.get("attempts", 0)))
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise QueueError("invalid queued job") from exc


class JobQueue:
    """FIFO Redis list queue with explicit retry semantics.

    A claimed job is only removed from Redis when ``ack`` is called. Failed
    handlers can therefore be re-enqueued explicitly with an incremented
    attempt count; malformed jobs are rejected rather than silently executed.
    """

    def __init__(self, client: QueueClient, *, namespace: str = "ats:jobs") -> None:
        if not namespace.strip():
            raise ValueError("namespace must not be empty")
        self._client = client
        self._namespace = namespace.strip()

    def key(self, queue: str) -> str:
        if not queue.strip():
            raise ValueError("queue must not be empty")
        return f"{self._namespace}:{queue.strip()}"

    def enqueue(self, queue: str, name: str, payload: dict[str, Any], *, job_id: str | None = None) -> Job:
        job = Job(job_id or uuid4().hex, name, dict(payload))
        try:
            self._client.rpush(self.key(queue), job.encode())
        except (OSError, TypeError, ValueError) as exc:
            raise QueueError("redis enqueue failed") from exc
        return job

    def claim(self, queue: str, *, timeout_seconds: int = 5) -> Job | None:
        if timeout_seconds < 0:
            raise ValueError("timeout_seconds must be >= 0")
        try:
            item = self._client.blpop(self.key(queue), timeout=timeout_seconds)
        except (OSError, TypeError, ValueError) as exc:
            raise QueueError("redis claim failed") from exc
        if item is None:
            return None
        _, raw = item
        return Job.decode(raw)

    def retry(self, queue: str, job: Job) -> Job:
        retried = Job(job.id, job.name, job.payload, job.attempts + 1)
        try:
            self._client.rpush(self.key(queue), retried.encode())
        except (OSError, TypeError, ValueError) as exc:
            raise QueueError("redis retry failed") from exc
        return retried

    @staticmethod
    def backoff_seconds(attempts: int, *, base: float = 1.0, maximum: float = 60.0) -> float:
        if attempts < 0 or base <= 0 or maximum <= 0:
            raise ValueError("invalid backoff configuration")
        return min(maximum, base * (2 ** attempts))

    @staticmethod
    def sleep_before_retry(attempts: int, *, base: float = 1.0, maximum: float = 60.0) -> None:
        time.sleep(JobQueue.backoff_seconds(attempts, base=base, maximum=maximum))
