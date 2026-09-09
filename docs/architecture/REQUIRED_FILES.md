# Required Files — Initial Build

## P0: first working vertical slice

```text
apps/api/app/main.py
apps/api/app/config.py
apps/api/app/routes/health.py
apps/api/app/routes/market_data.py
apps/api/app/routes/backtest.py
apps/web/README.md
apps/worker/README.md

packages/market-data/provider.py
packages/market-data/models.py
packages/market-data/schemas.py
packages/market-data/ingestion.py
packages/market-data/normalization.py
packages/market-data/validation.py

packages/instruments/instrument.py
packages/instruments/symbol_map.py
packages/instruments/trading_calendar.py

packages/indicators/atr.py
packages/indicators/ema.py
packages/indicators/vwap.py

packages/smc/swings.py
packages/smc/structure.py
packages/smc/liquidity.py
packages/smc/mss.py
packages/smc/bos.py
packages/smc/fvg.py

packages/strategies/base.py
packages/strategies/rules.py
packages/strategies/signals.py
packages/strategies/registry.py
packages/strategies/liquidity_mss_fvg.py

packages/backtest/engine.py
packages/backtest/events.py
packages/backtest/fills.py
packages/backtest/commission.py
packages/backtest/slippage.py
packages/backtest/position.py
packages/backtest/metrics.py

packages/portfolio/portfolio.py
packages/risk/limits.py
packages/risk/position_sizing.py
packages/risk/drawdown.py
packages/risk/kill_switch.py

research/hypotheses/README.md
research/experiments/README.md
research/reports/README.md

tests/unit/
tests/integration/
tests/backtest/
tests/data-quality/

infra/database/schema.sql
infra/docker/docker-compose.yml
scripts/run_backtest.py
```

## P1: research platform

```text
packages/portfolio/exposure.py
packages/portfolio/correlation.py
packages/backtest/broker_simulator.py
packages/backtest/portfolio.py
research/experiments/runner.py
research/experiments/manifest.py
research/reports/generator.py
```

## P2: advanced market analytics

```text
packages/options/chain.py
packages/options/greeks.py
packages/options/iv.py
packages/options/volatility_surface.py
packages/options/open_interest.py
packages/options/payoff.py

packages/microstructure/spread.py
packages/microstructure/imbalance.py
packages/microstructure/depth.py
packages/microstructure/trade_flow.py
packages/microstructure/price_impact.py
packages/microstructure/liquidity.py
packages/microstructure/execution.py

packages/regime/detector.py
packages/regime/features.py
packages/regime/classifier.py
packages/regime/transitions.py
```

## P3: ML + AI + execution

```text
packages/ml/features.py
packages/ml/datasets.py
packages/ml/models.py
packages/ml/training.py
packages/ml/validation.py
packages/ml/inference.py

packages/ai-agent/agent.py
packages/ai-agent/tools.py
packages/ai-agent/planner.py
packages/ai-agent/researcher.py
packages/ai-agent/strategy_builder.py
packages/ai-agent/report.py
packages/ai-agent/memory.py

packages/execution/broker.py
packages/execution/order_manager.py
packages/execution/execution_simulator.py
packages/execution/paper_broker.py
packages/execution/live_broker.py
packages/execution/reconciliation.py
```

## P0 database tables

- instruments
- candles
- trades
- quotes
- corporate_actions
- trading_sessions
- experiments
- experiment_results

Keep raw source data immutable. Store data version, strategy version, code version, parameters, universe, timeframe, transaction costs, slippage, random seed, and results for every experiment.

## Completion gate for P0

A developer must be able to:

1. Load NIFTY historical OHLCV data.
2. Validate and normalize it.
3. Detect swings, BOS/MSS, liquidity sweeps, and FVG deterministically.
4. Run the Liquidity Sweep + MSS + FVG strategy.
5. Backtest it with costs/slippage and position sizing.
6. Apply risk limits and reject invalid trades.
7. Persist an experiment record.
8. Return metrics and trades through the API.
9. Display the result in the web application.
10. Re-run the experiment from its stored manifest.
