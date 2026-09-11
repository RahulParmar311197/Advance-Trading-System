from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Protocol

from .health import HealthReport


@dataclass(frozen=True, slots=True)
class Alert:
    """An operational state transition that should be surfaced to operators."""

    alert_id: str
    severity: str
    status: str
    message: str


@dataclass(frozen=True, slots=True)
class AlertDelivery:
    """Outcome of handing an alert to a notification sink."""

    delivered: bool
    detail: str


class AlertNotifier(Protocol):
    def notify(self, alert: Alert) -> AlertDelivery:
        """Deliver an alert and explicitly report delivery failure."""


class LoggingAlertNotifier:
    """Operational notifier using the application's structured logging boundary."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("advance_trading_system.alerts")

    def notify(self, alert: Alert) -> AlertDelivery:
        try:
            self._logger.error(
                "operational_alert",
                extra={
                    "alert_id": alert.alert_id,
                    "severity": alert.severity,
                    "status": alert.status,
                    "message": alert.message,
                },
            )
        except Exception as exc:
            return AlertDelivery(False, f"notification failed: {type(exc).__name__}")
        return AlertDelivery(True, "logged")


class AlertTransitionTracker:
    """Emit alerts only when overall operational health changes state."""

    def __init__(self, notifier: AlertNotifier) -> None:
        self._notifier = notifier
        self._previous_healthy: bool | None = None

    def observe(self, report: HealthReport) -> tuple[Alert | None, AlertDelivery | None]:
        current = report.healthy
        previous = self._previous_healthy
        self._previous_healthy = current

        if previous is None or previous == current:
            return None, None

        if current:
            alert = Alert(
                alert_id="operational-health-recovered",
                severity="info",
                status="recovered",
                message="Operational dependencies recovered.",
            )
        else:
            failed = ", ".join(
                component.name for component in report.components if not component.healthy
            )
            alert = Alert(
                alert_id="operational-health-degraded",
                severity="critical",
                status="degraded",
                message=f"Operational dependencies degraded: {failed}.",
            )

        return alert, self._notifier.notify(alert)
