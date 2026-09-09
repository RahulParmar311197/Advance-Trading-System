from datetime import datetime, timezone
from decimal import Decimal

from packages.market_data.models import Candle
from packages.smc.bos import BOSEvent
from packages.smc.fvg import FVG
from packages.smc.liquidity import LiquiditySweep
from packages.smc.mss import MSSEvent
from packages.smc.events import all_smc_events


def candle(i: int) -> Candle:
    return Candle(
        datetime(2026, 1, 1, 9, 15 + i, tzinfo=timezone.utc),
        "NIFTY",
        "5m",
        Decimal("100"), Decimal("102"), Decimal("99"), Decimal("101"), Decimal("1000"),
    )


def test_all_smc_events_uses_common_contract_and_preserves_order() -> None:
    candles = [candle(i) for i in range(4)]
    events = all_smc_events(
        candles,
        bos=[BOSEvent(1, "bullish", Decimal("100"))],
        mss=[MSSEvent(2, "bearish", Decimal("101"))],
        liquidity=[LiquiditySweep(0, "bullish", Decimal("99"))],
        fvg=[FVG(3, "bullish", Decimal("102"), Decimal("103"))],
    )

    assert [event.event for event in events] == ["liquidity_sweep", "bos", "mss", "fvg"]
    assert events[0].symbol == "NIFTY"
    assert events[0].timeframe == "5m"
    assert events[0].timestamp == candles[0].timestamp
    assert events[3].price == Decimal("102.5")
    assert events[3].metadata == {"low": Decimal("102"), "high": Decimal("103")}


def test_event_serialization_is_explicit_and_does_not_invent_confidence() -> None:
    candles = [candle(0)]
    events = all_smc_events(candles, liquidity=[LiquiditySweep(0, "bullish", Decimal("99"))])
    record = events[0].as_dict()
    assert record["event"] == "liquidity_sweep"
    assert record["price"] == Decimal("99")
    assert record["confidence"] is None
