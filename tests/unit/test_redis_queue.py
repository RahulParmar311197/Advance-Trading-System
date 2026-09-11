from packages.queue.redis_queue import Job, JobQueue, QueueError


class FakeRedis:
    def __init__(self):
        self.lists = {}

    def rpush(self, key, value):
        self.lists.setdefault(key, []).append(value)

    def brpoplpush(self, source, destination, timeout=0):
        values = self.lists.get(source, [])
        if not values:
            return None
        value = values.pop()
        self.lists.setdefault(destination, []).insert(0, value)
        return value

    def lrem(self, key, count, value):
        values = self.lists.get(key, [])
        removed = 0
        while value in values and (count == 0 or removed < count):
            values.remove(value)
            removed += 1
        return removed


def test_queue_preserves_fifo_order_and_acknowledges():
    client = FakeRedis()
    queue = JobQueue(client)
    first = queue.enqueue("backtest", "run", {"experiment": "EXP-1"}, job_id="a")
    queue.enqueue("backtest", "run", {"experiment": "EXP-2"}, job_id="b")

    claimed = queue.claim("backtest", timeout_seconds=1)
    assert claimed == first
    queue.ack("backtest", claimed)
    assert client.lists[queue.processing_key("backtest")] == []


def test_failed_job_is_requeued_with_incremented_attempt():
    client = FakeRedis()
    queue = JobQueue(client)
    job = queue.enqueue("research", "compare", {}, job_id="a")
    claimed = queue.claim("research")
    retried = queue.retry("research", claimed)

    assert retried.id == job.id
    assert retried.attempts == 1
    assert queue.claim("research") == retried


def test_malformed_job_fails_closed():
    client = FakeRedis()
    queue = JobQueue(client)
    client.rpush(queue.key("backtest"), "not-json")
    try:
        queue.claim("backtest")
    except QueueError as exc:
        assert str(exc) == "invalid queued job"
    else:
        raise AssertionError("malformed queue payload must fail closed")


def test_backoff_is_bounded():
    assert JobQueue.backoff_seconds(0) == 1.0
    assert JobQueue.backoff_seconds(10) == 60.0
