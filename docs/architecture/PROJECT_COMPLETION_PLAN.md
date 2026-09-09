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
- [x] Chain model — validated immutable option contracts and chain grouping with strike/call/put accessors
- [x] Greeks — dependency-free European Black-Scholes Greeks with input validation and parity tests
- [x] IV — deterministic Black-Scholes price inversion by bisection with no-arbitrage validation and unit tests
- [x] OI/OI change — deterministic calculation from supplied option-chain snapshots; missing and duplicate observations fail closed
- [x] PCR — deterministic put/call open-interest ratio from supplied option-chain observations; missing OI and zero call OI fail closed, with unit tests and Python CI verification
- [x] Term structure — deterministic ordering of supplied implied-volatility observations by expiry; empty and duplicate observations fail closed, with unit tests and Python CI verification
- [x] Volatility surface — deterministic ordering of supplied implied-volatility observations by expiry and strike; implementation and unit tests committed, authoritative CI verification pass on full-suite head
- [x] Payoff analysis — deterministic expiry P&L for supplied option legs; implementation and unit tests committed, authoritative CI verification pass on full-suite head

### M7 Microstructure
- [x] Spread — deterministic bid/ask spread and relative-spread implementation and unit tests; authoritative Python CI verification pass
- [x] Depth — deterministic validated level-2 bid/ask snapshot, best levels, visible total depth, and bounded depth queries; implementation and unit tests; authoritative Python CI verification pass
- [x] Imbalance — deterministic normalized bid/ask and supplied-depth quantity imbalance; implementation and unit tests; authoritative Python CI verification pass
- [x] Trade flow — deterministic signed executed-volume and normalized buy/sell flow imbalance using explicitly supplied trade sides; implementation and unit tests; authoritative Python CI verification pass
- [x] Trade intensity — deterministic supplied-trade count per explicitly supplied observation window; targeted checks and authoritative Python CI verification pass on run `34333070096`
- [x] Price impact — deterministic signed notional, quantity-weighted execution VWAP, and implementation-shortfall analytics from supplied trade prints; tests and authoritative Python CI verification pass on run `34333070096`
- [x] Liquidity/resiliency — deterministic visible-depth and quoted-spread liquidity snapshot plus depth/spread recovery ratios from explicitly supplied initial, stressed, and recovered observations; unit tests and authoritative Python CI verification pass on run `34333173992`

### M8 Regime/ML
- [ ] Regime features — deterministic period return, mean absolute return, OLS close-price slope, path efficiency, and average volume implementation with unit tests; authoritative Python CI verification pending after one genuine fixture/assertion failure was corrected
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
