# Advance Trading System

AI Quant Platform for Indian markets, following the project source specification.

## Initial vertical slice

NIFTY historical data → 5m candles → deterministic SMC → Liquidity Sweep + MSS + FVG → backtest → risk checks → reproducible research report.

## Repository roadmap

```text
apps/
  web/              # Next.js dashboard
  api/              # FastAPI service
  worker/           # background jobs
packages/
  market-data/      # ingestion, schemas, validation, normalization
  instruments/      # symbols, expiry, trading calendar
  indicators/       # technical indicators
  smc/              # deterministic SMC/ICT event detection
  strategies/       # strategy framework and signals
  backtest/         # event-driven simulator, fills, costs, metrics
  portfolio/        # portfolio state and allocation
  risk/             # limits, exposure, drawdown, kill switch
  execution/        # broker abstraction and paper/live adapters
  options/          # chain, Greeks, IV, OI, payoff
  ml/               # datasets, models, validation, inference
  ai-agent/         # research orchestration and reports
research/           # hypotheses, experiments, notebooks, reports
data/               # raw, processed, features, metadata
tests/              # unit, integration, backtest, data-quality
infra/              # Docker, database, deployment
docs/               # architecture, data, strategies, research, operations
scripts/            # operational and development scripts
```

## Build sequence

1. Foundation: market data + instruments + PostgreSQL.
2. Deterministic analysis: indicators + SMC events.
3. Research + backtest: experiments, costs, slippage, metrics.
4. Strategy framework: configurable strategies.
5. Risk + portfolio.
6. Options + microstructure + regime.
7. ML and AI research agent.
8. Paper trading → production execution.

Keep raw market data immutable and make every experiment reproducible using data version, strategy version, parameters, universe, timeframe, cost model, slippage, random seed, and results.
