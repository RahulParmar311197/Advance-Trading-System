# Project Status

## Current implementation state

The repository has a working foundation and deterministic research components, but the P0 acceptance gate is not complete. Per the architecture, milestones are not considered complete merely because files exist; runtime acceptance tests must pass.

## Completed foundations
- M0 core Python/FastAPI bootstrap, environment config, health route, Docker API/database definitions.
- Market-data provider contract, OHLCV models/schemas, normalization, validation and ingestion.
- Canonical importable `packages.market_data` repository implementations; idempotent in-memory and PostgreSQL candle persistence.
- Content-addressed immutable raw OHLCV storage.
- Explicit caller-supplied static provider for deterministic local/integration tests.
- Authorized HTTP provider adapter with bearer-token support and strict JSON OHLCV parsing; it requires an externally configured authorized service and does not fabricate data.
- Instruments/symbol mapping, expiry primitive and trading-session primitives.
- EMA/ATR/VWAP and deterministic swing/BOS/MSS/liquidity/FVG calculations.
- Strategy framework/registry, Liquidity MSS FVG strategy, cost/slippage-aware backtest, metrics, portfolio/risk primitives.
- Continuous-integration workflow that installs the package and runs pytest.

## Remaining P0 blockers
1. Configure an actual authorized Indian historical-data service and validate its response contract with real provider data; no credentials are committed.
2. Add PostgreSQL integration test against a real database service.
3. Complete experiment persistence and reproducibility manifest.
4. Complete API/web journey: historical candles → SMC events → backtest → metrics/trades → saved experiment.
5. Run the full-stack acceptance test with real or explicitly user-supplied market data.

## Verification
A representative isolated test harness for the new HTTP provider behavior was executed locally: 2 tests passed. The complete GitHub repository cannot be executed from the current editing environment because repository commands/network checkout are unavailable, so no full-suite pass count is claimed.

The CI workflow now provides the repository-side execution path for the full pytest suite.

The synthetic smoke test remains explicitly a software test only and is not a market-performance claim.

## Next dependency
PostgreSQL application integration and reproducible experiment persistence are the next implementation targets; the external historical provider remains configuration-dependent until an authorized service/credentials are supplied.
