from decimal import Decimal

import pytest

from packages.execution.broker import OrderRequest, OrderSide, OrderStatus
from packages.execution.live_broker import LiveBroker, LiveBrokerConfig


class RecordingTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def submit_order(self, request: OrderRequest):
        self.calls.append(("submit", request))
        from packages.execution.broker import Order

        return Order(order_id="LIVE-1", request=request, status=OrderStatus.ACCEPTED)

    def cancel_order(self, order_id: str):
        self.calls.append(("cancel", order_id))
        raise NotImplementedError

    def get_order(self, order_id: str):
        self.calls.append(("get", order_id))
        raise NotImplementedError


def test_live_broker_is_disabled_by_default() -> None:
    broker = LiveBroker()
    with pytest.raises(RuntimeError, match="disabled"):
        broker.submit_order(OrderRequest("NIFTY", OrderSide.BUY, Decimal("1")))


def test_enabled_live_broker_requires_explicit_transport() -> None:
    with pytest.raises(ValueError, match="explicit transport"):
        LiveBroker(config=LiveBrokerConfig(enabled=True))


def test_enabled_adapter_delegates_only_to_supplied_transport() -> None:
    transport = RecordingTransport()
    broker = LiveBroker(transport, LiveBrokerConfig(enabled=True))
    request = OrderRequest("NIFTY", OrderSide.SELL, Decimal("2"))
    order = broker.submit_order(request)
    assert order.order_id == "LIVE-1"
    assert transport.calls == [("submit", request)]
