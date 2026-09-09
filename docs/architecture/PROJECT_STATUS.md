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
- Setuptools package discovery is now explicit and editable installation succeeds in CI.
- CI reached 17 passing tests before exposing a FastAPI route-introspection assertion that was incompatible with current FastAPI router representation; the test now uses the generated OpenAPI path set.
- CI also exposed and the implementation restored a missing deterministic provider module.
- A PostgreSQL service plus real PostgreSQL repository integration test are part of CI; the test was reached successfully in the run that reported the API assertion failure.
- A newer CI run is triggered by the latest test fix. No full-suite pass claim is made until that run completes.
- No real market-data credentials are committed and no fabricated market data/performance is used.

## Remaining P0 blockers
1. Verify the latest full pytest run and PostgreSQL integration; fix any remaining failures.
2. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
3. Implement and test the backtest execution API endpoint.
4. Implement experiment API endpoints and reproducibility re-run path.
5. Build the dashboard/candlestick/event/backtest result journey.
6. Run the full-stack acceptance test with real or explicitly user-supplied market data.

## Next dependency
Backtest execution API is the next application dependency once CI is green. Then complete experiment API/re-run and the web dashboard. Advanced options, microstructure, ML, AI-agent, execution, SaaS and hardening remain downstream dependencies.
