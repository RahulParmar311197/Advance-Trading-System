from decimal import Decimal

import pytest

from packages.execution.broker import OrderRequest, OrderSide, OrderStatus
from packages.execution.order_manager import OrderManager
from packages.execution.paper_broker import PaperBroker, PaperFill
from datetime import datetime, timezone


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
