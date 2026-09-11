from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

from packages.execution.broker import Order, OrderStatus
from packages.execution.reconciliation import ReconciliationResult


class ExecutionHealth(StrEnum):
    HEALTHY = "healthy"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class ExecutionMonitorReport:
    """Deterministic execution-health assessment from explicit state."""

    health: ExecutionHealth
    stale_order_ids: tuple[str, ...]
    unresolved_reconciliation: bool
    missing_timestamps: tuple[str, ...]

    @property
    def can_submit_new_orders(self) -> bool:
        return self.health is ExecutionHealth.HEALTHY


@dataclass(frozen=True, slots=True)
class ExecutionMonitor:
    """Fail-closed monitor for open-order staleness and reconciliation state."""

    stale_after: timedelta

    def __post_init__(self) -> None:
        if self.stale_after <= timedelta(0):
            raise ValueError("stale_after must be positive")

    def assess(
        self,
        orders: list[Order] | tuple[Order, ...],
        *,
        now: datetime,
        reconciliation: ReconciliationResult | None = None,
    ) -> ExecutionMonitorReport:
        """Assess only explicitly supplied order/reconciliation observations."""
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        stale: list[str] = []
        missing_timestamps: list[str] = []
        open_statuses = {OrderStatus.ACCEPTED, OrderStatus.PARTIALLY_FILLED}
        for order in orders:
            if order.status not in open_statuses:
                continue
            if order.submitted_at is None:
                missing_timestamps.append(order.order_id)
                continue
            if now - order.submitted_at >= self.stale_after:
                stale.append(order.order_id)

        stale_ids = tuple(sorted(stale))
        missing_ids = tuple(sorted(missing_timestamps))
        unresolved = reconciliation is not None and not reconciliation.reconciled
        health = ExecutionHealth.BLOCKED if stale_ids or missing_ids or unresolved else ExecutionHealth.HEALTHY
        return ExecutionMonitorReport(health, stale_ids, unresolved, missing_ids)
