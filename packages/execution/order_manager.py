from __future__ import annotations

from dataclasses import dataclass

from packages.execution.broker import Broker, Order, OrderRequest, OrderStatus
from packages.risk.kill_switch import KillSwitch


@dataclass(frozen=True, slots=True)
class OrderManager:
    """Application boundary for broker orders and fail-closed submission controls."""

    broker: Broker
    kill_switch: KillSwitch | None = None

    def submit(self, request: OrderRequest) -> Order:
        if self.kill_switch is not None and not self.kill_switch.allow_new_trade():
            raise RuntimeError("kill switch is active; new order submission blocked")
        return self.broker.submit_order(request)

    def cancel(self, order_id: str) -> Order:
        return self.broker.cancel_order(order_id)

    def status(self, order_id: str) -> Order:
        return self.broker.get_order(order_id)

    def require_fill(self, order_id: str) -> Order:
        """Return a filled order or fail closed without changing broker state."""
        order = self.status(order_id)
        if order.status is not OrderStatus.FILLED:
            raise RuntimeError(f"order is not filled: {order.status.value}")
        return order
