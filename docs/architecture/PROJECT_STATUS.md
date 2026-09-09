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
- M7 spread, depth, imbalance, and trade-flow implementations: deterministic microstructure analytics with fail-closed validation and unit tests; authoritative Python CI verification passed on full-suite run `34331678571`.
- M7 trade intensity: deterministic supplied-trade count per explicitly supplied observation window; authoritative Python CI verification passed on run `34333070096`.
- M7 price impact: deterministic signed traded notional, quantity-weighted execution VWAP, and implementation-shortfall analytics from supplied trade prints; authoritative Python CI verification passed on run `34333070096` after correcting the Decimal precision assertion without changing the calculation implementation.
- M7 liquidity/resiliency: deterministic `LiquiditySnapshot` over supplied quote/depth, visible-liquidity aggregation, depth-recovery ratio, and spread-recovery ratio; unit tests and authoritative Python CI verification passed on run `34333173992`.
- M8 regime features implementation: deterministic period return, mean absolute return, OLS close-price slope, price-path efficiency, and average volume with fail-closed candle-window validation and unit tests. Corrected implementation/test revision is awaiting authoritative CI verification.
- M8 regime detector implementation: deterministic transparent threshold classifier over supplied regime features, with explicit caller-supplied thresholds, validation, and unit tests. Authoritative CI verification is pending on the current integrated head.
- Web lint configuration and patched supported Next.js dependency; workflow invokes ESLint directly.

## Verification
- Python CI run `34317901724` completed successfully after the options chain/Greeks foundation and tests.
- Web CI run `34317602647` completed successfully: dependency installation, ESLint with zero warnings, and Next.js production build all passed.
- Python CI run `34319546635` completed successfully after the OI/OI-change implementation and tests.
- Web CI run `34320730098` completed successfully on the PCR implementation/test revision: dependency installation, ESLint, and Next.js production build all passed.
- Python CI run `34320854541` completed successfully on the PCR implementation/test revision; the full repository test suite passed.
- Python CI run `34327233459` completed successfully on the volatility-surface implementation/test revision; the full repository test suite passed.
- Web CI run `34327336870` completed successfully on the payoff implementation/test revision: dependency installation, ESLint, and Next.js production build all passed.
- Web CI run `34330218338` completed successfully on the spread implementation/test revision: dependency installation, ESLint, and Next.js production build all passed.
- Web CI run `34330792178` completed successfully on the depth implementation head; this does not verify Python tests.
- Web CI run `34331457669` completed successfully on the status-update head; this does not verify Python tests.
- Python CI run `34331678571` completed successfully on the trade-flow test head; the workflow's test job passed all configured repository tests.
- Python CI run `34333070096` completed successfully on the corrected trade-intensity/price-impact head; the workflow test job passed all configured repository tests.
- Python CI run `34333173992` completed successfully after liquidity/resiliency implementation and tests; the workflow test job passed all configured repository tests.
- Python CI run `34333390091` caught two genuine regime-feature issues; 121 other repository tests passed. The subsequent implementation/test correction fixed the period-return assertion and bounded path-efficiency calculation.
- Python CI run `34333684477` caught one remaining genuine regime-feature fixture assertion: the test expected 4/101 while the specified period return contract correctly computes final-vs-initial close, 4/100. The test was corrected.
- Isolated detector checks passed 5/5 and syntax compilation passed in the analysis environment; these are supplementary and not authoritative repository verification.
- A fresh authoritative Python CI run is pending for the corrected regime-feature plus detector head.
- Local isolated execution is not the authoritative full-suite verification; GitHub Actions is authoritative because this environment is not a Git checkout.
- No dedicated Python lint/type-check configuration is currently present in `pyproject.toml`.
- No real market-data credentials are committed and no fabricated market data/performance is used.

## Remaining blockers
1. Authoritatively CI-verify the corrected M8 regime-feature and detector head, then mark only passing components complete.
2. Configure an authorized real Indian historical-data service and validate its response contract with real provider data.
3. Run the full-stack acceptance journey with real or explicitly user-supplied market data.
4. Verify the research-validation implementations in CI on their current integrated revision.
5. Continue M8 with regime classifier and transitions after the detector is verified.

## Next dependency
Authoritatively CI-verify the current M8 regime-feature/detector head. If green, mark verified components complete and implement the next M8 regime dependency without fabricating market data or labels.
