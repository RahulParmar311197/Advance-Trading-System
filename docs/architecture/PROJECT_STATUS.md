# Project Status

## Current implementation state

The repository has a runnable Python/FastAPI foundation, deterministic research components, reproducible experiment persistence, and a Next.js web dashboard implementation. The P0 acceptance gate is not complete; milestone completion is based on runtime acceptance tests, not file presence.

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
- Next.js dashboard implementation: candle chart, SMC event overlay, backtest results, experiment table, API controls, and local Docker service.
- FastAPI CORS boundary for the local dashboard origin.

## Verification
- Setuptools package discovery is explicit and editable installation succeeds in CI.
- CI run 44 completed successfully after the experiment JSON serialization boundary fix.
- The latest CI run was triggered after the dashboard work and is still pending verification; no dashboard runtime/build pass is claimed yet.
- Python integration tests cover the API route contract and dashboard CORS configuration.
- No real market-data credentials are committed and no fabricated market data/performance is used.
- No dedicated Python lint/type-check configuration is currently present in `pyproject.toml`.
- Web build verification is the remaining immediate verification task; the existing CI workflow currently executes the Python suite only.

## Remaining P0 blockers
1. Verify the latest CI run and fix any failures, including frontend build verification once wired into CI.
2. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
3. Run the full-stack acceptance journey with real or explicitly user-supplied market data.
4. Add the remaining P0 equity-curve/research validation pieces needed by the acceptance journey.

## Next dependency
After dashboard verification, the next P0 research dependency is the equity curve plus walk-forward/out-of-sample/stress-test research validation. Advanced options, microstructure, ML, AI-agent, execution, SaaS and hardening remain downstream dependencies.
