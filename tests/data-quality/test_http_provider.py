from datetime import datetime, timezone
from decimal import Decimal
import json

from packages.market_data.http_provider import AuthorizedHTTPMarketDataProvider


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


def test_http_provider_parses_authorized_service_payload(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["authorization"] = request.get_header("Authorization")
        captured["timeout"] = timeout
        return FakeResponse({"data": [{
            "timestamp": "2026-01-01T09:15:00Z",
            "open": "100", "high": "101", "low": "99", "close": "100.5", "volume": "20"
        }]})

    monkeypatch.setattr("packages.market_data.http_provider.urlopen", fake_urlopen)
    provider = AuthorizedHTTPMarketDataProvider("https://data.example.test/ohlcv", api_key="secret", timeout_seconds=7)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = provider.historical_ohlcv("NIFTY", "5m", start, start)

    assert captured["authorization"] == "Bearer secret"
    assert captured["timeout"] == 7
    assert "symbol=NIFTY" in captured["url"]
    assert rows[0].symbol == "NIFTY"
    assert rows[0].close == Decimal("100.5")


def test_http_provider_rejects_malformed_payload(monkeypatch):
    monkeypatch.setattr("packages.market_data.http_provider.urlopen", lambda request, timeout: FakeResponse({"data": [{"close": "100"}]}))
    provider = AuthorizedHTTPMarketDataProvider("https://data.example.test/ohlcv")
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    try:
        provider.historical_ohlcv("NIFTY", "5m", start, start)
    except ValueError as exc:
        assert "missing required fields" in str(exc)
    else:
        raise AssertionError("malformed provider data must fail closed")
