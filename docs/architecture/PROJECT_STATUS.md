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
- Next.js dashboard implementation: candle chart, SMC event overlay, backtest results, realized equity curve, experiment table, API controls, and local Docker service.
- FastAPI CORS boundary for the local dashboard origin.
- Walk-forward research engine with rolling train/test windows, optional strategy fitting, OOS-only signal execution, compounding equity, window-level metrics, and tests.
- Explicit out-of-sample evaluator using a final holdout block, train-only optional fitting, holdout-only execution, and tests.
- Deterministic stress-test runner applying explicitly supplied slippage and risk scenarios to the same candles and strategy, with scenario metrics and unit tests.
- Web lint configuration and patched supported Next.js dependency; workflow invokes ESLint directly.

## Verification
- Previous Python CI passed the PostgreSQL integration suite.
- The first Web lint gate failed because ESLint was unconfigured; this was fixed with explicit ESLint configuration and a direct lint command.
- The Python CI exposed a real walk-forward fixture error; the fixture was corrected to make the intended target fill possible instead of weakening the assertion.
- Latest CI triggered by the stress-test changes is still pending verification.
- The backtest API returns a candle-aligned realized equity curve derived from actual closed-trade P&L.
- No real market-data credentials are committed and no fabricated market data/performance is used.
- No dedicated Python lint/type-check configuration is currently present in `pyproject.toml`.

## Remaining P0/P1 blockers
1. Verify the latest Python and Web CI runs and fix any failures.
2. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
3. Run the full-stack acceptance journey with real or explicitly user-supplied market data.
4. Verify walk-forward, out-of-sample, and stress-test implementations in CI.
5. Implement strategy comparison and research report generation.

## Next dependency
After CI verification, implement strategy comparison across reproducible experiment/backtest results. Research report generation remains downstream. Advanced options, microstructure, ML, AI-agent, execution, SaaS and hardening remain later dependencies.
