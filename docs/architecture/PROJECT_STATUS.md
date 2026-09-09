# Project Status

## Current implementation state

The repository has a runnable Python/FastAPI foundation and deterministic research components. The P0 acceptance gate is not complete; milestone completion is based on runtime acceptance tests, not file presence.

## Completed foundations
- M0 repository structure, Python package configuration, environment template, root Docker Compose, CI workflow, and health endpoint.
- Market-data provider contract, OHLCV models/schemas, normalization, validation and ingestion.
- Canonical importable `packages.market_data` candle persistence implementations.
- Content-addressed immutable raw OHLCV storage.
- Explicit caller-supplied static provider for deterministic tests.
- Authorized HTTP provider adapter with strict JSON parsing and no fabricated data.
- Instruments/symbol mapping, expiry primitive and trading-session primitives.
- EMA/ATR/VWAP and deterministic swing/BOS/MSS/liquidity/FVG calculations.
- Common structured SMC event contract with serialization and tests.
- Strategy framework/registry, Liquidity MSS FVG strategy, cost/slippage-aware backtest, metrics, portfolio/risk primitives.
- Historical candle API and deterministic SMC-events API, both backed by PostgreSQL candle data.
- Experiment manifest/repository persistence implementation.

## Verification
- The previous CI package-install failure was fixed with explicit setuptools package discovery.
- CI then exposed and the implementation fixed a stale FastAPI route assertion.
- CI then exposed a missing deterministic provider module; it was restored.
- A PostgreSQL service plus real PostgreSQL repository integration test are now part of CI.
- The current branch has newer commits than the last completed CI run, so the latest run must finish before claiming a full-suite pass.
- No real market-data credentials are committed and no fabricated market data/performance is used.

## Remaining P0 blockers
1. Verify the PostgreSQL integration test and full pytest suite in the latest CI run; fix failures before marking the integration complete.
2. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
3. Implement and test the backtest execution API endpoint.
4. Implement experiment API endpoints and reproducibility re-run path.
5. Build the dashboard/candlestick/event/backtest result journey.
6. Run the full-stack acceptance test with real or explicitly user-supplied market data.

## Next dependency
Backtest execution API is now the next application dependency after CI verification. Then complete experiment API/re-run and the web dashboard. Advanced options, microstructure, ML, AI-agent, execution, SaaS and hardening remain downstream dependencies.
