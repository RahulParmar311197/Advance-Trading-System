# Billing integration contract

The repository defines an internal boundary for billing events without selecting a payment provider. This is intentional: the architecture requires an explicitly selected/authorized provider or real internal billing contract before provider behavior can be implemented.

## Boundary

`BillingService.ingest(BillingEvent)` accepts only a normalized, already-authenticated event. Provider adapters are responsible for authenticating and verifying signatures before invoking the service.

A `BillingEvent` contains:

- immutable event ID for idempotency;
- organization ID for tenant ownership;
- event type;
- timezone-aware occurrence time;
- provider reference;
- normalized status.

An event ID may be recorded repeatedly only when the payload is identical. Reuse with a different payload is rejected.

## Explicit non-goals

This contract does not create subscriptions, charge customers, verify provider signatures, issue refunds, or manufacture provider events. No payment credentials or provider-specific assumptions are stored in the repository.

## Next integration step

Select and authorize the production billing provider (or provide the real internal billing contract), then add its authenticated adapter and integration tests against the provider's documented webhook/event contract. Do not mark billing complete from this boundary alone.
