# Vibe Coding File Map

This is the implementation inventory. Create files in dependency order; do not create placeholder files merely to satisfy the tree.

## Core
- `README.md`
- `.env.example`
- `docker-compose.yml`
- `pyproject.toml`
- `Makefile`
- `.github/workflows/ci.yml`

## API
- `apps/api/app/main.py`
- `apps/api/app/config.py`
- `apps/api/app/dependencies.py`
- `apps/api/app/routes/health.py`
- `apps/api/app/routes/market_data.py`
- `apps/api/app/routes/features.py`
- `apps/api/app/routes/signals.py`
- `apps/api/app/routes/backtest.py`
- `apps/api/app/routes/experiments.py`
- `apps/api/app/schemas.py`

## Worker
- `apps/worker/main.py`
- `apps/worker/jobs/ingest.py`
- `apps/worker/jobs/features.py`
- `apps/worker/jobs/backtest.py`
- `apps/worker/jobs/research.py`

## Web
- `apps/web/README.md`
- `apps/web/app/page.tsx`
- `apps/web/app/chart/page.tsx`
- `apps/web/app/backtest/page.tsx`
- `apps/web/app/research/page.tsx`
- `apps/web/components/CandlestickChart.tsx`
- `apps/web/components/SignalOverlay.tsx`
- `apps/web/components/BacktestResults.tsx`
- `apps/web/components/ExperimentTable.tsx`

## Market data
- `packages/market-data/provider.py`
- `packages/market-data/models.py`
- `packages/market-data/schemas.py`
- `packages/market-data/ingestion.py`
- `packages/market-data/normalization.py`
- `packages/market-data/validation.py`

## Instruments
- `packages/instruments/instrument.py`
- `packages/instruments/symbol_map.py`
- `packages/instruments/expiry.py`
- `packages/instruments/trading_calendar.py`

## Indicators
- `packages/indicators/sma.py`
- `packages/indicators/ema.py`
- `packages/indicators/rsi.py`
- `packages/indicators/atr.py`
- `packages/indicators/vwap.py`
- `packages/indicators/volatility.py`
- `packages/indicators/volume.py`

## SMC
- `packages/smc/swings.py`
- `packages/smc/structure.py`
- `packages/smc/liquidity.py`
- `packages/smc/displacement.py`
- `packages/smc/fvg.py`
- `packages/smc/order_blocks.py`
- `packages/smc/premium_discount.py`
- `packages/smc/mss.py`
- `packages/smc/bos.py`

## Strategies
- `packages/strategies/base.py`
- `packages/strategies/registry.py`
- `packages/strategies/rules.py`
- `packages/strategies/signals.py`
- `packages/strategies/position_sizing.py`
- `packages/strategies/liquidity_mss_fvg.py`

## Backtest
- `packages/backtest/engine.py`
- `packages/backtest/events.py`
- `packages/backtest/broker_simulator.py`
- `packages/backtest/fills.py`
- `packages/backtest/commission.py`
- `packages/backtest/slippage.py`
- `packages/backtest/position.py`
- `packages/backtest/portfolio.py`
- `packages/backtest/metrics.py`

## Portfolio/risk
- `packages/portfolio/portfolio.py`
- `packages/portfolio/exposure.py`
- `packages/risk/limits.py`
- `packages/risk/position_sizing.py`
- `packages/risk/exposure.py`
- `packages/risk/drawdown.py`
- `packages/risk/correlation.py`
- `packages/risk/portfolio_risk.py`
- `packages/risk/kill_switch.py`

## Options
- `packages/options/chain.py`
- `packages/options/greeks.py`
- `packages/options/iv.py`
- `packages/options/volatility_surface.py`
- `packages/options/open_interest.py`
- `packages/options/expiry.py`
- `packages/options/payoff.py`

## Microstructure
- `packages/microstructure/spread.py`
- `packages/microstructure/imbalance.py`
- `packages/microstructure/depth.py`
- `packages/microstructure/trade_flow.py`
- `packages/microstructure/price_impact.py`
- `packages/microstructure/liquidity.py`
- `packages/microstructure/execution.py`

## Regime
- `packages/regime/detector.py`
- `packages/regime/features.py`
- `packages/regime/classifier.py`
- `packages/regime/transitions.py`

## ML
- `packages/ml/features.py`
- `packages/ml/datasets.py`
- `packages/ml/models.py`
- `packages/ml/training.py`
- `packages/ml/validation.py`
- `packages/ml/inference.py`

## AI agent
- `packages/ai-agent/agent.py`
- `packages/ai-agent/tools.py`
- `packages/ai-agent/planner.py`
- `packages/ai-agent/researcher.py`
- `packages/ai-agent/strategy_builder.py`
- `packages/ai-agent/report.py`
- `packages/ai-agent/memory.py`

## Execution
- `packages/execution/broker.py`
- `packages/execution/order_manager.py`
- `packages/execution/execution_simulator.py`
- `packages/execution/paper_broker.py`
- `packages/execution/live_broker.py`
- `packages/execution/reconciliation.py`

## Data/infrastructure
- `infra/database/migrations/`
- `infra/docker/`
- `infra/deployment/`
- `scripts/seed_sample_data.py`
- `scripts/run_backtest.py`
- `scripts/validate_data.py`

## Tests
- `tests/unit/`
- `tests/integration/`
- `tests/backtest/`
- `tests/data-quality/`

## Rule for Vibe Coding
When implementing a file, inspect adjacent interfaces first, implement only what its callers need, add a test, then integrate. Avoid generating hundreds of disconnected stubs. The goal is a runnable system at every stage.
