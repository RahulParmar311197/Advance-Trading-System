from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Mapping

from .provider import MarketDataProvider
from .schemas import RawOHLCV


class CSVMarketDataProvider(MarketDataProvider):
    """Read provider-supplied OHLCV CSV data without inventing missing observations.

    The CSV must contain timestamp, symbol, timeframe, open, high, low, close,
    and volume columns. Column names can be changed through ``columns``. This
    adapter intentionally does not fill gaps, repair prices, or synthesize rows;
    normal validation remains the responsibility of the ingestion pipeline.
    """

    REQUIRED_FIELDS = ("timestamp", "symbol", "timeframe", "open", "high", "low", "close", "volume")

    def __init__(self, path: str | Path, columns: Mapping[str, str] | None = None) -> None:
        self._path = Path(path)
        self._columns = dict(columns or {})
        unknown = set(self._columns) - set(self.REQUIRED_FIELDS)
        if unknown:
            raise ValueError(f"unsupported column mappings: {sorted(unknown)}")

    def historical_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[RawOHLCV]:
        if start.tzinfo is None or start.utcoffset() is None:
            raise ValueError("start must be timezone-aware")
        if end.tzinfo is None or end.utcoffset() is None:
            raise ValueError("end must be timezone-aware")
        if end <= start:
            raise ValueError("end must be after start")
        if not symbol.strip() or not timeframe.strip():
            raise ValueError("symbol and timeframe are required")
        if not self._path.is_file():
            raise FileNotFoundError(self._path)

        with self._path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = set(reader.fieldnames or ())
            missing = [self._column(field) for field in self.REQUIRED_FIELDS if self._column(field) not in headers]
            if missing:
                raise ValueError(f"CSV missing required columns: {missing}")

            rows: list[RawOHLCV] = []
            for line_number, row in enumerate(reader, start=2):
                try:
                    timestamp = self._parse_timestamp(row, "timestamp")
                    row_symbol = self._required_text(row, "symbol")
                    row_timeframe = self._required_text(row, "timeframe")
                    values = {
                        field: self._parse_decimal(row, field)
                        for field in ("open", "high", "low", "close", "volume")
                    }
                except (ValueError, InvalidOperation) as exc:
                    raise ValueError(f"invalid OHLCV row at CSV line {line_number}: {exc}") from exc

                if row_symbol != symbol or row_timeframe != timeframe:
                    continue
                if start <= timestamp < end:
                    rows.append(
                        RawOHLCV(
                            timestamp=timestamp,
                            symbol=row_symbol,
                            timeframe=row_timeframe,
                            **values,
                        )
                    )

        return rows

    def _column(self, field: str) -> str:
        return self._columns.get(field, field)

    def _required_text(self, row: dict[str, str], field: str) -> str:
        value = row.get(self._column(field), "")
        if not value or not value.strip():
            raise ValueError(f"{field} is required")
        return value.strip()

    def _parse_timestamp(self, row: dict[str, str], field: str) -> datetime:
        value = self._required_text(row, field)
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return timestamp

    def _parse_decimal(self, row: dict[str, str], field: str) -> Decimal:
        value = self._required_text(row, field)
        return Decimal(value)
