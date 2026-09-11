# Provider-supplied CSV market-data import

`packages.market_data.csv_provider.CSVMarketDataProvider` is a strict local adapter for historical OHLCV files obtained from an external market-data source.

## Contract

The input CSV must provide timestamp, symbol, timeframe, open, high, low, close, and volume columns. Explicit column mappings are supported when a provider uses different names.

Timestamps must include timezone information. Rows are filtered by the requested symbol, timeframe, and half-open `[start, end)` interval.

The adapter does **not**:

- synthesize candles;
- forward-fill missing observations;
- repair prices or volumes;
- infer a trading calendar;
- claim that the source is an authorized Indian market-data provider.

The returned `RawOHLCV` rows should pass through the existing normalization and validation pipeline before persistence.

## Example

```python
from datetime import datetime, timezone
from packages.market_data.csv_provider import CSVMarketDataProvider

provider = CSVMarketDataProvider("/data/provider/nifty_5m.csv")
rows = provider.historical_ohlcv(
    "NIFTY",
    "5m",
    datetime(2026, 1, 1, tzinfo=timezone.utc),
    datetime(2026, 2, 1, tzinfo=timezone.utc),
)
```

This adapter is useful when real provider data is supplied as a file, but it does not remove the project requirement to configure and validate an authorized real Indian historical-data service for production ingestion.
