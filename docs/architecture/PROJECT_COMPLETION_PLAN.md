# Project Completion Plan

## Objective
Turn the architecture in the project source into a continuously runnable Indian quantitative trading research platform, then extend it to paper/live execution and SaaS.

## Current continuation state
M10 broker interface, deterministic paper broker, order manager, execution simulator, reconciliation, disabled-by-default live adapter, and fail-closed execution monitoring are implemented with unit tests. Live-adapter CI passed; the latest monitoring/kill-switch integration revision is awaiting authoritative CI verification. Next dependency is to verify that revision, then continue M10 hardening/production execution controls.

### M10 Paper/live execution — current state
- Broker interface: complete and CI verified.
- Paper broker: complete and CI verified.
- Order manager: complete and CI verified in integrated revision; now additionally gates new submissions through the optional risk kill switch.
- Execution simulator: complete and CI verified.
- Reconciliation: complete and CI verified.
- Live adapter: complete, disabled by default, CI verified.
- Execution monitoring: implementation and unit tests complete; latest authoritative CI verification pending.
- Kill-switch integration: implementation and unit tests complete; latest authoritative CI verification pending.

## Milestones

### M0 Bootstrap
- [x] Repository structure
- [x] Python package configuration
- [x] Environment template
- [x] Docker Compose
- [x] CI workflow added
- [x] Health endpoint

### M1 Data foundation
- [x] Provider interface
- [x] Historical OHLCV ingestion
- [x] Normalization
- [x] Validation
- [x] Instruments
- [x] Symbol mapping
- [x] Trading calendar
- [x] PostgreSQL migrations/integration — implementation, integration test, and CI verification pass
- [x] Immutable raw storage
- [x] Data-quality tests
- [ ] Authorized real historical provider configured for Indian market data

### M2 Analytics foundation
- [x] EMA
- [x] ATR
- [x] VWAP
- [x] Swing highs/lows
- [x] BOS
- [x] MSS
- [x] Liquidity sweep
- [x] FVG
- [x] Structured event schema integration

### M3 Strategy/backtest
- [x] Strategy base/registry
- [x] Liquidity MSS FVG
- [x] Event-driven backtest
- [x] Fills
- [x] Position sizing
- [x] Brokerage/fees
- [x] Slippage
- [x] Equity curve — realized, candle-aligned curve returned by the API and rendered in the dashboard
- [x] Performance metrics
- [x] Risk limits
- [x] Kill switch

### M4 Research
- [x] Experiment schema
- [x] Dataset/version metadata
- [x] Parameter capture
- [x] Walk-forward — rolling train/test window engine implemented with OOS execution and tests; CI verification pending
- [x] Out-of-sample — explicit final holdout evaluator implemented with train-only fitting, holdout-only execution and tests; CI verification pending
- [x] Stress tests — deterministic scenario runner varies explicit slippage and risk assumptions against the same strategy/data, with unit tests; CI verification pending
- [x] Strategy comparison — deterministic comparison of reproducible experiment metrics, ranked by return then drawdown; API integration and JSON-safe output added
- [x] Research report generation — factual Markdown report generated from persisted comparison results; API and dashboard integration added
- [x] Portfolio exposure aggregation — deterministic symbol-level absolute notional exposure
- [x] Portfolio correlation — deterministic Pearson correlation matrix for supplied return series
- [x] Backtest broker simulator — deterministic slippage/commission fill model
- [x] Backtest portfolio curve — realized equity/ending-equity accounting from completed trades
- [x] Core `packages/portfolio/portfolio.py` accounting upgrade — deterministic realized P&L, trade recording, equity, and candle-indexed realized curve

### M5 Web/API
- [x] Market data endpoints
- [x] SMC event contract
- [x] Backtest execution endpoint
- [x] Experiment endpoints
- [x] Dashboard implementation — Next.js page consumes candles, SMC events, backtest results and experiments
- [x] Candlestick chart implementation
- [x] Signal/event overlays
- [x] Backtest results view
- [x] Experiment table
- [x] Research comparison/report view
- [x] Dashboard runtime/build verification in CI
- [ ] Full-stack acceptance with supplied/real market data

### M6 Options
- [x] Chain model
- [x] Greeks
- [x] IV
- [x] OI/OI change
- [x] PCR
- [x] Term structure
- [x] Volatility surface
- [x] Payoff analysis

### M7 Microstructure
- [x] Spread
- [x] Depth
- [x] Imbalance
- [x] Trade flow
- [x] Trade intensity
- [x] Price impact
- [x] Liquidity/resiliency

### M8 Regime/ML
- [x] Regime features
- [x] Regime detector
- [x] Regime classifier
- [x] Transitions
- [x] Dataset builder
- [x] Logistic baseline
- [x] Random Forest
- [x] Gradient boosting
- [x] Out-of-sample model validation
- [x] Model versioning

### M9 AI research agent
- [x] Agent interface
- [x] Research planner
- [x] Tool registry
- [x] Historical data tool
- [x] Feature tool
- [x] SMC tool
- [x] Backtest tool
- [x] Walk-forward tool
- [x] Strategy comparison tool
- [x] Risk analysis tool
- [x] Report tool
- [x] Experiment memory

### M10 Paper/live execution
- [x] Broker interface
- [x] Paper broker
- [x] Order manager
- [x] Execution simulator
- [x] Reconciliation
- [x] Live adapter behind feature flag
- [ ] Execution monitoring — implementation and unit tests complete; authoritative CI pending
- [ ] Kill switch integration — OrderManager blocks new submissions while active while preserving existing-order cancellation/status; implementation and unit tests complete; authoritative CI pending

### M11 Production/SaaS
- [ ] Authentication
- [ ] Authorization
- [ ] Organizations
- [ ] API keys
- [ ] Audit logs
- [ ] Redis/cache
- [ ] Queue/workers
- [ ] Scheduled jobs
- [ ] Monitoring
- [ ] Alerts
- [ ] Error tracking
- [ ] Data-quality monitoring
- [ ] Deployment
- [ ] Billing hooks

### M12 Hardening
- [ ] Bad-data tests
- [ ] Missing-candle tests
- [ ] Duplicate-tick tests
- [ ] Timestamp tests
- [ ] Market-closure tests
- [ ] Network failure tests
- [ ] Database failure tests
- [ ] Broker failure tests
- [ ] Partial-fill tests
- [ ] Rejected-order tests
- [ ] API timeout tests
- [ ] Recovery/runbook tests

## Critical acceptance test
A fresh developer must be able to start the stack, load sample NIFTY data, open the dashboard, see 5m candles and SMC events, run the Liquidity MSS FVG backtest, see realistic metrics, and reproduce the experiment from its recorded metadata.

## Delivery rule
Do not mark a milestone complete because files exist. Mark it complete only when the code runs and its acceptance tests pass.
