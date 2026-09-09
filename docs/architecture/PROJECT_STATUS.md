# Project Status

## Implemented in this commit
- M0 core Python/FastAPI bootstrap, environment config, health route, Docker API/database definitions.
- M1 market-data provider contract, OHLCV models/schemas, normalization, validation, ingestion.
- Instruments/symbol mapping and trading-session primitives.
- M2 EMA/ATR/VWAP and deterministic swing/BOS/MSS/liquidity/FVG calculations.
- M3 strategy framework/registry, Liquidity MSS FVG strategy, cost/slippage-aware backtest, metrics, portfolio/risk primitives.

## Remaining
- Real historical NIFTY provider and immutable raw-object storage.
- PostgreSQL experiment repository and full persistence wiring.
- Full SMC/indicator suite, worker, Next.js dashboard and result visualization.
- P1 research platform, then options, microstructure, regime, ML, AI agent, execution, production and hardening.

## Verification
`python -m pytest` passes 8 tests in the implementation workspace. `python scripts/run_backtest.py` is a deterministic synthetic smoke test only and makes no market-performance claim.
