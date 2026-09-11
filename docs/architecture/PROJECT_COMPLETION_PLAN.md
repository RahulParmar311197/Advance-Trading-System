# Project Completion Plan

## Objective
Turn the architecture in the project source into a continuously runnable Indian quantitative trading research platform, then extend it to paper/live execution and SaaS.

## Current continuation state
M10 execution monitoring and kill-switch integration are CI-verified. M12 hardening is implemented; duplicate-tick testing remains intentionally blocked because the repository has no concrete tick/trade observation model. M11 production/SaaS now has organization-scoped API-key authentication, role authorization, persistent organization/user/API-key repositories, organization-scoped experiment resources, Redis caching, a recoverable Redis-backed job queue/worker, an interval scheduler that enqueues explicit recurring work, CI-verified operational monitoring/readiness checks, operational alert transitions, credential-free error tracking, candle-window data-quality assessment with unit coverage, a provider-neutral production Compose deployment with fail-closed configuration validation and runbook, and a persistent provider-neutral billing-event boundary. Deployment and billing persistence are CI-verified; a production provider adapter remains blocked pending authorization.

### M11 Production/SaaS
- [x] Authentication/credential verification boundary
- [x] Authorization boundary
- [x] Persistent organizations/users/API-key repositories
- [x] Route-level resource scoping
- [x] Redis/cache
- [x] Queue/workers
- [x] Scheduled jobs
- [x] Monitoring
- [x] Alerts
- [x] Error tracking
- [x] Data-quality monitoring — immutable candle-window assessment built on canonical OHLCV validation and session-aware missing-candle detection, with unit coverage
- [x] Deployment — provider-neutral production Compose topology, fail-closed production configuration validation, health-gated startup, CI Compose validation, and deployment/rollback runbook; no cloud provider is claimed
- [ ] Billing hooks — normalized billing-event contract, PostgreSQL persistence, and idempotency tests are complete; authenticated provider adapter is blocked until an explicitly selected/authorized provider or real internal billing contract is supplied

### M12 Hardening
- [x] Bad-data tests
- [x] Missing-candle tests
- [ ] Duplicate-tick tests — blocked until a concrete tick/trade observation model is introduced; do not fabricate one
- [x] Timestamp tests
- [x] Market-closure tests
- [x] Network failure tests
- [x] Database failure tests
- [x] Broker failure tests
- [x] Partial-fill tests
- [x] Rejected-order tests
- [x] API timeout tests
- [x] Recovery/runbook tests

## Research verification
- [x] Causal out-of-sample verification — CI run `34582674053` passed with the corrected fixture; the evaluator fits only the training block and generates holdout signals causally, exposing at most the current test candle.
- [x] Causal walk-forward verification — the same CI run passed; each rolling window fits only its training block and evaluates signals only against its OOS test block without future test-candle exposure.
- [x] Stress-test verification on the integrated revision — CI run `34582877990` passed; tests verify scenario-specific slippage degradation, risk-driven sizing/equity behavior, and invalid stress-parameter rejection.
- [x] Combined research verification — the same synthetic test-only dataset exercises out-of-sample, walk-forward, and stress-test evaluators together; Python/Compose CI passed on run `34583446968` / job `103212090259`.

## Real-data integration preparation
- [x] Strict provider-supplied CSV OHLCV adapter — timezone-aware parsing, explicit column mapping, symbol/timeframe/window filtering, and fail-closed handling of malformed rows; no gap filling or fabricated observations.
- [x] CSV adapter unit coverage for filtering, column mapping, malformed schema/timestamps, and preservation of missing observations.
- [ ] Authorized real Indian historical-data provider — blocked until provider credentials/authorization and its documented response contract are supplied.

## Remaining blockers
1. Select and authorize a production billing provider or supply the real internal billing contract, then implement its authenticated adapter.
2. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
3. Complete the full-stack acceptance journey with supplied/real market data.
4. Add duplicate-tick tests only after a concrete tick/trade observation model is introduced.

## Critical acceptance test
A fresh developer must be able to start the stack, load sample NIFTY data, open the dashboard, see 5m candles and SMC events, run the Liquidity MSS FVG backtest, see realistic metrics, and reproduce the experiment from its recorded metadata.

## Delivery rule
Do not mark a milestone complete because files exist. Mark it complete only when the code runs and its acceptance tests pass.
