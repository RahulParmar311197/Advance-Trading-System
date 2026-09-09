# Project Status

## Current implementation state

The repository has a runnable Python/FastAPI foundation, deterministic research components, reproducible experiment persistence, and a Next.js web dashboard implementation. The P0 acceptance gate is not complete; milestone completion is based on runtime acceptance tests, not file presence.

## Completed foundations
- M0 repository structure, Python package configuration, environment template, Docker Compose, CI workflow, and health endpoint.
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
- M7 spread, depth, imbalance, trade-flow, trade intensity, price impact, liquidity/resiliency, and execution implementations with fail-closed validation and unit tests. Execution consumes only explicitly supplied visible order-book liquidity and reports partial fills without inventing liquidity.
- M8 regime features, detector, classifier, transitions, and deterministic candle-window dataset builder implementations with unit tests.
- M8 nearest-centroid model baseline: dependency-free deterministic multiclass classifier with explicit training dataset and unit tests committed; supplementary baseline, not a replacement for the required logistic baseline.
- M8 logistic-regression baseline: dependency-free deterministic one-vs-rest logistic classifier with explicit learning configuration, immutable fitted parameters, fail-closed validation, unit tests, and authoritative Python CI verification on run `34337582225`.
- M8 Random Forest baseline: dependency-free deterministic bootstrap decision-tree ensemble with explicit seed/configuration, feature subsampling, immutable fitted trees, and unit tests.
- M8 deterministic training layer: explicit model-selection configuration and public training/prediction dispatch for the supported baselines.
- Web lint configuration and patched supported Next.js dependency; workflow invokes ESLint directly.

## Verification
- Python CI run `34337582225` completed successfully on the corrected logistic-baseline revision.
- Web CI run `34337651570` completed successfully; dashboard lint and build passed.
- Python CI run `34338164088` completed successfully; microstructure execution tests passed.
- Python CI run `34338335095` completed successfully; Random Forest tests passed.
- The newest training-layer revision is awaiting authoritative Python CI verification.
- Local isolated execution is not the authoritative full-suite verification; GitHub Actions is authoritative because this environment is not a Git checkout and outbound GitHub DNS is unavailable from the container.
- No dedicated Python lint/type-check configuration is currently present in `pyproject.toml`.
- No real market-data credentials are committed and no fabricated market data/performance is used.

## Remaining blockers
1. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
2. Run the full-stack acceptance journey with supplied/real market data.
3. Verify the research-validation implementations in CI on their current integrated revision.
4. Complete authoritative CI verification for the newest ML training-layer revision.
5. Implement and verify the required Gradient Boosting baseline.
6. Complete M8 out-of-sample model validation and model versioning.

## Next dependency
Complete authoritative Python CI verification of the current ML training-layer revision. If green, implement the required Gradient Boosting baseline using explicit dataset inputs and deterministic configuration; if CI finds a failure, fix the actual failure before advancing.
