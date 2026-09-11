from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class BrokerError(RuntimeError):
    """Recoverable broker/venue failure; callers must fail closed."""


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


class OrderStatus(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"


@dataclass(frozen=True, slots=True)
class OrderRequest:
    """Validated broker-independent order intent."""

    symbol: str
    side: OrderSide
    quantity: Decimal
    order_type: OrderType = OrderType.MARKET
    limit_price: Decimal | None = None
    stop_price: Decimal | None = None
    client_order_id: str | None = None

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.order_type is OrderType.LIMIT:
            if self.limit_price is None or self.limit_price <= 0:
                raise ValueError("limit orders require a positive limit_price")
        elif self.limit_price is not None:
            raise ValueError("limit_price is only valid for limit orders")
        if self.order_type is OrderType.STOP:
            if self.stop_price is None or self.stop_price <= 0:
                raise ValueError("stop orders require a positive stop_price")
        elif self.stop_price is not None:
            raise ValueError("stop_price is only valid for stop orders")
        if self.client_order_id is not None and not self.client_order_id.strip():
            raise ValueError("client_order_id must not be empty")


@dataclass(frozen=True, slots=True)
class Order:
    """Broker-neutral order state returned by execution adapters."""

    order_id: str
    request: OrderRequest
    status: OrderStatus
    filled_quantity: Decimal = Decimal("0")
    average_fill_price: Decimal | None = None
    reason: str | None = None
    submitted_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.order_id.strip():
            raise ValueError("order_id must not be empty")
        if self.filled_quantity < 0 or self.filled_quantity > self.request.quantity:
            raise ValueError("filled_quantity must be within requested quantity")
        if self.average_fill_price is not None and self.average_fill_price <= 0:
            raise ValueError("average_fill_price must be positive")
        if self.status is OrderStatus.FILLED and self.filled_quantity != self.request.quantity:
            raise ValueError("filled orders must have the requested quantity filled")
        if self.status is OrderStatus.PARTIALLY_FILLED and not (
            Decimal("0") < self.filled_quantity < self.request.quantity
        ):
            raise ValueError("partially filled orders require a partial quantity")
        if self.status is OrderStatus.REJECTED and self.filled_quantity != 0:
            raise ValueError("rejected orders cannot contain a fill")


class Broker(ABC):
    """Stable broker contract shared by paper and live execution adapters.

    Implementations must return the broker's observed order state and must not
    manufacture fills when the underlying execution venue did not provide one.
    Broker failures should raise ``BrokerError`` so application layers can fail
    closed without treating an unavailable venue as an executed order.
    """

    @abstractmethod
    def submit_order(self, request: OrderRequest) -> Order:
        """Submit an order and return the broker's observed state."""
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> Order:
        """Cancel an open order and return its resulting broker-observed state."""
        raise NotImplementedError

    @abstractmethod
    def get_order(self, order_id: str) -> Order:
        """Return the current state of a previously submitted order."""
        raise NotImplementedError
