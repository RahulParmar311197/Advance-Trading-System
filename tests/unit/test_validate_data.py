from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.validate_data import validate_csv


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = ["timestamp", "symbol", "timeframe", "open", "high", "low", "close", "volume"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _window() -> tuple[datetime, datetime]:
    return (
        datetime(2026, 1, 5, 9, 15, tzinfo=timezone.utc),
        datetime(2026, 1, 5, 9, 30, tzinfo=timezone.utc),
    )


def test_validate_csv_accepts_provider_supplied_rows(tmp_path: Path) -> None:
    path = tmp_path / "provider.csv"
    _write_csv(
        path,
        [
            {"timestamp": "2026-01-05T09:15:00+00:00", "symbol": "NIFTY", "timeframe": "5m", "open": "100", "high": "102", "low": "99", "close": "101", "volume": "10"},
            {"timestamp": "2026-01-05T09:20:00+00:00", "symbol": "NIFTY", "timeframe": "5m", "open": "101", "high": "103", "low": "100", "close": "102", "volume": "11"},
            {"timestamp": "2026-01-05T09:25:00+00:00", "symbol": "NIFTY", "timeframe": "5m", "open": "102", "high": "104", "low": "101", "close": "103", "volume": "12"},
        ],
    )

    report = validate_csv(path, "NIFTY", "5m", *_window())

    assert report["candle_count"] == 3
    assert report["missing_candle_count"] == 0
    assert report["missing_candles"] == []


def test_validate_csv_reports_missing_session_candles_without_repairing(tmp_path: Path) -> None:
    path = tmp_path / "provider.csv"
    _write_csv(
        path,
        [
            {"timestamp": "2026-01-05T09:15:00+00:00", "symbol": "NIFTY", "timeframe": "5m", "open": "100", "high": "102", "low": "99", "close": "101", "volume": "10"},
            {"timestamp": "2026-01-05T09:25:00+00:00", "symbol": "NIFTY", "timeframe": "5m", "open": "102", "high": "104", "low": "101", "close": "103", "volume": "12"},
        ],
    )

    report = validate_csv(path, "NIFTY", "5m", *_window())

    assert report["candle_count"] == 2
    assert report["missing_candle_count"] == 1
    assert report["missing_candles"] == ["2026-01-05T09:20:00+00:00"]


def test_validate_csv_rejects_invalid_ohlc(tmp_path: Path) -> None:
    path = tmp_path / "provider.csv"
    _write_csv(
        path,
        [
            {"timestamp": "2026-01-05T09:15:00+00:00", "symbol": "NIFTY", "timeframe": "5m", "open": "100", "high": "99", "low": "98", "close": "99", "volume": "10"},
        ],
    )

    with pytest.raises(ValueError, match="invalid OHLC range"):
        validate_csv(path, "NIFTY", "5m", *_window())


def test_validate_csv_supports_explicit_column_mapping(tmp_path: Path) -> None:
    path = tmp_path / "provider.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["time", "ticker", "bar", "o", "h", "l", "c", "v"],
        )
        writer.writeheader()
        writer.writerow(
            {"time": "2026-01-05T09:15:00+00:00", "ticker": "NIFTY", "bar": "5m", "o": "100", "h": "102", "l": "99", "c": "101", "v": "10"}
        )

    report = validate_csv(
        path,
        "NIFTY",
        "5m",
        *_window(),
        columns={
            "timestamp": "time",
            "symbol": "ticker",
            "timeframe": "bar",
            "open": "o",
            "high": "h",
            "low": "l",
            "close": "c",
            "volume": "v",
        },
    )

    assert report["candle_count"] == 1
