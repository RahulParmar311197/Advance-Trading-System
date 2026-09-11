from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from packages.execution.broker import Broker, BrokerError, Order, OrderRequest


class LiveBrokerTransport(Protocol):
    """Provider-owned transport that returns broker-observed order state."""

    def submit_order(self, request: OrderRequest) -> Order: ...

    def cancel_order(self, order_id: str) -> Order: ...

    def get_order(self, order_id: str) -> Order: ...


@dataclass(frozen=True, slots=True)
class LiveBrokerConfig:
    """Explicit live-execution gate; disabled is the safe default."""

    enabled: bool = False


class LiveBroker(Broker):
    """Broker adapter with explicit live gating and network-failure translation."""

    def __init__(self, transport: LiveBrokerTransport | None = None, config: LiveBrokerConfig | None = None) -> None:
        self._transport = transport
        self._config = config or LiveBrokerConfig()
        if self._config.enabled and self._transport is None:
            raise ValueError("enabled live broker requires an explicit transport")

    def submit_order(self, request: OrderRequest) -> Order:
        try:
            return self._require_transport().submit_order(request)
        except (ConnectionError, TimeoutError, OSError) as exc:
            raise BrokerError("live broker transport unavailable during submission") from exc

    def cancel_order(self, order_id: str) -> Order:
        try:
            return self._require_transport().cancel_order(order_id)
        except (ConnectionError, TimeoutError, OSError) as exc:
            raise BrokerError("live broker transport unavailable during cancellation") from exc

    def get_order(self, order_id: str) -> Order:
        try:
            return self._require_transport().get_order(order_id)
        except (ConnectionError, TimeoutError, OSError) as exc:
            raise BrokerError("live broker transport unavailable during status query") from exc

    def _require_transport(self) -> LiveBrokerTransport:
        if not self._config.enabled:
            raise RuntimeError("live broker is disabled")
        if self._transport is None:
            raise RuntimeError("live broker transport is not configured")
        return self._transport
