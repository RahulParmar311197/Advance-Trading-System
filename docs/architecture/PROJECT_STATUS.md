# Project Status

## Current implementation state

The repository has a runnable Python/FastAPI foundation, deterministic research components, reproducible experiment persistence, a Next.js dashboard, paper/live execution boundaries, and a production/SaaS security and asynchronous-job slice. The P0 acceptance gate is not complete; milestone completion is based on runtime acceptance tests, not file presence.

## Completed foundations
- M0 repository structure, Python package configuration, environment template, Docker Compose, CI workflow, and health endpoint.
- Market-data provider contract, OHLCV models/schemas, normalization, validation and ingestion.
- Canonical `packages.market_data` candle persistence and content-addressed immutable raw OHLCV storage.
- Instruments/symbol mapping, trading calendar, deterministic indicators and SMC events.
- Strategy/backtest framework, Liquidity MSS FVG strategy, cost/slippage-aware backtest, metrics, portfolio/risk primitives, and API integration.
- Experiment persistence, reproducibility metadata, strategy comparison, report generation, and research dashboard views.
- Options, microstructure, regime/ML, and M9 research-agent foundations with deterministic validation and unit coverage.
- M10 broker interface, paper broker, order manager, execution simulator, reconciliation, disabled-by-default live adapter, execution monitoring, and kill-switch integration; authoritative CI verification is recorded in the completion plan.
- M12 partial-fill, rejection, typed broker failure, network/database, timestamp, market-closure, and data-quality hardening. Duplicate-tick testing remains blocked until a concrete tick/trade observation model exists.
- M11 authentication/authorization: digest-only persistent API-key metadata, organization-scoped principals, role permissions, fail-closed 401/403 behavior, protected market-data/backtest/experiment routes, and CORS support for authentication headers.
- M11 persistent organizations/users/API-key repositories: parameterized PostgreSQL create/get/revoke boundaries with unit coverage.
- M11 route-level experiment resource scoping: manifest/results/comparison/report repository access requires authenticated organization scope.
- M11 Redis/cache: namespaced JSON Redis adapter with bounded TTL, optional API dependency, SMC-event read-through caching, local Redis service, and unit coverage.
- M11 queue/workers: FIFO Redis queue with recoverable in-flight claims, acknowledgement/retry/backoff semantics, runnable worker process, Docker worker service, and a real PostgreSQL-persisted backtest job handler.
- M11 scheduled jobs: separate interval scheduler service with validated explicit job configuration, Redis enqueue boundary, missed-interval storm protection, Redis outage recovery, Docker service, and unit coverage.
- M11 monitoring: liveness plus PostgreSQL/Redis/queue readiness reporting, configurable queue selection, fail-closed HTTP 503 behavior, documentation and integration/unit coverage.
- M11 alerts: readiness health-transition alerts through the application logging boundary with explicit delivery outcomes and transition de-duplication/recovery signaling; transition and delivery-failure behavior now has direct unit coverage.
- M11 error tracking: normalized exception events with HTTP request context and traceback-aware application logging, fail-closed database-error handling, and generic 500 handling without leaking exception text.
- M11 data-quality monitoring: immutable candle-window assessment built on canonical OHLCV validation and session-aware missing-candle detection, with unit coverage.
- M11 deployment: provider-neutral production Compose topology with explicit secrets/configuration, dependency health gates, restart policies, internal database/Redis networking, production configuration validation, CI Compose validation, and an operational deployment/rollback runbook. The API container healthcheck now targets `/health/ready`, so web startup is gated on PostgreSQL/Redis/queue readiness rather than process liveness alone.
- M11 billing contract boundary: normalized timezone-aware billing events with organization ownership, idempotent event recording semantics, explicit separation between provider authentication and application ingestion, and a PostgreSQL persistence sink. No payment provider is selected or simulated.
- Causal OOS/walk-forward research verification: training-only fitting and causal holdout signal generation are covered by unit tests and full CI.
- Stress testing and combined research integration are covered by deterministic test-only fixtures and CI verification.
- Provider-supplied CSV market-data preparation: strict timezone-aware OHLCV parsing, explicit column mapping, requested symbol/timeframe/window filtering, and fail-closed malformed-row handling; no repair or fabricated observations.
- Market-data API hardening: candle and SMC queries use half-open `[start, end)` windows, reject naive query timestamps, and reject empty windows, with integration/unit coverage.
- Deployment hardening: production `DATABASE_URL` and `REDIS_URL` now accept only schemes supported by their respective clients (`postgres`/`postgresql`, `redis`/`rediss`), with explicit wrong-scheme rejection and TLS Redis coverage.
- Readiness hardening: PostgreSQL readiness connection failures and Redis client-construction failures now fail closed as structured 503 readiness responses rather than escaping through the HTTP layer.
- Instrument expiry calendar: configurable weekly expiry weekday, explicit holiday set, previous/next trading-day adjustment, inclusive range generation, and unit coverage; no exchange-specific expiry weekday is assumed.
- Option expiry calendar: immutable, timezone-aware calendar of explicitly supplied expiry timestamps with sorted/duplicate validation, half-open range queries, and fail-closed lookup/query validation; no exchange-specific schedule is inferred.

