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
- P1 deterministic exposure aggregation, return-series correlation, broker fill simulation, realized backtest portfolio curve, and core portfolio accounting with trade recording/equity/realized P&L, each with tests.
- P2 options foundation: validated immutable option-contract/chain model, dependency-free European Black-Scholes Greeks, deterministic Black-Scholes price/inversion IV, deterministic OI/OI-change analytics, deterministic put/call open-interest ratio analytics, deterministic implied-volatility term-structure ordering, deterministic volatility-surface observation ordering, and deterministic option expiry payoff analysis.
- M7 spread, depth, imbalance, trade-flow, trade intensity, price impact, liquidity/resiliency, and execution implementations with fail-closed validation and unit tests. Execution consumes only explicitly supplied visible order-book liquidity and reports partial fills without inventing liquidity.
- M8 regime features, detector, classifier, transitions, and deterministic candle-window dataset builder implementations with unit tests.
- M8 nearest-centroid model baseline: dependency-free deterministic multiclass classifier with explicit training dataset and unit tests committed; supplementary baseline, not a replacement for the required logistic baseline.
- M8 logistic-regression baseline: dependency-free deterministic one-vs-rest logistic classifier with explicit learning configuration, immutable fitted parameters, fail-closed validation, unit tests, and authoritative Python CI verification on run `34337582225`.
- M8 Random Forest baseline: dependency-free deterministic bootstrap decision-tree ensemble with explicit seed/configuration, feature subsampling, immutable fitted trees, unit tests, and authoritative Python CI verification on run `34338335095`.
- M8 deterministic training layer: explicit model-selection configuration and public training/prediction dispatch for supported baselines.
- M8 Gradient Boosting baseline: deterministic one-vs-rest squared-error boosting over regression stumps, explicit estimator count/learning rate, immutable fitted stages, feature-width validation, implementation and unit tests; full integrated M8 CI verification passed on run `34340996500`.
- M8 strict out-of-sample evaluator: final holdout is excluded from training and accuracy is calculated only from holdout predictions; implementation and corrected deterministic tests; full integrated M8 CI verification passed on run `34340996500`.
- M8 inference boundary: explicit fitted-model prediction contract, immutable inference result, batch shape validation, and fail-closed delegation to fitted model prediction; unit tests; full integrated M8 CI verification passed on run `34340996500`.
- M8 deterministic model versioning implementation: content-addressed version identity includes model class, fitted parameters, exact labeled feature dataset, and explicit training configuration; immutable version record and unit tests; full integrated M8 CI verification passed on run `34340996500`.
- M9 agent interface, planner, tool registry, historical-data tool, feature tool, SMC tool, backtest tool, walk-forward tool, strategy comparison tool, risk analysis tool, report tool, and experiment memory are implemented with deterministic validation and unit coverage.
- M10 broker-neutral execution contract: validated order request, order status/fill state, and abstract submit/cancel/query interface in `packages/execution/broker.py`, with unit coverage; authoritative CI verification pending.
- Web lint configuration and patched supported Next.js dependency; workflow invokes ESLint directly.

## Verification
- Python CI run `34340996500` completed successfully; full M8 model/research suite passed with 193 tests.
- Feature-tool Python CI completed successfully on run `34344767506`.
- CI run `34565820493` on the first M9-memory integration revision exposed six pre-existing/integration regressions: `build_equity_curve()` returns mapping records but `packages/ai_agent/backtest.py` indexed them positionally; the SMC fixture still did not produce an event. The run reported 223 passed and 7 failed.
- Fixed the equity-curve access to use `point["index"]` and replaced the SMC fixture with an oscillating sequence that exercises actual swing/BOS/FVG behavior.
- Corrected M9 head `f990a18bb6e53425ef30c969e5a17b52efb94874` passed the authoritative Python test job `34565942337` and web build/lint job `34565942410`.
- The local container cannot clone the repository because outbound GitHub DNS is unavailable; GitHub Actions is therefore the authoritative full-suite test environment.
- No dedicated Python lint/type-check configuration is present in `pyproject.toml`; Web lint is configured separately.
- No real market-data credentials are committed and no fabricated market data/performance is used.

## Remaining blockers
1. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
2. Run the full-stack acceptance journey with supplied/real market data.
3. Verify the research-validation implementations in CI on their current integrated revision.
4. Complete authoritative Python CI verification for the new M10 broker-interface revision.
5. Implement the paper broker only after the broker contract revision is verified.

## Next dependency
Verify the M10 broker-interface revision in GitHub Actions. If green, implement the paper broker against the stable broker contract; if red, fix the actual failure before advancing.
