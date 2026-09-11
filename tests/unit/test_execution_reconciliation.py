from decimal import Decimal

import pytest

from packages.execution.broker import OrderRequest, OrderSide, OrderStatus
from packages.execution.reconciliation import ReconciliationIssueType, reconcile_orders


def order(
    order_id: str,
    status: OrderStatus = OrderStatus.ACCEPTED,
    filled_quantity: str = "0",
    average_fill_price: str | None = None,
):
    from packages.execution.broker import Order

    return Order(
        order_id=order_id,
        request=OrderRequest("NIFTY", OrderSide.BUY, Decimal("2")),
        status=status,
        filled_quantity=Decimal(filled_quantity),
        average_fill_price=(None if average_fill_price is None else Decimal(average_fill_price)),
    )


def test_identical_order_sets_reconcile() -> None:
    expected = [order("A"), order("B", OrderStatus.FILLED, "2", "25000")]
    result = reconcile_orders(expected, list(expected))
    assert result.reconciled
    assert not result.fail_closed
    assert result.matched_order_ids == ("A", "B")


def test_missing_and_unexpected_orders_fail_closed() -> None:
    result = reconcile_orders([order("A")], [order("B")])
    assert result.fail_closed
    assert {(issue.order_id, issue.issue_type) for issue in result.issues} == {
        ("A", ReconciliationIssueType.MISSING_OBSERVED),
        ("B", ReconciliationIssueType.UNEXPECTED_OBSERVED),
    }


def test_state_and_fill_differences_are_reported() -> None:
    expected = order("A", OrderStatus.ACCEPTED)
    observed = order("A", OrderStatus.FILLED, "2", "25000")
    result = reconcile_orders([expected], [observed])
    assert {issue.issue_type for issue in result.issues} == {
        ReconciliationIssueType.STATUS_MISMATCH,
        ReconciliationIssueType.FILLED_QUANTITY_MISMATCH,
        ReconciliationIssueType.AVERAGE_FILL_PRICE_MISMATCH,
    }
    assert not result.reconciled


def test_duplicate_order_ids_are_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate expected order id"):
        reconcile_orders([order("A"), order("A")], [])
    with pytest.raises(ValueError, match="duplicate observed order id"):
        reconcile_orders([], [order("A"), order("A")])
