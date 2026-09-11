from datetime import datetime, timezone

import pytest

from packages.saas.billing import (
    BillingContractError,
    BillingEvent,
    PostgreSQLBillingEventSink,
)


class FakeCursor:
    def __init__(self, row=None):
        self.row = row
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params):
        self.executed.append((query, params))

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self, row=None):
        self.cursor_instance = FakeCursor(row)
        self.commits = 0

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commits += 1


def _event() -> BillingEvent:
    return BillingEvent(
        event_id="evt-1",
        organization_id="org-1",
        event_type="invoice.paid",
        occurred_at=datetime(2026, 9, 11, 8, 0, tzinfo=timezone.utc),
        provider_reference="provider-ref-1",
        status="paid",
    )


def _row(event: BillingEvent, *, status: str | None = None):
    return (
        event.event_id,
        event.organization_id,
        event.event_type,
        event.occurred_at,
        event.provider_reference,
        status or event.status,
    )


def test_postgres_sink_uses_parameterized_idempotent_insert():
    event = _event()
    connection = FakeConnection(_row(event))

    PostgreSQLBillingEventSink(connection).record(event)

    insert_query, insert_params = connection.cursor_instance.executed[0]
    assert "ON CONFLICT (event_id) DO NOTHING" in insert_query
    assert insert_params == (
        event.event_id,
        event.organization_id,
        event.event_type,
        event.occurred_at,
        event.provider_reference,
        event.status,
    )
    assert connection.cursor_instance.executed[1][1] == (event.event_id,)
    assert connection.commits == 1


def test_postgres_sink_accepts_replayed_identical_event():
    event = _event()
    connection = FakeConnection(_row(event))
    sink = PostgreSQLBillingEventSink(connection)

    sink.record(event)
    sink.record(event)

    assert connection.commits == 2


def test_postgres_sink_rejects_conflicting_reuse_of_event_id():
    event = _event()
    connection = FakeConnection(_row(event, status="refunded"))

    with pytest.raises(BillingContractError, match="different payload"):
        PostgreSQLBillingEventSink(connection).record(event)


def test_postgres_sink_get_returns_normalized_event():
    event = _event()
    connection = FakeConnection(_row(event))

    result = PostgreSQLBillingEventSink(connection).get(event.event_id)

    assert result == event
    assert connection.cursor_instance.executed == [
        (
            """SELECT event_id, organization_id, event_type, occurred_at,
                          provider_reference, status
                   FROM billing_events
                   WHERE event_id=%s""",
            (event.event_id,),
        )
    ]


def test_postgres_sink_get_returns_none_for_missing_event():
    connection = FakeConnection(None)

    assert PostgreSQLBillingEventSink(connection).get("missing") is None
