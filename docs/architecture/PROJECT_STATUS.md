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
- M11 alerts: readiness health-transition alerts through the application logging boundary with explicit delivery outcomes and transition de-duplication/recovery signaling.
- M11 error tracking: normalized exception events with HTTP request context and traceback-aware application logging, fail-closed database-error handling, and generic 500 handling without leaking exception text.
- M11 data-quality monitoring: immutable candle-window assessment built on canonical OHLCV validation and session-aware missing-candle detection, with unit coverage.
- M11 deployment: provider-neutral production Compose topology with explicit secrets/configuration, dependency health gates, restart policies, internal database/Redis networking, production configuration validation, CI Compose validation, and an operational deployment/rollback runbook.
- M11 billing contract boundary: normalized timezone-aware billing events with organization ownership, idempotent event recording semantics, explicit separation between provider authentication and application ingestion, and a PostgreSQL persistence sink. No payment provider is selected or simulated.
- Causal OOS/walk-forward research verification fixtures: strategy fitting is asserted to receive only each applicable training block, while trade generation/evaluation is asserted against only the OOS test block.

## Verification
- Alerts and web lint/build passed on the recorded M11 alert revision.
- Error tracking Python CI passed on run `34577482109` / job `103193146616`.
- Data-quality monitoring CI passed on run `34578034504` / job `103194909226`.
- Deployment implementation passed Python/Compose CI on run `34578717765` / job `103197072683`.
- Billing PostgreSQL persistence and contract tests passed on CI run `34580507357` / run number `484`; Web lint/build passed on run `34580507412` / run number `420`.
- The first causal-research test revision failed because its synthetic test strategy emitted a second entry signal after an exit; the fixture was corrected rather than weakening the research implementation.
- The corrected causal-research revision is under GitHub Actions verification. The previous failing run had 355 passing tests and 2 fixture failures; the corrected revision must pass before this gate is marked complete.
- The local container cannot clone the repository because outbound GitHub DNS is unavailable; GitHub Actions is the authoritative full-suite test environment.
- No dedicated Python lint/type-check configuration is present in `pyproject.toml`; Web lint is configured separately.
- No real market-data credentials are committed and no fabricated market data/performance is used.

## Remaining blockers
1. Verify the corrected causal walk-forward/out-of-sample revision in GitHub Actions.
2. Verify the existing stress-test implementation on the current integrated revision.
3. Select and authorize a production billing provider or supply the real internal billing contract, then implement its authenticated adapter.
4. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
5. Complete the full-stack acceptance journey with supplied/real market data.
6. Verify walk-forward, out-of-sample, and stress-test implementations together on the final integrated revision.
7. Add duplicate-tick tests only after a concrete tick/trade observation model is introduced.

## Next dependency
The billing persistence/contract boundary is complete but cannot progress to a provider adapter without an explicitly selected/authorized provider or real internal billing contract. The next unblocked engineering dependency is verification of causal OOS/walk-forward behavior, followed by stress-test verification, without fabricating market data or results.
