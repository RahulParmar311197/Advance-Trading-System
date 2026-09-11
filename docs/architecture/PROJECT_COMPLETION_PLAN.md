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
- [ ] Causal out-of-sample verification — corrected test fixtures now assert training-only fitting and test-only trade evaluation; current CI verification pending.
- [ ] Causal walk-forward verification — corrected test fixtures now assert each rolling train block is isolated from the corresponding OOS block; current CI verification pending.
- [ ] Stress-test verification on the integrated revision.

## Remaining blockers
1. Verify the corrected causal OOS/walk-forward revision in GitHub Actions.
2. Verify the existing stress-test implementation on the integrated revision.
3. Select and authorize a production billing provider or supply the real internal billing contract, then implement its authenticated adapter.
4. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
5. Complete the full-stack acceptance journey with supplied/real market data.
6. Verify walk-forward, out-of-sample, and stress-test implementations together on the final integrated revision.
7. Add duplicate-tick tests only after a concrete tick/trade observation model is introduced.

## Critical acceptance test
A fresh developer must be able to start the stack, load sample NIFTY data, open the dashboard, see 5m candles and SMC events, run the Liquidity MSS FVG backtest, see realistic metrics, and reproduce the experiment from its recorded metadata.

## Delivery rule
Do not mark a milestone complete because files exist. Mark it complete only when the code runs and its acceptance tests pass.
