from datetime import datetime, timedelta, timezone
from decimal import Decimal

from packages.market_data.ingestion import ingest_historical_ohlcv
from packages.market_data.provider_memory import InMemoryMarketDataProvider
from packages.market_data.repository import InMemoryCandleRepository
from packages.market_data.schemas import RawOHLCV


def test_ingestion_normalizes_valid_provider_rows_and_persists() -> None:
    start = datetime(2026, 1, 1, 9, 15, tzinfo=timezone.utc)
    rows = [RawOHLCV(start + timedelta(minutes=5 * i), "NIFTY", "5m", Decimal(100+i), Decimal(102+i), Decimal(99+i), Decimal(101+i), Decimal(1000)) for i in range(2)]
    provider = InMemoryMarketDataProvider(rows)
    repo = InMemoryCandleRepository()
    result = ingest_historical_ohlcv(provider, repo, "NIFTY", "5m", start, start + timedelta(minutes=10), "fixture-v1")
    assert len(result) == 2
    assert len(repo.load("NIFTY", "5m", start, start + timedelta(minutes=10))) == 2
