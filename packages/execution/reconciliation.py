from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Iterable

from packages.execution.broker import Order


class ReconciliationIssueType(StrEnum):
    MISSING_OBSERVED = "missing_observed"
    UNEXPECTED_OBSERVED = "unexpected_observed"
    STATUS_MISMATCH = "status_mismatch"
    FILLED_QUANTITY_MISMATCH = "filled_quantity_mismatch"
    AVERAGE_FILL_PRICE_MISMATCH = "average_fill_price_mismatch"


@dataclass(frozen=True, slots=True)
class ReconciliationIssue:
    """One deterministic difference between expected and broker-observed state."""

    order_id: str
    issue_type: ReconciliationIssueType
    expected: str | None
    observed: str | None


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    """Complete reconciliation result; unresolved issues fail closed."""

    matched_order_ids: tuple[str, ...]
    issues: tuple[ReconciliationIssue, ...]

    @property
    def reconciled(self) -> bool:
        return not self.issues

    @property
    def fail_closed(self) -> bool:
        return bool(self.issues)


def reconcile_orders(
    expected_orders: Iterable[Order], observed_orders: Iterable[Order]
) -> ReconciliationResult:
    """Compare locally expected orders with explicitly broker-observed orders.

    The function performs no state repair and invents no broker state. Duplicate
    order IDs are rejected because reconciliation cannot safely determine which
    observation is authoritative.
    """
    expected = _index_orders(expected_orders, "expected")
    observed = _index_orders(observed_orders, "observed")
    issues: list[ReconciliationIssue] = []
    matched: list[str] = []

    for order_id in sorted(expected.keys() | observed.keys()):
        local = expected.get(order_id)
        remote = observed.get(order_id)
        if local is None:
            issues.append(
                ReconciliationIssue(
                    order_id, ReconciliationIssueType.UNEXPECTED_OBSERVED, None, remote.status.value
                )
            )
            continue
        if remote is None:
            issues.append(
                ReconciliationIssue(
                    order_id, ReconciliationIssueType.MISSING_OBSERVED, local.status.value, None
                )
            )
            continue
        if local.status is not remote.status:
            issues.append(
                ReconciliationIssue(
                    order_id,
                    ReconciliationIssueType.STATUS_MISMATCH,
                    local.status.value,
                    remote.status.value,
                )
            )
        if local.filled_quantity != remote.filled_quantity:
            issues.append(
                ReconciliationIssue(
                    order_id,
                    ReconciliationIssueType.FILLED_QUANTITY_MISMATCH,
                    str(local.filled_quantity),
                    str(remote.filled_quantity),
                )
            )
        if local.average_fill_price != remote.average_fill_price:
            issues.append(
                ReconciliationIssue(
                    order_id,
                    ReconciliationIssueType.AVERAGE_FILL_PRICE_MISMATCH,
                    _decimal_text(local.average_fill_price),
                    _decimal_text(remote.average_fill_price),
                )
            )
        if not any(issue.order_id == order_id for issue in issues):
            matched.append(order_id)

    return ReconciliationResult(tuple(matched), tuple(issues))


def _index_orders(orders: Iterable[Order], side: str) -> dict[str, Order]:
    indexed: dict[str, Order] = {}
    for order in orders:
        if order.order_id in indexed:
            raise ValueError(f"duplicate {side} order id: {order.order_id}")
        indexed[order.order_id] = order
    return indexed


def _decimal_text(value: Decimal | None) -> str | None:
    return None if value is None else str(value)
