from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from packages.market_data.csv_provider import CSVMarketDataProvider


CSV = """timestamp,symbol,timeframe,open,high,low,close,volume\n2026-01-02T09:15:00+05:30,NIFTY,5m,100,101,99,100.5,1000\n2026-01-02T09:20:00+05:30,NIFTY,5m,100.5,102,100,101.5,1100\n2026-01-02T09:25:00+05:30,BANKNIFTY,5m,200,201,199,200.5,900\n"""


def window() -> tuple[datetime, datetime]:
    start = datetime(2026, 1, 2, 9, 15, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    return start, start + timedelta(minutes=15)


def test_provider_reads_only_requested_symbol_and_time_window(tmp_path: Path):
    path = tmp_path / "nifty.csv"
    path.write_text(CSV, encoding="utf-8")

    start, end = window()
    rows = CSVMarketDataProvider(path).historical_ohlcv("NIFTY", "5m", start, end)

    assert len(rows) == 2
    assert rows[0].close == 100.5
    assert rows[1].volume == 1100
    assert all(row.symbol == "NIFTY" for row in rows)


def test_provider_supports_explicit_column_mapping(tmp_path: Path):
    path = tmp_path / "provider.csv"
    path.write_text(
        CSV.replace("timestamp,symbol,timeframe,open,high,low,close,volume", "ts,ticker,interval,o,h,l,c,v"),
        encoding="utf-8",
    )

    start, end = window()
    rows = CSVMarketDataProvider(
        path,
        columns={
            "timestamp": "ts",
            "symbol": "ticker",
            "timeframe": "interval",
            "open": "o",
            "high": "h",
            "low": "l",
            "close": "c",
            "volume": "v",
        },
    ).historical_ohlcv("NIFTY", "5m", start, end)

    assert len(rows) == 2


def test_provider_rejects_missing_columns(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text("timestamp,symbol,timeframe,open,high,low,close\n", encoding="utf-8")

    start, end = window()
    with pytest.raises(ValueError, match="missing required columns"):
        CSVMarketDataProvider(path).historical_ohlcv("NIFTY", "5m", start, end)


def test_provider_rejects_naive_timestamp(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text(CSV.replace("2026-01-02T09:15:00+05:30", "2026-01-02T09:15:00"), encoding="utf-8")

    start, end = window()
    with pytest.raises(ValueError, match="timezone-aware"):
        CSVMarketDataProvider(path).historical_ohlcv("NIFTY", "5m", start, end)


def test_provider_does_not_fill_missing_rows(tmp_path: Path):
    path = tmp_path / "sparse.csv"
    path.write_text(CSV.splitlines()[0] + "\n" + CSV.splitlines()[1] + "\n", encoding="utf-8")

    start, end = window()
    rows = CSVMarketDataProvider(path).historical_ohlcv("NIFTY", "5m", start, end)

    assert len(rows) == 1
