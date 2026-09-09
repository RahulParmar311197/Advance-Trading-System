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
- Backtest execution API: validates the request, loads one immutable data version, executes the registered strategy/backtester, and returns metrics/trades without fabricated data.
- Experiment API: creates and persists manifests/results, lists and retrieves experiments, and re-runs from the stored manifest while refusing a data-version mismatch.

## Verification
- Setuptools package discovery is explicit and editable installation succeeds in CI.
- CI run 28 completed successfully after the FastAPI route assertion fix; it included PostgreSQL service initialization and the existing repository integration tests.
- CI run 40 is currently executing the newly added backtest/experiment API and repository retrieval tests; no pass claim is made until it completes.
- CI also exposed and the implementation restored a missing deterministic provider module.
- No real market-data credentials are committed and no fabricated market data/performance is used.
- No dedicated lint/type-check configuration is currently present in `pyproject.toml`; CI's pytest run is the available automated verification gate for these changes.

## Remaining P0 blockers
1. Verify the current CI run and fix any remaining failures.
2. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
3. Build the dashboard/candlestick/event/backtest result journey.
4. Run the full-stack acceptance test with real or explicitly user-supplied market data.
5. Add the remaining P0 equity-curve/research validation pieces needed by the acceptance journey.

## Next dependency
After CI is green, the next P0 application dependency is the web dashboard: historical candles → deterministic SMC events → backtest execution → metrics/trades → experiment results. Advanced options, microstructure, ML, AI-agent, execution, SaaS and hardening remain downstream dependencies.
