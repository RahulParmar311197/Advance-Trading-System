from datetime import datetime, timezone
from decimal import Decimal

import pytest

from packages.execution.broker import (
    Broker,
    Order,
    OrderRequest,
    OrderSide,
    OrderStatus,
    OrderType,
)


def market_request() -> OrderRequest:
    return OrderRequest(
        symbol="NIFTY",
        side=OrderSide.BUY,
        quantity=Decimal("2"),
    )


def test_order_request_accepts_market_order() -> None:
    request = market_request()
    assert request.order_type is OrderType.MARKET
    assert request.limit_price is None
    assert request.stop_price is None


def test_order_request_requires_price_for_limit_and_stop_orders() -> None:
    with pytest.raises(ValueError, match="limit_price"):
        OrderRequest("NIFTY", OrderSide.BUY, Decimal("1"), OrderType.LIMIT)
    with pytest.raises(ValueError, match="stop_price"):
        OrderRequest("NIFTY", OrderSide.SELL, Decimal("1"), OrderType.STOP)


def test_order_request_rejects_prices_for_wrong_order_type() -> None:
    with pytest.raises(ValueError, match="limit_price"):
        OrderRequest(
            "NIFTY",
            OrderSide.BUY,
            Decimal("1"),
            limit_price=Decimal("100"),
        )
    with pytest.raises(ValueError, match="stop_price"):
        OrderRequest(
            "NIFTY",
            OrderSide.BUY,
            Decimal("1"),
            stop_price=Decimal("100"),
        )


def test_order_rejects_invalid_fill_state() -> None:
    with pytest.raises(ValueError, match="within requested quantity"):
        Order("O1", market_request(), OrderStatus.ACCEPTED, Decimal("3"))

    with pytest.raises(ValueError, match="filled orders"):
        Order("O2", market_request(), OrderStatus.FILLED, Decimal("1"))

    with pytest.raises(ValueError, match="partially filled"):
        Order("O3", market_request(), OrderStatus.PARTIALLY_FILLED, Decimal("0"))

    with pytest.raises(ValueError, match="rejected orders"):
        Order("O4", market_request(), OrderStatus.REJECTED, Decimal("1"))


def test_order_accepts_valid_filled_state() -> None:
    timestamp = datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc)
    order = Order(
        "O1",
        market_request(),
        OrderStatus.FILLED,
        Decimal("2"),
        Decimal("25000"),
        submitted_at=timestamp,
    )
    assert order.filled_quantity == Decimal("2")
    assert order.average_fill_price == Decimal("25000")
    assert order.submitted_at == timestamp


def test_broker_contract_can_be_implemented_without_changing_order_types() -> None:
    class RecordingBroker(Broker):
        def __init__(self) -> None:
            self.orders: dict[str, Order] = {}

        def submit_order(self, request: OrderRequest) -> Order:
            order = Order("O1", request, OrderStatus.ACCEPTED)
            self.orders[order.order_id] = order
            return order

        def cancel_order(self, order_id: str) -> Order:
            current = self.orders[order_id]
            canceled = Order(
                current.order_id,
                current.request,
                OrderStatus.CANCELED,
                current.filled_quantity,
                current.average_fill_price,
                current.reason,
                current.submitted_at,
            )
            self.orders[order_id] = canceled
            return canceled

        def get_order(self, order_id: str) -> Order:
            return self.orders[order_id]

    broker: Broker = RecordingBroker()
    submitted = broker.submit_order(market_request())
    assert submitted.status is OrderStatus.ACCEPTED
    assert broker.get_order("O1") == submitted
    assert broker.cancel_order("O1").status is OrderStatus.CANCELED
