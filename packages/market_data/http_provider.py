from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .provider import MarketDataProvider
from .schemas import RawOHLCV


class AuthorizedHTTPMarketDataProvider(MarketDataProvider):
    """Provider adapter for an authorized HTTP OHLCV data service.

    The service must return a JSON array (or ``{"data": [...]}``) containing
    timestamp, symbol, timeframe, open, high, low, close and volume fields.
    No rows are synthesized, interpolated, or silently filled.
    """

    def __init__(self, base_url: str, api_key: str | None = None, timeout_seconds: float = 15.0) -> None:
        if not base_url.startswith(("https://", "http://")):
            raise ValueError("base_url must be an HTTP(S) URL")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def historical_ohlcv(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[RawOHLCV]:
        if start > end:
            raise ValueError("start must be <= end")
        query = urlencode({
            "symbol": symbol,
            "timeframe": timeframe,
            "start": start.isoformat(),
            "end": end.isoformat(),
        })
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(f"{self.base_url}?{query}", headers=headers, method="GET")
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.load(response)
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(f"market-data provider request failed: {exc}") from exc

        rows = payload.get("data") if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise ValueError("provider response must be a JSON array or an object with a data array")
        return [self._parse_row(item, symbol, timeframe) for item in rows]

    @staticmethod
    def _parse_row(item: object, symbol: str, timeframe: str) -> RawOHLCV:
        if not isinstance(item, dict):
            raise ValueError("provider row must be an object")
        required = ("timestamp", "open", "high", "low", "close", "volume")
        missing = [field for field in required if field not in item]
        if missing:
            raise ValueError(f"provider row missing required fields: {', '.join(missing)}")
        timestamp = item["timestamp"]
        if not isinstance(timestamp, str):
            raise ValueError("timestamp must be an ISO-8601 string")
        parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return RawOHLCV(
            timestamp=parsed_timestamp,
            symbol=str(item.get("symbol", symbol)),
            timeframe=str(item.get("timeframe", timeframe)),
            open=Decimal(str(item["open"])),
            high=Decimal(str(item["high"])),
            low=Decimal(str(item["low"])),
            close=Decimal(str(item["close"])),
            volume=Decimal(str(item["volume"])),
        )
