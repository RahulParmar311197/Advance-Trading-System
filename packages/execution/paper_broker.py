from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from itertools import count

from packages.execution.broker import Broker, Order, OrderRequest, OrderSide, OrderStatus, OrderType
from packages.execution.execution_simulator import ExecutionObservation, simulate_fill


@dataclass(frozen=True, slots=True)
class PaperFill:
    """Explicit market observation used to fill paper orders."""

    symbol: str
    price: Decimal
    timestamp: datetime
    quantity: Decimal | None = None

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")
        if self.price <= 0:
            raise ValueError("price must be positive")
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        if self.quantity is not None and self.quantity <= 0:
            raise ValueError("fill quantity must be positive")


class PaperBroker(Broker):
    """Deterministic paper broker driven only by explicitly supplied prices."""

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._sequence = count(1)

    def submit_order(self, request: OrderRequest) -> Order:
        order_id = request.client_order_id or f"PAPER-{next(self._sequence):08d}"
        if order_id in self._orders:
            raise ValueError(f"order already exists: {order_id}")
        order = Order(
            order_id=order_id,
            request=request,
            status=OrderStatus.ACCEPTED,
            submitted_at=datetime.now(timezone.utc),
        )
        self._orders[order_id] = order
        return order

    def cancel_order(self, order_id: str) -> Order:
        order = self.get_order(order_id)
        if order.status in {OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.REJECTED}:
            raise ValueError(f"order cannot be canceled in state: {order.status.value}")
        canceled = Order(
            order_id=order.order_id,
            request=order.request,
            status=OrderStatus.CANCELED,
            filled_quantity=order.filled_quantity,
            average_fill_price=order.average_fill_price,
            reason="canceled by caller",
            submitted_at=order.submitted_at,
        )
        self._orders[order_id] = canceled
        return canceled

    def get_order(self, order_id: str) -> Order:
        if not order_id.strip():
            raise ValueError("order_id must not be empty")
        try:
            return self._orders[order_id]
        except KeyError as exc:
            raise KeyError(f"unknown order: {order_id}") from exc

    def process_fill(self, order_id: str, fill: PaperFill) -> Order:
        """Apply one explicit observed price and quantity to an eligible order."""
        order = self.get_order(order_id)
        if order.status not in {OrderStatus.ACCEPTED, OrderStatus.PARTIALLY_FILLED}:
            raise ValueError(f"order is not fillable in state: {order.status.value}")
        if fill.symbol != order.request.symbol:
            raise ValueError("fill symbol does not match order symbol")
        if not self._triggered(order.request, fill.price):
            return order

        remaining = order.request.quantity - order.filled_quantity
        fill_quantity = remaining if fill.quantity is None else fill.quantity
        if fill_quantity > remaining:
            raise ValueError("fill quantity exceeds remaining order quantity")
        if fill_quantity <= 0:
            raise ValueError("fill quantity must be positive")

        total_filled = order.filled_quantity + fill_quantity
        weighted_value = Decimal("0")
        if order.filled_quantity and order.average_fill_price is not None:
            weighted_value += order.filled_quantity * order.average_fill_price
        weighted_value += fill_quantity * fill.price
        average_price = weighted_value / total_filled
        status = (
            OrderStatus.FILLED
            if total_filled == order.request.quantity
            else OrderStatus.PARTIALLY_FILLED
        )
        updated = Order(
            order_id=order.order_id,
            request=order.request,
            status=status,
            filled_quantity=total_filled,
            average_fill_price=average_price,
            submitted_at=order.submitted_at,
        )
        self._orders[order_id] = updated
        return updated

    def process_observation(
        self,
        order_id: str,
        observation: ExecutionObservation,
        *,
        slippage_bps: Decimal = Decimal("0"),
    ) -> Order:
        """Simulate and apply a fill from one explicitly supplied observation."""
        order = self.get_order(order_id)
        simulated = simulate_fill(order.request, observation, slippage_bps=slippage_bps)
        if simulated is None:
            return order
        return self.process_fill(
            order_id,
            PaperFill(simulated.symbol, simulated.price, simulated.timestamp),
        )

    @staticmethod
    def _triggered(request: OrderRequest, price: Decimal) -> bool:
        if request.order_type is OrderType.MARKET:
            return True
        if request.order_type is OrderType.LIMIT:
            if request.limit_price is None:
                raise ValueError("limit order is missing limit_price")
            return price <= request.limit_price if request.side is OrderSide.BUY else price >= request.limit_price
        if request.stop_price is None:
            raise ValueError("stop order is missing stop_price")
        return price >= request.stop_price if request.side is OrderSide.BUY else price <= request.stop_price
