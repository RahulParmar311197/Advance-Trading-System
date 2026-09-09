from datetime import datetime, timezone
from decimal import Decimal

import pytest

from packages.ai_agent.historical_data import HistoricalDataRequest, get_historical_data
from packages.market_data.provider_static import StaticOHLCVProvider
from packages.market_data.schemas import RawOHLCV


def rows() -> list[RawOHLCV]:
    return [
        RawOHLCV(
            timestamp=datetime(2026, 1, 2, 9, 20, tzinfo=timezone.utc),
            symbol="NIFTY",
            timeframe="5m",
            open=Decimal("100"),
            high=Decimal("102"),
            low=Decimal("99"),
            close=Decimal("101"),
            volume=Decimal("10"),
        ),
        RawOHLCV(
            timestamp=datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc),
            symbol="NIFTY",
            timeframe="5m",
            open=Decimal("99"),
            high=Decimal("101"),
            low=Decimal("98"),
            close=Decimal("100"),
            volume=Decimal("9"),
        ),
    ]


def request() -> HistoricalDataRequest:
    return HistoricalDataRequest(
        symbol="NIFTY",
        timeframe="5m",
        start=datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc),
        end=datetime(2026, 1, 2, 9, 20, tzinfo=timezone.utc),
    )


def test_historical_data_tool_normalizes_and_validates_provider_rows():
    result = get_historical_data(StaticOHLCVProvider(rows()), request())

    assert [c.timestamp for c in result.candles] == [
        datetime(2026, 1, 2, 9, 15, tzinfo=timezone.utc),
        datetime(2026, 1, 2, 9, 20, tzinfo=timezone.utc),
    ]
    assert result.candles[0].symbol == "NIFTY"
    assert result.candles[0].timeframe == "5m"


def test_historical_data_tool_returns_only_provider_supplied_rows():
    result = get_historical_data(StaticOHLCVProvider(rows()), request())
    assert len(result.candles) == 2


def test_request_rejects_invalid_scope():
    with pytest.raises(ValueError, match="symbol"):
        HistoricalDataRequest(
            symbol=" ", timeframe="5m", start=request().start, end=request().end
        )
    with pytest.raises(ValueError, match="timeframe"):
        HistoricalDataRequest(
            symbol="NIFTY", timeframe=" ", start=request().start, end=request().end
        )
    with pytest.raises(ValueError, match="start"):
        HistoricalDataRequest(
            symbol="NIFTY", timeframe="5m", start=request().end, end=request().start
        )


def test_invalid_provider_data_fails_closed():
    invalid = rows()
    invalid[1] = RawOHLCV(
        timestamp=invalid[1].timestamp,
        symbol="NIFTY",
        timeframe="5m",
        open=Decimal("100"),
        high=Decimal("99"),
        low=Decimal("98"),
        close=Decimal("100"),
        volume=Decimal("9"),
    )
    with pytest.raises(ValueError, match="OHLC"):
        get_historical_data(StaticOHLCVProvider(invalid), request())
