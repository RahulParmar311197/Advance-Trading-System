# Advance Trading System — Vibe Coding Master Guide

## Mission
Build the entire Advance Trading System as a working, testable, reproducible platform as fast as practical. Work vertically: every milestone must leave the repository runnable.

## Source of truth
Use `docs/architecture/REQUIRED_FILES.md` and the project source specification as the architecture baseline. Do not invent a second architecture.

## Development rules
1. Prefer a thin working implementation over empty abstractions.
2. Keep interfaces stable so providers, brokers and strategies can be swapped.
3. Deterministic calculations stay in Python; AI explains/orchestrates and never bypasses risk.
4. Raw market data is immutable. Derived data is versioned.
5. Every backtest must record data version, strategy version, parameters, costs, slippage and results.
6. No live trading by default. Paper trading is the default execution mode.
7. Never fabricate market data, fills, broker responses or performance.
8. Fail closed: missing/invalid data or risk violations mean no new trade.
9. Add tests with each module; prioritize data quality, SMC correctness, backtest accounting and risk.
10. Avoid premature complexity. Advanced ML/microstructure/options should plug into the same feature/signal/risk pipeline.

## Build order
### P0 — Working vertical slice
Market data abstraction → instruments/calendar → OHLCV storage → chart/API → indicators → deterministic SMC → Liquidity Sweep + MSS + FVG strategy → event backtester → costs/slippage → metrics → risk → experiment record → web results.

### P1 — Research platform
More indicators/SMC events → strategy registry → walk-forward validation → stress testing → portfolio accounting → experiment comparison → research reports.

### P2 — Advanced market intelligence
Options chain/Greeks/IV/OI → volatility surface → market microstructure → order-flow features → regime detector.

### P3 — ML and AI research
Feature datasets → baseline models → out-of-sample validation → model registry → AI research agent tools → hypothesis generation → automated experiment workflow → report generation.

### P4 — Execution
Broker interface → paper broker → order manager → reconciliation → live broker adapter only after paper validation → execution monitoring and kill switch.

### P5 — Production/SaaS
Authentication → permissions → audit logs → queues → Redis → monitoring → alerts → data quality jobs → deployment → billing hooks → operational hardening.

## Required first user journey
1. Open dashboard.
2. Select NIFTY and 5m.
3. Load historical OHLCV.
4. Display candles.
5. Display deterministic swing/BOS/MSS/liquidity/FVG events.
6. Select `Liquidity MSS FVG`.
7. Configure risk and RR.
8. Run backtest.
9. Show equity curve, trades and metrics.
10. Save reproducible experiment.
11. Compare experiments.

## Definition of done
A module is done only when it has implementation + public interface + validation + tests + documentation/example + integration into the running application where applicable.

## Suggested implementation loop
For each task:
- Read the relevant source/spec.
- Inspect existing files before editing.
- Implement the smallest real version.
- Add unit tests.
- Add integration test when it crosses a package boundary.
- Run formatting/lint/type checks/tests.
- Update docs.
- Commit with a focused message.
- Continue to the next dependency; do not wait for the whole project to be perfect.

## Parallelization
Safe parallel workstreams:
- Data/instruments
- SMC/indicators
- Backtester/risk
- API
- Web dashboard
- Tests/docs/CI

Merge dependencies in this order:
`data + instruments` → `features/SMC` → `strategy` → `backtest/risk` → `API` → `web` → `research agent` → `execution` → `production`.

## Performance principles
- Use Polars/Pandas appropriately for batch research.
- Use PostgreSQL for queryable normalized data and object storage for immutable raw datasets/artifacts.
- Batch historical computations; avoid per-row network/database calls.
- Cache expensive feature calculations and backtest datasets.
- Push long jobs to the worker queue.
- Keep API requests non-blocking for long backtests.

## Research integrity
Never optimize on the test set. Support train/in-sample, validation, out-of-sample and walk-forward periods. Include transaction costs, slippage, brokerage/fees and realistic position sizing. Store experiment metadata so results can be reproduced.

## Safety boundary
The AI agent may propose hypotheses, configure experiments, analyze results and generate reports. It must not disable risk limits, invent missing data, or directly authorize live orders. All execution passes through the risk engine and broker abstraction.

## Fast completion strategy
Do not build every package to production depth before integration. Build the first vertical slice end-to-end, then repeatedly replace thin implementations with stronger ones while keeping interfaces and tests stable. This gives a continuously runnable project and minimizes integration surprises.
