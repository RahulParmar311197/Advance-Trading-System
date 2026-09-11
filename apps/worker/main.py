from __future__ import annotations

import os

import redis

from packages.queue.redis_queue import JobQueue, QueueError
from packages.queue.worker import Worker


def build_worker() -> tuple[Worker, str]:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    queue_name = os.getenv("QUEUE_NAME", "default")
    max_attempts = int(os.getenv("QUEUE_MAX_ATTEMPTS", "3"))
    client = redis.Redis.from_url(redis_url, decode_responses=False)
    return Worker(JobQueue(client), {} , max_attempts=max_attempts), queue_name


def main() -> None:
    worker, queue_name = build_worker()
    while True:
        try:
            worker.run_once(queue_name, timeout_seconds=5)
        except QueueError as exc:
            raise SystemExit(f"worker stopped: {exc}") from exc
        except Exception:
            # Job handlers own their retry policy; an unhandled job failure
            # should not be converted into a successful acknowledgement.
            continue


if __name__ == "__main__":
    main()
