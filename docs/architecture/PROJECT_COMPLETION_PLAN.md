# Project Completion Plan

## Objective
Turn the architecture in the project source into a continuously runnable Indian quantitative trading research platform, then extend it to paper/live execution and SaaS.

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
- [ ] PostgreSQL migrations/integration — implementation and CI test added; latest CI verification pending
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
- [ ] Equity curve
- [x] Performance metrics
- [x] Risk limits
- [x] Kill switch

### M4 Research
- [x] Experiment schema
- [x] Dataset/version metadata
- [x] Parameter capture
- [ ] Walk-forward
- [ ] Out-of-sample
- [ ] Stress tests
- [ ] Strategy comparison
- [ ] Research report generation

### M5 Web/API
- [x] Market data endpoints
- [x] SMC event contract
- [ ] Backtest job endpoint
- [ ] Experiment endpoints — persistence implementation exists; API integration remains
- [ ] Dashboard
- [ ] Candlestick chart
- [ ] Signal/event overlays
- [ ] Backtest results
- [ ] Experiment comparison

### M6 Options
- [ ] Chain model
- [ ] Greeks
- [ ] IV
- [ ] OI/OI change
- [ ] PCR
- [ ] Term structure
- [ ] Volatility surface
- [ ] Payoff analysis

### M7 Microstructure
- [ ] Spread
- [ ] Depth
- [ ] Imbalance
- [ ] Trade flow
- [ ] Trade intensity
- [ ] Price impact
- [ ] Liquidity/resiliency

### M8 Regime/ML
- [ ] Regime features
- [ ] Regime classifier
- [ ] Transitions
- [ ] Dataset builder
- [ ] Logistic baseline
- [ ] Random Forest
- [ ] Gradient boosting
- [ ] Out-of-sample model validation
- [ ] Model versioning

### M9 AI research agent
- [ ] Agent interface
- [ ] Research planner
- [ ] Tool registry
- [ ] Historical data tool
- [ ] Feature tool
- [ ] SMC tool
- [ ] Backtest tool
- [ ] Walk-forward tool
- [ ] Strategy comparison tool
- [ ] Risk analysis tool
- [ ] Report tool
- [ ] Experiment memory

### M10 Paper/live execution
- [ ] Broker interface
- [ ] Paper broker
- [ ] Order manager
- [ ] Execution simulator
- [ ] Reconciliation
- [ ] Live adapter behind feature flag
- [ ] Execution monitoring
- [ ] Kill switch integration

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
