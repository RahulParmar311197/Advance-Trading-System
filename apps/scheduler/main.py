from __future__ import annotations

import json
import os
import time
from typing import Any

import redis

from packages.queue.redis_queue import JobQueue, QueueError
from packages.scheduler.interval import IntervalScheduler, ScheduledJob


def load_schedules(raw: str) -> list[ScheduledJob]:
    """Parse the explicit JSON schedule configuration; fail closed on errors."""
    try:
        values = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("SCHEDULES_JSON must be valid JSON") from exc
    if not isinstance(values, list):
        raise ValueError("SCHEDULES_JSON must contain a JSON array")
    schedules: list[ScheduledJob] = []
    for value in values:
        if not isinstance(value, dict):
            raise ValueError("each scheduled job must be a JSON object")
        try:
            schedules.append(
                ScheduledJob(
                    name=str(value["name"]),
                    queue=str(value.get("queue", "default")),
                    job_name=str(value["job_name"]),
                    payload=dict(value.get("payload", {})),
                    interval_seconds=int(value["interval_seconds"]),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid scheduled job configuration") from exc
    names = [schedule.name for schedule in schedules]
    if len(names) != len(set(names)):
        raise ValueError("scheduled job names must be unique")
    return schedules


def build_scheduler() -> IntervalScheduler:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    raw_schedules = os.getenv("SCHEDULES_JSON", "[]")
    schedules = load_schedules(raw_schedules)
    client = redis.Redis.from_url(redis_url, decode_responses=False)
    return IntervalScheduler(JobQueue(client), schedules)


def main() -> None:
    scheduler = build_scheduler()
    while True:
        try:
            scheduler.tick()
        except QueueError:
            # Keep the schedule alive; a transient Redis outage is retried on
            # the next deadline rather than being turned into a false success.
            pass
        time.sleep(min(60.0, max(0.1, scheduler.seconds_until_next_run())))


if __name__ == "__main__":
    main()
