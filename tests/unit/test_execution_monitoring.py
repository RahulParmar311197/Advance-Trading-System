from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from packages.execution.broker import Order, OrderRequest, OrderSide, OrderStatus
from packages.execution.monitoring import ExecutionHealth, ExecutionMonitor
from packages.execution.reconciliation import reconcile_orders

NOW = datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)


def make_order(
    order_id: str,
    status: OrderStatus,
    submitted_at: datetime | None,
    *,
    filled_quantity: Decimal = Decimal("0"),
    average_fill_price: Decimal | None = None,
) -> Order:
    return Order(
        order_id=order_id,
        request=OrderRequest("NIFTY", OrderSide.BUY, Decimal("1")),
        status=status,
        filled_quantity=filled_quantity,
        average_fill_price=average_fill_price,
        submitted_at=submitted_at,
    )


def test_healthy_monitor_allows_new_orders() -> None:
    monitor = ExecutionMonitor(timedelta(minutes=5))
    report = monitor.assess(
        [make_order("A", OrderStatus.ACCEPTED, NOW - timedelta(minutes=1))],
        now=NOW,
    )
    assert report.health is ExecutionHealth.HEALTHY
    assert report.can_submit_new_orders


def test_stale_and_missing_timestamps_block_new_orders() -> None:
    monitor = ExecutionMonitor(timedelta(minutes=5))
    report = monitor.assess(
        [
            make_order("STALE", OrderStatus.ACCEPTED, NOW - timedelta(minutes=5)),
            make_order(
                "UNKNOWN",
                OrderStatus.PARTIALLY_FILLED,
                None,
                filled_quantity=Decimal("0.5"),
                average_fill_price=Decimal("25000"),
            ),
            make_order(
                "FILLED",
                OrderStatus.FILLED,
                None,
                filled_quantity=Decimal("1"),
                average_fill_price=Decimal("25000"),
            ),
        ],
        now=NOW,
    )
    assert report.health is ExecutionHealth.BLOCKED
    assert not report.can_submit_new_orders
    assert report.stale_order_ids == ("STALE",)
    assert report.missing_timestamps == ("UNKNOWN",)


def test_reconciliation_failure_blocks_new_orders() -> None:
    monitor = ExecutionMonitor(timedelta(minutes=5))
    expected = make_order("A", OrderStatus.ACCEPTED, NOW)
    observed = make_order(
        "A",
        OrderStatus.FILLED,
        NOW,
        filled_quantity=Decimal("1"),
        average_fill_price=Decimal("25000"),
    )
    reconciliation = reconcile_orders([expected], [observed])
    report = monitor.assess([], now=NOW, reconciliation=reconciliation)
    assert report.health is ExecutionHealth.BLOCKED
    assert report.unresolved_reconciliation


def test_recovery_requires_a_clean_reconciliation_before_unblocking() -> None:
    monitor = ExecutionMonitor(timedelta(minutes=5))
    expected = make_order("A", OrderStatus.FILLED, NOW)
    mismatched = make_order(
        "A",
        OrderStatus.FILLED,
        NOW,
        filled_quantity=Decimal("1"),
        average_fill_price=Decimal("25001"),
    )
    blocked = monitor.assess([], now=NOW, reconciliation=reconcile_orders([expected], [mismatched]))
    assert blocked.health is ExecutionHealth.BLOCKED
    assert not blocked.can_submit_new_orders

    reconciled = reconcile_orders([expected], [expected])
    recovered = monitor.assess([], now=NOW, reconciliation=reconciled)
    assert recovered.health is ExecutionHealth.HEALTHY
    assert recovered.can_submit_new_orders


def test_naive_now_and_invalid_timeout_fail_closed() -> None:
    with pytest.raises(ValueError, match="positive"):
        ExecutionMonitor(timedelta(0))
    monitor = ExecutionMonitor(timedelta(minutes=5))
    with pytest.raises(ValueError, match="timezone-aware"):
        monitor.assess([], now=datetime(2026, 1, 2, 10, 0))
