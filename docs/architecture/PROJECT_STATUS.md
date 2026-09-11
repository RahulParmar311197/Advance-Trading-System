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
- M11 route-level experiment resource scoping: manifest/results/comparison/report repository access requires the authenticated organization and fails closed for missing scope; unit/API fixtures cover the tenant boundary.
- M11 Redis/cache: namespaced JSON Redis adapter with bounded TTL, optional API dependency, SMC-event read-through caching, local Redis service, and unit coverage. Cache failure is non-authoritative and falls back to PostgreSQL-derived computation.
- M11 queue/workers: FIFO Redis queue with recoverable in-flight claims, acknowledgement/retry/backoff semantics, runnable worker process, Docker worker service, and a real PostgreSQL-persisted backtest job handler.

## Verification
- Full Python CI passed on M11 security/resource-scoping/cache revision `4dbb426c450fe606886d04848e4bd0c680d827ee` (run `34572595333`, job `103177768789`): 312 tests passed.
- Full Python CI passed on queue/worker revision `4834fbf28ad9296d2346b058e9d2f12bb05b4cf2` (run `34573241100`, job `103179806342`); the subsequent at-least-once retry correction was also exercised by the succeeding CI trigger.
- The local container cannot clone the repository because outbound GitHub DNS is unavailable; GitHub Actions is the authoritative full-suite test environment.
- No dedicated Python lint/type-check configuration is present in `pyproject.toml`; Web lint is configured separately.
- No real market-data credentials are committed and no fabricated market data/performance is used.

## Remaining blockers
1. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
2. Complete the full-stack acceptance journey with supplied/real market data.
3. Verify walk-forward, out-of-sample, and stress-test implementations on the current integrated revision where the checklist still records CI verification as pending.
4. Continue M11 scheduled jobs, monitoring, alerts, error tracking, data-quality monitoring, deployment, and billing hooks.
5. Add duplicate-tick tests only after a concrete tick/trade observation model is introduced.

## Next dependency
Scheduled jobs are the next M11 dependency. They should enqueue real recurring work through the queue rather than perform long-running research or ingestion synchronously in the API. Preserve the real-provider and full-stack acceptance blockers as explicit gates.
