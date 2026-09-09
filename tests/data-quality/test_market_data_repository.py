from datetime import datetime, timezone
from decimal import Decimal

from packages.market_data.models import Candle
from packages.market_data.repository import InMemoryCandleRepository


def candle(ts: int) -> Candle:
    return Candle(
        timestamp=datetime.fromtimestamp(ts, tz=timezone.utc),
        symbol="NIFTY",
        timeframe="5m",
        open=Decimal("100"), high=Decimal("102"), low=Decimal("99"),
        close=Decimal("101"), volume=Decimal("10"),
    )


def test_repository_is_idempotent_and_sorted() -> None:
    repo = InMemoryCandleRepository()
    rows = [candle(120), candle(60)]
    assert repo.save(rows, "provider-v1") == 2
    assert repo.save(rows, "provider-v1") == 0
    loaded = repo.load("NIFTY", "5m", candle(0).timestamp, candle(180).timestamp)
    assert [c.timestamp for c in loaded] == [candle(60).timestamp, candle(120).timestamp]


def test_empty_data_version_rejected() -> None:
    repo = InMemoryCandleRepository()
    try:
        repo.save([candle(60)], " ")
    except ValueError as exc:
        assert "data_version" in str(exc)
    else:
        raise AssertionError("expected ValueError")
