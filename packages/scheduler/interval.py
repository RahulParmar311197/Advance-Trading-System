from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from packages.queue.redis_queue import Job, JobQueue, QueueError


@dataclass(frozen=True, slots=True)
class ScheduledJob:
    """Validated recurring job definition.

    Scheduling is intentionally interval-based. The scheduler owns timing;
    workers own execution, retries, and acknowledgement.
    """

    name: str
    queue: str
    job_name: str
    payload: dict[str, Any]
    interval_seconds: int

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.queue.strip() or not self.job_name.strip():
            raise ValueError("schedule name, queue, and job name must not be empty")
        if self.interval_seconds < 1:
            raise ValueError("interval_seconds must be >= 1")


class IntervalScheduler:
    """Enqueue due recurring jobs without executing application work."""

    def __init__(self, queue: JobQueue, schedules: list[ScheduledJob], *, clock=None) -> None:
        self.queue = queue
        self.schedules = tuple(schedules)
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        now = self._clock()
        if now.tzinfo is None:
            raise ValueError("scheduler clock must return timezone-aware datetimes")
        self._next_runs = {
            schedule.name: now + timedelta(seconds=schedule.interval_seconds)
            for schedule in self.schedules
        }

    def tick(self) -> list[Job]:
        """Enqueue every job whose interval has elapsed once.

        A missed interval produces one job, not a burst of catch-up jobs. The
        next deadline is advanced from the current time, preventing a restart
        or outage from flooding the queue with stale work.
        """
        now = self._clock()
        if now.tzinfo is None:
            raise ValueError("scheduler clock must return timezone-aware datetimes")
        created: list[Job] = []
        for schedule in self.schedules:
            due = self._next_runs[schedule.name]
            if now < due:
                continue
            job = self.queue.enqueue(schedule.queue, schedule.job_name, schedule.payload)
            created.append(job)
            self._next_runs[schedule.name] = now + timedelta(seconds=schedule.interval_seconds)
        return created

    def seconds_until_next_run(self) -> float:
        if not self._next_runs:
            return 60.0
        now = self._clock()
        return max(0.0, min((deadline - now).total_seconds() for deadline in self._next_runs.values()))
