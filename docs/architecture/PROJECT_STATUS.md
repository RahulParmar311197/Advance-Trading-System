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
- Deterministic experiment strategy-comparison ranking by return then drawdown, with unit tests and JSON-safe API serialization.
- Markdown research report generator based only on supplied comparison results, with explicit methodology and limitations, plus unit tests.
- Experiment-facing comparison and report API endpoints plus dashboard views consuming persisted results only.
- P1 deterministic exposure aggregation, return-series correlation, broker fill simulation, and realized backtest portfolio accounting, each with unit tests.
- Web lint configuration and patched supported Next.js dependency; workflow invokes ESLint directly.

## Verification
- Python CI run `34316509982` completed successfully before the latest P1 additions; the newer Python run for the P1 test commit completed its test step successfully and was in post-job cleanup when last checked.
- The Web workflow caught a real React Hook dependency warning after dashboard integration; the dashboard was fixed with `useCallback` and a dependency-correct effect, and a new Web CI run was queued.
- The first Web lint gate failed because ESLint was unconfigured; this was fixed with explicit ESLint configuration and a direct lint command.
- The Python CI exposed a real walk-forward fixture error; the fixture was corrected to make the intended target fill possible instead of weakening the assertion.
- Backtest API returns a candle-aligned realized equity curve derived from actual closed-trade P&L.
- No real market-data credentials are committed and no fabricated market data/performance is used.
- No dedicated Python lint/type-check configuration is currently present in `pyproject.toml`.

## Remaining P0/P1 blockers
1. Verify the latest Web CI after the hook-lint fix.
2. Replace the existing thin `packages/portfolio/portfolio.py` model with the integrated deterministic accounting implementation; GitHub contents writes currently reject its returned blob SHA, so it remains explicitly incomplete rather than being falsely marked done.
3. Verify the latest P1 tests in a completed CI run and fix any failures.
4. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
5. Run the full-stack acceptance journey with real or explicitly user-supplied market data.
6. Verify walk-forward, out-of-sample, stress-test, strategy-comparison, and report implementations in CI.

## Next dependency
Finish and verify the core portfolio accounting file, then proceed through remaining P1 research/accounting dependencies. Only after P1 verification should work move to P2 options, microstructure, and regime components. Real provider configuration and full-stack acceptance remain explicit blockers.
