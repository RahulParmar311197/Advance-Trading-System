from datetime import datetime, timedelta, timezone

import pytest

from apps.scheduler.main import load_schedules
from packages.queue.redis_queue import JobQueue
from packages.scheduler.interval import IntervalScheduler, ScheduledJob


class FakeRedis:
    def __init__(self):
        self.values = []

    def rpush(self, key, value):
        self.values.append((key, value))


def test_schedule_configuration_is_validated():
    schedules = load_schedules(
        '[{"name":"daily-backtest","queue":"default","job_name":"backtest.run",'
        '"payload":{"organization_id":"org-1"},"interval_seconds":3600}]'
    )
    assert schedules[0].job_name == "backtest.run"
    assert schedules[0].interval_seconds == 3600

    with pytest.raises(ValueError, match="valid JSON"):
        load_schedules("not-json")
    with pytest.raises(ValueError, match="JSON array"):
        load_schedules("{}")
    with pytest.raises(ValueError, match="unique"):
        load_schedules(
            '[{"name":"same","job_name":"a","interval_seconds":10},'
            '{"name":"same","job_name":"b","interval_seconds":20}]'
        )


def test_scheduler_enqueues_only_when_due():
    client = FakeRedis()
    clock = [datetime(2026, 1, 1, tzinfo=timezone.utc)]
    schedule = ScheduledJob("heartbeat", "default", "heartbeat", {"source": "scheduler"}, 60)
    scheduler = IntervalScheduler(JobQueue(client), [schedule], clock=lambda: clock[0])

    assert scheduler.tick() == []
    clock[0] += timedelta(seconds=59)
    assert scheduler.tick() == []
    clock[0] += timedelta(seconds=1)
    jobs = scheduler.tick()
    assert len(jobs) == 1
    assert jobs[0].name == "heartbeat"
    assert len(client.values) == 1


def test_scheduler_does_not_burst_after_missed_intervals():
    client = FakeRedis()
    clock = [datetime(2026, 1, 1, tzinfo=timezone.utc)]
    schedule = ScheduledJob("job", "default", "work", {}, 10)
    scheduler = IntervalScheduler(JobQueue(client), [schedule], clock=lambda: clock[0])

    clock[0] += timedelta(minutes=2)
    assert len(scheduler.tick()) == 1
    assert len(client.values) == 1
    assert scheduler.seconds_until_next_run() == pytest.approx(10)


def test_scheduler_requires_timezone_aware_clock():
    schedule = ScheduledJob("job", "default", "work", {}, 10)
    with pytest.raises(ValueError, match="timezone-aware"):
        IntervalScheduler(
            JobQueue(FakeRedis()), [schedule], clock=lambda: datetime(2026, 1, 1)
        )
