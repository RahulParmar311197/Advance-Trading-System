from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from packages.market_data.csv_provider import CSVMarketDataProvider
from packages.market_data.models import Candle
from packages.market_data.validation import find_missing_candles, validate_ohlcv


def _parse_datetime(value: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid ISO-8601 timestamp: {value}") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise argparse.ArgumentTypeError("timestamps must include timezone information")
    return timestamp


def validate_csv(
    path: str | Path,
    symbol: str,
    timeframe: str,
    start: datetime,
    end: datetime,
    columns: dict[str, str] | None = None,
) -> dict[str, object]:
    """Validate provider-supplied CSV rows through the canonical OHLCV rules.

    This command is deliberately read-only: it never repairs, fills, sorts, or
    persists input data. A successful result therefore means the supplied rows
    are valid as received and that any reported session gaps are observations,
    not automatically repaired data.
    """
    provider = CSVMarketDataProvider(path, columns=columns)
    raw_rows = provider.historical_ohlcv(symbol, timeframe, start, end)
    candles = [
        Candle(
            timestamp=row.timestamp,
            symbol=row.symbol,
            timeframe=row.timeframe,
            open=row.open,
            high=row.high,
            low=row.low,
            close=row.close,
            volume=row.volume,
        )
        for row in raw_rows
    ]
    validate_ohlcv(candles)
    missing = find_missing_candles(candles, timeframe) if candles else ()
    return {
        "path": str(Path(path)),
        "symbol": symbol,
        "timeframe": timeframe,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "candle_count": len(candles),
        "missing_candle_count": len(missing),
        "missing_candles": [timestamp.isoformat() for timestamp in missing],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate provider-supplied OHLCV CSV data.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--start", required=True, type=_parse_datetime)
    parser.add_argument("--end", required=True, type=_parse_datetime)
    parser.add_argument(
        "--column",
        action="append",
        default=[],
        metavar="FIELD=CSV_COLUMN",
        help="Override a CSV column name; may be repeated.",
    )
    return parser


def _parse_columns(values: list[str]) -> dict[str, str]:
    columns: dict[str, str] = {}
    for value in values:
        field, separator, column = value.partition("=")
        if not separator or not field or not column:
            raise ValueError(f"invalid --column mapping: {value!r}")
        columns[field] = column
    return columns


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    try:
        report = validate_csv(
            args.path,
            args.symbol,
            args.timeframe,
            args.start,
            args.end,
            columns=_parse_columns(args.column),
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