## Verification
- Alerts and web lint/build passed on the recorded M11 alert revision; direct transition/delivery unit coverage was added in commit `0822568d9a20a5e4c6c11444df4646e436bdb8bd`.
- Error tracking Python CI passed on run `34577482109` / job `103193146616`.
- Data-quality monitoring CI passed on run `34578034504` / job `103194909226`.
- Deployment implementation passed Python/Compose CI on run `34578717765` / job `103197072683`.
- Billing PostgreSQL persistence and contract tests passed on CI run `34580507357` / run number `484`; Web lint/build passed on run `34580507412` / run number `420`.
- Corrected causal OOS/walk-forward fixtures passed the full Python/Compose CI on run `34582674053` / job `103209631487`; Web lint/build passed on run `34582674057` / job `103209631515`.
- Stress-test verification passed the full Python/Compose CI on run `34582877990` / job `103210285835`.
- Combined research verification passed the full Python/Compose CI on run `34583446968` / job `103212090259`; Web lint/build passed on run `34583446913` / job `103212089982`.
- The CSV provider implementation and tests passed full Python/Compose CI on run `34584113636` / job `103214214002`; Web lint/build passed on run `34584113590` / job `103214213577`.
- The corrected API-window-hardening tests passed full Python/Compose CI on run `34585734250` / job `103219387353`; the preceding Web workflow passed lint/build on run `34585098388` / job `103217358543`.
- The latest readiness and production deployment changes passed both authoritative workflows on commit `e97f09984afefdeacb6a855f02bd69f3d4876980`: Python/Compose CI run `34588714810` / run number `554` and Web lint/build run `34588714882` / run number `490`.
- The instrument expiry implementation and corrected tests were committed on `c54015ceaab0522795756a21da5383eff7ee1d93`; authoritative CI verification for that revision passed in Python/Compose run `34594336561` / job `103246501466` and Web run `34594336568` / job `103246501507`.
- The local container cannot clone the repository because outbound GitHub DNS is unavailable; GitHub Actions is the authoritative full-suite test environment.
- No dedicated Python lint/type-check configuration is present in `pyproject.toml`; Web lint is configured separately.
- No real market-data credentials are committed and no fabricated market data/performance is used.
- No production billing provider or authorized Indian historical-data service has been supplied, so those external integrations remain intentionally unimplemented.

## Remaining blockers
1. Select and authorize a production billing provider or supply the real internal billing contract, then implement an authenticated adapter.
2. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
3. Complete the full-stack acceptance journey with supplied/real market data.
4. Add duplicate-tick tests only after a concrete tick/trade observation model is introduced.

## Next dependency
The internal readiness/deployment hardening and instrument/option expiry primitives are CI-verified. The next substantive dependency remains externally supplied authorization/data: a production billing provider or real internal billing contract, and an authorized real Indian historical-data service. The strict CSV adapter remains the non-fabricating path for provider-supplied files but does not substitute for production provider authorization. Duplicate-tick testing remains blocked until a concrete tick/trade observation model exists.
