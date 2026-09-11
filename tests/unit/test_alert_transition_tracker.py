from packages.monitoring.alerts import (
    AlertTransitionTracker,
    AlertDelivery,
    Alert,
)
from packages.monitoring.health import ComponentHealth, HealthReport


class Notifier:
    def __init__(self) -> None:
        self.alerts: list[Alert] = []

    def notify(self, alert: Alert) -> AlertDelivery:
        self.alerts.append(alert)
        return AlertDelivery(True, "test-delivered")


def report(*, healthy: bool) -> HealthReport:
    return HealthReport(
        (
            ComponentHealth("database", healthy, "reachable" if healthy else "down"),
            ComponentHealth("redis", healthy, "reachable" if healthy else "down"),
        )
    )


def test_tracker_emits_only_on_health_transition() -> None:
    notifier = Notifier()
    tracker = AlertTransitionTracker(notifier)

    assert tracker.observe(report(healthy=True)) == (None, None)
    alert, delivery = tracker.observe(report(healthy=False))
    assert alert is not None
    assert alert.alert_id == "operational-health-degraded"
    assert alert.severity == "critical"
    assert alert.status == "degraded"
    assert "database, redis" in alert.message
    assert delivery == AlertDelivery(True, "test-delivered")

    assert tracker.observe(report(healthy=False)) == (None, None)
    alert, delivery = tracker.observe(report(healthy=True))
    assert alert is not None
    assert alert.alert_id == "operational-health-recovered"
    assert alert.severity == "info"
    assert alert.status == "recovered"
    assert delivery == AlertDelivery(True, "test-delivered")
    assert len(notifier.alerts) == 2


def test_tracker_surfaces_notification_failure() -> None:
    class BrokenNotifier:
        def notify(self, alert: Alert) -> AlertDelivery:
            return AlertDelivery(False, "notification failed: RuntimeError")

    tracker = AlertTransitionTracker(BrokenNotifier())
    tracker.observe(report(healthy=True))
    alert, delivery = tracker.observe(report(healthy=False))

    assert alert is not None
    assert delivery == AlertDelivery(False, "notification failed: RuntimeError")
