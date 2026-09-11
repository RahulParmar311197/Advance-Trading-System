from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


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


class PostgreSQLBillingEventSink:
    """Persist normalized billing events in PostgreSQL with idempotent semantics.

    The sink receives only :class:`BillingEvent` instances. Provider credentials,
    webhook signatures, and raw provider payloads must be handled by the
    provider adapter before this boundary is called.
    """

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def record(self, event: BillingEvent) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO billing_events
                   (event_id, organization_id, event_type, occurred_at,
                    provider_reference, status)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON CONFLICT (event_id) DO NOTHING""",
                (
                    event.event_id,
                    event.organization_id,
                    event.event_type,
                    event.occurred_at,
                    event.provider_reference,
                    event.status,
                ),
            )
            cursor.execute(
                """SELECT event_id, organization_id, event_type, occurred_at,
                          provider_reference, status
                   FROM billing_events
                   WHERE event_id=%s""",
                (event.event_id,),
            )
            row = cursor.fetchone()
        self._connection.commit()

        if row is None:
            raise BillingContractError("billing event could not be persisted")

        stored = BillingEvent(
            event_id=str(row[0]),
            organization_id=str(row[1]),
            event_type=str(row[2]),
            occurred_at=row[3],
            provider_reference=str(row[4]),
            status=str(row[5]),
        )
        if stored != event:
            raise BillingContractError("event_id already exists with different payload")

    def get(self, event_id: str) -> BillingEvent | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """SELECT event_id, organization_id, event_type, occurred_at,
                          provider_reference, status
                   FROM billing_events
                   WHERE event_id=%s""",
                (event_id,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        return BillingEvent(
            event_id=str(row[0]),
            organization_id=str(row[1]),
            event_type=str(row[2]),
            occurred_at=row[3],
            provider_reference=str(row[4]),
            status=str(row[5]),
        )


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
