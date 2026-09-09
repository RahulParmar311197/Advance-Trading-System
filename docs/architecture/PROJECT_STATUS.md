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
- P2 options foundation: validated immutable option-contract/chain model, dependency-free European Black-Scholes Greeks, deterministic Black-Scholes price/inversion IV, deterministic OI/OI-change analytics, deterministic put/call open-interest ratio analytics, deterministic implied-volatility term-structure ordering, deterministic volatility-surface observation ordering, and deterministic option expiry payoff analysis.
- M7 spread, depth, imbalance, trade-flow, trade intensity, price impact, and liquidity/resiliency implementations with fail-closed validation, unit tests, and authoritative Python CI verification.
- M8 regime features: deterministic period return, mean absolute return, OLS close-price slope, price-path efficiency, and average volume with fail-closed candle-window validation and unit tests.
- M8 regime detector: deterministic transparent threshold classifier over supplied regime features with explicit caller-supplied thresholds, validation, and unit tests.
- M8 regime classifier: deterministic structured classification combining the verified primary detector label with explicit trend-direction and volatility-state labels, with immutable output and unit tests; Python CI run `34335923065` passed the full configured suite.
- M8 regime transitions: deterministic primary-regime change detection over caller-supplied ordered classifications, with immutable transition records and unit tests committed; authoritative CI verification is pending on the current revision.
- Web lint configuration and patched supported Next.js dependency; workflow invokes ESLint directly.

## Verification
- Python CI run `34333070096` completed successfully on the corrected trade-intensity/price-impact head; all configured repository tests passed.
- Python CI run `34333173992` completed successfully after liquidity/resiliency implementation and tests; all configured repository tests passed.
- Python CI run `34333390091` exposed two genuine regime-feature issues; those implementation/test issues were corrected.
- Python CI run `34333684477` exposed the remaining regime-feature fixture expectation error; the fixture was corrected to use the first and final candle closes.
- Python CI run `34334649943` completed successfully on the integrated regime-feature/detector head; the full repository suite passed.
- Python CI run `34335923065` completed successfully after the regime-classifier implementation and unit tests; the full configured repository test suite passed.
- Web CI run `34336119528` is validating the current revision; dashboard lint has passed and the build was still running at the latest check.
- Local isolated execution is not the authoritative full-suite verification; GitHub Actions is authoritative because this environment is not a Git checkout.
- No dedicated Python lint/type-check configuration is currently present in `pyproject.toml`.
- No real market-data credentials are committed and no fabricated market data/performance is used.

## Remaining blockers
1. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
2. Run the full-stack acceptance journey with real or explicitly user-supplied market data.
3. Verify the research-validation implementations in CI on their current integrated revision.
4. Continue M8 after authoritative verification of regime transitions, then implement the M8 ML dataset/model sequence.

## Next dependency
Complete authoritative CI verification for M8 regime transitions. Then implement the M8 dataset builder with explicit feature/label inputs and no fabricated labels or market data.
