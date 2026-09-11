# Project Completion Plan

## Objective
Turn the architecture in the project source into a continuously runnable Indian quantitative trading research platform, then extend it to paper/live execution and SaaS.

## Current continuation state
M10 execution monitoring and kill-switch integration are CI-verified. M12 hardening is implemented; duplicate-tick testing remains intentionally blocked because the repository has no concrete tick/trade observation model. M11 production/SaaS now has organization-scoped API-key authentication, role authorization, persistent organization/user/API-key repositories, organization-scoped experiment resources, Redis caching, and a recoverable Redis-backed job queue/worker with a real persisted backtest job. Python CI verifies the current queue/worker slice. Next dependency is scheduled jobs.

### M10 Paper/live execution — current state
- Broker interface: complete and CI verified.
- Paper broker: complete and CI verified; supports explicit market/limit/stop fills and explicit partial fills with weighted average price.
- Order manager: complete and CI verified; new submissions are blocked while the optional kill switch is active.
- Execution simulator: complete and CI verified.
- Reconciliation: complete and CI verified.
- Live adapter: complete, disabled by default, CI verified.
- Execution monitoring: complete and CI verified.
- Kill-switch integration: complete and CI verified.

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
- [x] Stress tests — deterministic scenario runner varies explicit slippage and risk assumptions against the same candles and strategy, with unit tests; CI verification pending
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
- [x] Execution monitoring
- [x] Kill switch integration

### M11 Production/SaaS
- [x] Authentication/credential verification boundary — organization-scoped API-key digest verification and fail-closed invalid/inactive handling
- [x] Authorization boundary — role permissions plus organization isolation
- [x] Organizations — database schema introduced
- [x] Users — database schema introduced
- [x] API keys — database schema introduced; secrets stored as digests in the persistence model
- [x] Audit logs — append-only event construction and persistence boundary
- [x] Integrate authentication into API routes — persistent API-key lookup, fail-closed 401 handling, role-based 403 handling, protected market-data/backtest/experiment routes, and integration tests
- [x] Persistent user/organization/API-key repositories — parameterized PostgreSQL create/get/revoke boundaries with unit coverage
- [x] Route-level resource scoping for organization-owned resources — experiment manifests/results/comparison/report queries require the authenticated organization and fail closed for missing scope; Python CI verified on run `34572595333` / job `103177768789`
- [x] Redis/cache — namespaced JSON Redis adapter, bounded TTL, optional API dependency, SMC-event read-through cache, local Redis service, and unit coverage; Python CI verified on run `34572595333` / job `103177768789`
- [x] Queue/workers — FIFO Redis queue with recoverable in-flight claims, acknowledgement/retry/backoff semantics, runnable worker process, Docker worker service, and real PostgreSQL-persisted backtest handler; Python CI verified on run `34573241100` / job `103179806342`
- [ ] Scheduled jobs
- [ ] Monitoring
- [ ] Alerts
- [ ] Error tracking
- [ ] Data-quality monitoring
- [ ] Deployment
- [ ] Billing hooks

### M12 Hardening
- [x] Bad-data tests — OHLC range, negative volume, duplicate/out-of-order timestamps, and timezone-awareness coverage
- [x] Missing-candle tests — session-aware expected-candle detection without reporting overnight/weekend gaps
- [ ] Duplicate-tick tests — blocked until a concrete tick/trade observation model is introduced; do not fabricate one
- [x] Timestamp tests — candle validation rejects naive timestamps
- [x] Market-closure tests — Indian weekday/session boundaries and timezone conversion
- [x] Network failure tests — live broker translates connection/timeout/socket failures to typed `BrokerError`; authoritative Python CI verified previously
- [x] Database failure tests — API translates PostgreSQL operational failures to fail-closed HTTP 503; bounded connection timeout added
- [x] Broker failure tests — typed `BrokerError` contract and OrderManager fail-closed propagation; authoritative Python CI verified on run `34567836083`
- [x] Partial-fill tests — explicit paper partial-fill accumulation, weighted average price, and overfill rejection; authoritative Python CI verified on integrated revision `14533c19`
- [x] Rejected-order tests — rejected broker state propagates through OrderManager and fail-closed fill/cancel behavior; authoritative Python CI verified on integrated revision `14533c19`
- [x] API timeout tests — database connection timeout is bounded and timeout failures return HTTP 503
- [x] Recovery/runbook tests — execution remains blocked for unresolved reconciliation and becomes healthy only after clean reconciliation

## Critical acceptance test
A fresh developer must be able to start the stack, load sample NIFTY data, open the dashboard, see 5m candles and SMC events, run the Liquidity MSS FVG backtest, see realistic metrics, and reproduce the experiment from its recorded metadata.

## Delivery rule
Do not mark a milestone complete because files exist. Mark it complete only when the code runs and its acceptance tests pass.
