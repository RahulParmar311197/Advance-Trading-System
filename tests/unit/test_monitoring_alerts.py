from __future__ import annotations

import logging

from packages.monitoring.alerts import (
    Alert,
    AlertDelivery,
    AlertTransitionTracker,
    LoggingAlertNotifier,
)
from packages.monitoring.health import ComponentHealth, HealthReport


def report(healthy: bool) -> HealthReport:
    return HealthReport(
        (
            ComponentHealth("database", healthy, "reachable" if healthy else "OperationalError"),
            ComponentHealth("redis", healthy, "reachable" if healthy else "ConnectionError"),
        )
    )


class RecordingNotifier:
    def __init__(self, delivered: bool = True) -> None:
        self.alerts: list[Alert] = []
        self.delivered = delivered

    def notify(self, alert: Alert) -> AlertDelivery:
        self.alerts.append(alert)
        return AlertDelivery(self.delivered, "sent" if self.delivered else "failed")


def test_tracker_alerts_only_on_health_transitions() -> None:
    notifier = RecordingNotifier()
    tracker = AlertTransitionTracker(notifier)

    assert tracker.observe(report(True)) == (None, None)
    assert tracker.observe(report(True)) == (None, None)

    alert, delivery = tracker.observe(report(False))
    assert alert is not None
    assert alert.status == "degraded"
    assert "database" in alert.message
    assert delivery == AlertDelivery(True, "sent")

    assert tracker.observe(report(False)) == (None, None)

    alert, delivery = tracker.observe(report(True))
    assert alert is not None
    assert alert.status == "recovered"
    assert delivery == AlertDelivery(True, "sent")
    assert [item.status for item in notifier.alerts] == ["degraded", "recovered"]


def test_delivery_failure_is_explicit() -> None:
    notifier = RecordingNotifier(delivered=False)
    tracker = AlertTransitionTracker(notifier)

    tracker.observe(report(True))
    _, delivery = tracker.observe(report(False))

    assert delivery == AlertDelivery(False, "failed")


def test_logging_notifier_reports_success(caplog) -> None:
    logger = logging.getLogger("test-alerts")
    notifier = LoggingAlertNotifier(logger)
    alert = Alert("test", "critical", "degraded", "dependency failed")

    with caplog.at_level(logging.ERROR, logger="test-alerts"):
        result = notifier.notify(alert)

    assert result == AlertDelivery(True, "logged")
    assert "operational_alert" in caplog.text
    assert "dependency failed" in caplog.text
