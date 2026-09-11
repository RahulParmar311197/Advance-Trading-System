from decimal import Decimal

import pytest

from packages.execution.broker import OrderRequest, OrderSide
from packages.execution.order_manager import OrderManager
from packages.execution.paper_broker import PaperBroker
from packages.risk.kill_switch import KillSwitch


def test_order_manager_blocks_new_submissions_when_kill_switch_active() -> None:
    broker = PaperBroker()
    kill_switch = KillSwitch()
    manager = OrderManager(broker, kill_switch=kill_switch)
    request = OrderRequest("NIFTY", OrderSide.BUY, Decimal("1"))

    kill_switch.activate()
    with pytest.raises(RuntimeError, match="kill switch is active"):
        manager.submit(request)

    assert broker.orders == ()


def test_order_manager_allows_submission_after_kill_switch_deactivation() -> None:
    kill_switch = KillSwitch()
    manager = OrderManager(PaperBroker(), kill_switch=kill_switch)
    request = OrderRequest("NIFTY", OrderSide.SELL, Decimal("2"))

    kill_switch.activate()
    kill_switch.deactivate()
    order = manager.submit(request)

    assert order.request == request


def test_kill_switch_does_not_block_existing_order_lifecycle() -> None:
    broker = PaperBroker()
    kill_switch = KillSwitch()
    manager = OrderManager(broker, kill_switch=kill_switch)
    request = OrderRequest("NIFTY", OrderSide.BUY, Decimal("1"))
    order = manager.submit(request)

    kill_switch.activate()

    assert manager.status(order.order_id) == order
    canceled = manager.cancel(order.order_id)
    assert canceled.status.value == "canceled"
