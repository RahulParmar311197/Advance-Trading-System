# Project Status

## Current implementation state

The repository has a working foundation and deterministic research components, but the P0 acceptance gate is not complete. Per the architecture, milestones are not considered complete merely because files exist; runtime acceptance tests must pass.

## Completed foundations
- M0 core Python/FastAPI bootstrap, environment config, health route, Docker API/database definitions.
- M1 market-data provider contract, OHLCV models/schemas, normalization, validation, ingestion.
- Candle repository contract with deterministic in-memory implementation and PostgreSQL DB-API adapter.
- Instruments/symbol mapping and trading-session primitives.
- M2 EMA/ATR/VWAP and deterministic swing/BOS/MSS/liquidity/FVG calculations.
- M3 strategy framework/registry, Liquidity MSS FVG strategy, cost/slippage-aware backtest, metrics, portfolio/risk primitives.

## Latest work
- Historical OHLCV ingestion now supports idempotent repository persistence through `ingest_historical_ohlcv`.
- Added explicit in-memory provider for tests/local development; it accepts only caller-supplied rows and never fabricates prices.
- Added data-quality tests for repository idempotency, ingestion persistence, and required raw-data fields.

## Remaining P0 blockers
1. Connect a real historical NIFTY OHLCV provider without fabricating data.
2. Add immutable raw-object storage and dataset versioning.
3. Wire PostgreSQL repositories into the application startup/configuration.
4. Complete experiment persistence and reproducibility manifest.
5. Complete API/web journey: historical candles → SMC events → backtest → metrics/trades → saved experiment.
6. Run the full stack acceptance test with real or explicitly user-supplied market data.

## Verification
The repository's previously verified baseline was `python -m pytest` with 8 passing tests. This change adds additional data-quality tests; the GitHub integration used here cannot execute the repository test suite, so no new pass count is claimed without an execution environment.

The synthetic smoke test remains explicitly a software test only and is not a market-performance claim.
