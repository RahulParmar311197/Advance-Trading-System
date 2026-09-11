from datetime import datetime, timezone
from decimal import Decimal

import pytest

from packages.execution.broker import Broker, BrokerError, Order, OrderRequest, OrderSide, OrderStatus
from packages.execution.order_manager import OrderManager
from packages.execution.paper_broker import PaperBroker, PaperFill


class RejectedBroker(Broker):
    def __init__(self) -> None:
        self.order = Order(
            order_id="REJECTED-1",
            request=OrderRequest("NIFTY", OrderSide.BUY, Decimal("1")),
            status=OrderStatus.REJECTED,
            reason="venue rejected order",
        )

    def submit_order(self, request: OrderRequest) -> Order:
        return self.order

    def cancel_order(self, order_id: str) -> Order:
        raise ValueError("rejected order cannot be canceled")

    def get_order(self, order_id: str) -> Order:
        if order_id != self.order.order_id:
            raise KeyError(order_id)
        return self.order


class FailingBroker(Broker):
    def submit_order(self, request: OrderRequest) -> Order:
        raise BrokerError("broker unavailable")

    def cancel_order(self, order_id: str) -> Order:
        raise BrokerError("broker unavailable")

    def get_order(self, order_id: str) -> Order:
        raise BrokerError("broker unavailable")


def test_order_manager_delegates_lifecycle_to_broker() -> None:
    broker = PaperBroker()
    manager = OrderManager(broker)
    order = manager.submit(OrderRequest("NIFTY", OrderSide.BUY, Decimal("1")))
    assert manager.status(order.order_id).status is OrderStatus.ACCEPTED
    with pytest.raises(RuntimeError, match="not filled"):
        manager.require_fill(order.order_id)
    filled = broker.process_fill(order.order_id, PaperFill("NIFTY", Decimal("25000"), datetime.now(timezone.utc)))
    assert manager.require_fill(filled.order_id).status is OrderStatus.FILLED


def test_order_manager_cancels_open_order() -> None:
    broker = PaperBroker()
    manager = OrderManager(broker)
    order = manager.submit(OrderRequest("NIFTY", OrderSide.SELL, Decimal("1")))
    canceled = manager.cancel(order.order_id)
    assert canceled.status is OrderStatus.CANCELED


def test_order_manager_fails_closed_for_rejected_order() -> None:
    manager = OrderManager(RejectedBroker())
    rejected = manager.submit(OrderRequest("NIFTY", OrderSide.BUY, Decimal("1")))
    assert rejected.status is OrderStatus.REJECTED
    with pytest.raises(RuntimeError, match="not filled"):
        manager.require_fill(rejected.order_id)
    with pytest.raises(ValueError, match="cannot be canceled"):
        manager.cancel(rejected.order_id)


def test_order_manager_propagates_broker_failure_without_inventing_state() -> None:
    manager = OrderManager(FailingBroker())
    request = OrderRequest("NIFTY", OrderSide.BUY, Decimal("1"))
    with pytest.raises(BrokerError, match="unavailable"):
        manager.submit(request)
    with pytest.raises(BrokerError, match="unavailable"):
        manager.status("UNKNOWN")
    with pytest.raises(BrokerError, match="unavailable"):
        manager.cancel("UNKNOWN")
