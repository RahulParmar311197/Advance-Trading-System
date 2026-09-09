# Advance Trading System

First working slice: market-data normalization/validation, instruments/calendar, deterministic indicators and SMC, Liquidity MSS FVG strategy, cost/slippage-aware backtesting, risk primitives, and FastAPI boundaries.

## Quick start

```bash
pip install -e .
python -m pytest
uvicorn apps.api.app.main:app --reload
```

The repository does not fabricate historical data or backtest performance. Any smoke fixture used by tests is explicitly synthetic.
