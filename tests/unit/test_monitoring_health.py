from packages.monitoring.health import build_report, check_database, check_queue_depth, check_redis


class Cursor:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, query):
        assert query == "SELECT 1"

    def fetchone(self):
        return (1,)


class Database:
    def cursor(self):
        return Cursor()


class BrokenDatabase:
    def cursor(self):
        raise OSError("down")


class Redis:
    def __init__(self, *, healthy=True, depth=0):
        self.healthy = healthy
        self.depth = depth

    def ping(self):
        if not self.healthy:
            raise OSError("down")
        return True

    def llen(self, key):
        assert key == "ats:jobs:default"
        return self.depth


def test_health_checks_report_component_state():
    assert check_database(Database()).healthy
    assert check_redis(Redis(depth=3)).healthy
    assert check_queue_depth(Redis(depth=3), "ats:jobs:default").detail == "depth=3"
    assert not check_database(BrokenDatabase()).healthy
    assert not check_redis(Redis(healthy=False)).healthy


def test_health_report_is_degraded_when_any_component_fails():
    report = build_report((lambda: check_database(Database()), lambda: check_redis(Redis(healthy=False))))
    assert not report.healthy
    assert report.as_dict()["status"] == "degraded"
    assert report.as_dict()["components"]["redis"]["status"] == "error"
