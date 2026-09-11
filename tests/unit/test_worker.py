import pytest

from packages.queue.redis_queue import JobQueue, QueueError
from packages.queue.worker import Worker


class FakeRedis:
    def __init__(self):
        self.lists = {}

    def lpush(self, key, value):
        self.lists.setdefault(key, []).insert(0, value)

    def rpush(self, key, value):
        self.lists.setdefault(key, []).append(value)

    def brpoplpush(self, source, destination, timeout=0):
        if not self.lists.get(source):
            return None
        value = self.lists[source].pop()
        self.lists.setdefault(destination, []).insert(0, value)
        return value

    def lrem(self, key, count, value):
        values = self.lists.get(key, [])
        if value not in values:
            return 0
        values.remove(value)
        return 1


def test_worker_acknowledges_successful_job():
    redis = FakeRedis()
    queue = JobQueue(redis)
    seen = []
    queue.enqueue("backtest", "run", {"id": "EXP-1"}, job_id="a")
    worker = Worker(queue, {"run": lambda payload: seen.append(payload)})

    assert worker.run_once("backtest") is True
    assert seen == [{"id": "EXP-1"}]
    assert redis.lists[queue.processing_key("backtest")] == []


def test_worker_requeues_retryable_failure():
    redis = FakeRedis()
    queue = JobQueue(redis)
    queue.enqueue("research", "fail", {}, job_id="a")
    worker = Worker(queue, {"fail": lambda _payload: (_ for _ in ()).throw(RuntimeError("boom"))}, max_attempts=3)

    with pytest.raises(RuntimeError):
        worker.run_once("research")
    assert queue.claim("research").attempts == 1


def test_worker_does_not_retry_after_max_attempts():
    redis = FakeRedis()
    queue = JobQueue(redis)
    queue.enqueue("research", "fail", {}, job_id="a")
    worker = Worker(queue, {"fail": lambda _payload: (_ for _ in ()).throw(RuntimeError("boom"))}, max_attempts=1)

    with pytest.raises(RuntimeError):
        worker.run_once("research")
    assert redis.lists[queue.key("research")] == []
    assert redis.lists[queue.processing_key("research")] == []


def test_unknown_job_type_fails_closed_and_is_not_retried():
    redis = FakeRedis()
    queue = JobQueue(redis)
    queue.enqueue("research", "unknown", {}, job_id="a")
    worker = Worker(queue, {})

    with pytest.raises(QueueError, match="no handler"):
        worker.run_once("research")
    assert redis.lists[queue.processing_key("research")] == []
