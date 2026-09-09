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
- P1 deterministic exposure aggregation, return-series correlation, broker fill simulation, realized backtest portfolio accounting, and core portfolio accounting with trade recording/equity/realized P&L, each with tests.
- Web lint configuration and patched supported Next.js dependency; workflow invokes ESLint directly.

## Verification
- Python CI run `34317564177` completed successfully after the P1 portfolio/broker additions and tests.
- Web CI run `34317602647` completed successfully: dependency installation, ESLint with zero warnings, and Next.js production build all passed.
- The Web workflow previously caught a real React Hook dependency warning; it was fixed with `useCallback` and a dependency-correct effect rather than suppressing lint.
- The Python CI previously exposed a real walk-forward fixture error; the fixture was corrected to make the intended target fill possible instead of weakening the assertion.
- Backtest API returns a candle-aligned realized equity curve derived from actual closed-trade P&L.
- No real market-data credentials are committed and no fabricated market data/performance is used.
- No dedicated Python lint/type-check configuration is currently present in `pyproject.toml`.

## Remaining P0/P1 blockers
1. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
2. Run the full-stack acceptance journey with real or explicitly user-supplied market data.
3. Verify walk-forward, out-of-sample, stress-test, strategy-comparison, and report implementations in CI on their current integrated revision.
4. Continue P2 options/microstructure/regime dependencies after P1 verification.

## Next dependency
Run/verify the integrated research-validation path in CI for walk-forward, out-of-sample, stress-test, comparison, and reporting. In parallel, real provider configuration and full-stack acceptance remain explicit blockers. After those gates, begin P2 options analytics from the required architecture inventory.
