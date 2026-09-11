from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class BillingContractError(ValueError):
    """Raised when a billing event violates the internal billing contract."""


@dataclass(frozen=True, slots=True)
class BillingEvent:
    event_id: str
    organization_id: str
    event_type: str
    occurred_at: datetime
    provider_reference: str
    status: str

    def __post_init__(self) -> None:
        for name in ("event_id", "organization_id", "event_type", "provider_reference", "status"):
            if not getattr(self, name).strip():
                raise BillingContractError(f"{name} must be non-empty")
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise BillingContractError("occurred_at must be timezone-aware")


class BillingEventSink(Protocol):
    def record(self, event: BillingEvent) -> None:
        """Persist one already-authenticated provider event idempotently."""


class InMemoryBillingEventSink:
    """Deterministic contract fixture; not a payment-provider implementation."""

    def __init__(self) -> None:
        self._events: dict[str, BillingEvent] = {}

    def record(self, event: BillingEvent) -> None:
        existing = self._events.get(event.event_id)
        if existing is not None and existing != event:
            raise BillingContractError("event_id already exists with different payload")
        self._events[event.event_id] = event

    def get(self, event_id: str) -> BillingEvent | None:
        return self._events.get(event_id)


class BillingService:
    """Application boundary for authorized billing events.

    Provider-specific authentication and signature verification must happen
    before this service is called. The service deliberately accepts no raw
    provider payload and creates no billing events itself.
    """

    def __init__(self, sink: BillingEventSink) -> None:
        self._sink = sink

    def ingest(self, event: BillingEvent) -> BillingEvent:
        self._sink.record(event)
        return event
