from datetime import datetime, timezone

import pytest

from packages.saas.billing import (
    BillingContractError,
    BillingEvent,
    BillingService,
    InMemoryBillingEventSink,
)


def event(event_id: str = "evt_1") -> BillingEvent:
    return BillingEvent(
        event_id=event_id,
        organization_id="org_1",
        event_type="subscription.updated",
        occurred_at=datetime(2026, 9, 11, 8, 0, tzinfo=timezone.utc),
        provider_reference="provider_ref_1",
        status="active",
    )


def test_billing_event_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(BillingContractError, match="timezone-aware"):
        BillingEvent(
            event_id="evt_1",
            organization_id="org_1",
            event_type="subscription.updated",
            occurred_at=datetime(2026, 9, 11, 8, 0),
            provider_reference="provider_ref_1",
            status="active",
        )


def test_billing_service_is_idempotent_for_same_event() -> None:
    sink = InMemoryBillingEventSink()
    service = BillingService(sink)

    first = service.ingest(event())
    second = service.ingest(event())

    assert first == second
    assert sink.get("evt_1") == first


def test_billing_service_rejects_reused_event_id_with_different_payload() -> None:
    sink = InMemoryBillingEventSink()
    service = BillingService(sink)
    service.ingest(event())

    conflicting = BillingEvent(
        event_id="evt_1",
        organization_id="org_2",
        event_type="subscription.updated",
        occurred_at=event().occurred_at,
        provider_reference="provider_ref_2",
        status="active",
    )
    with pytest.raises(BillingContractError, match="different payload"):
        service.ingest(conflicting)


def test_billing_event_requires_identity_fields() -> None:
    with pytest.raises(BillingContractError, match="organization_id"):
        BillingEvent(
            event_id="evt_1",
            organization_id=" ",
            event_type="subscription.updated",
            occurred_at=event().occurred_at,
            provider_reference="provider_ref_1",
            status="active",
        )
