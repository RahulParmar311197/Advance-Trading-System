from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .redis_queue import Job, JobQueue, QueueError

Handler = Callable[[dict[str, Any]], None]


class Worker:
    """Execute registered queue jobs with explicit acknowledgement/retry."""

    def __init__(self, queue: JobQueue, handlers: dict[str, Handler], *, max_attempts: int = 3) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self.queue = queue
        self.handlers = dict(handlers)
        self.max_attempts = max_attempts

    def run_once(self, queue_name: str, *, timeout_seconds: int = 5) -> bool:
        job = self.queue.claim(queue_name, timeout_seconds=timeout_seconds)
        if job is None:
            return False
        handler = self.handlers.get(job.name)
        if handler is None:
            self.queue.ack(queue_name, job)
            raise QueueError(f"no handler registered for job {job.name!r}")
        try:
            handler(job.payload)
        except Exception:
            if job.attempts + 1 >= self.max_attempts:
                self.queue.ack(queue_name, job)
            else:
                self.queue.retry(queue_name, job)
            raise
        self.queue.ack(queue_name, job)
        return True
