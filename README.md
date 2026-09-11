# Advance Trading System

First working slice: market-data normalization/validation, instruments/calendar, deterministic indicators and SMC, Liquidity MSS FVG strategy, cost/slippage-aware backtesting, risk primitives, and FastAPI boundaries.

## Quick start

```bash
pip install -e .
python -m pytest
uvicorn apps.api.app.main:app --reload
```

The repository does not fabricate historical data or backtest performance. Any smoke fixture used by tests is explicitly synthetic.

## Validate provider-supplied OHLCV

For a real provider-supplied CSV, validate the requested symbol/timeframe/window before sending the rows into the ingestion pipeline:

```bash
python scripts/validate_data.py /data/provider/nifty_5m.csv \\
  --symbol NIFTY \\
  --timeframe 5m \\
  --start 2026-01-01T03:45:00+00:00 \\
  --end 2026-02-01T03:45:00+00:00
```

The command is read-only. It parses timezone-aware timestamps, applies the strict CSV provider contract, runs canonical OHLCV validation, and reports session-aware missing candles. It never fills gaps, repairs observations, or persists changes. Provider-specific column names can be mapped with repeated `--column FIELD=CSV_COLUMN` arguments.

This validation command does not turn a CSV into an authorized Indian market-data source; production provider authorization and a documented response contract remain required.
