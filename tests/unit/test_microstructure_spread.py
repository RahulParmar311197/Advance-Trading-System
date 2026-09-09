from decimal import Decimal

import pytest

from packages.microstructure.spread import (
    BidAskQuote,
    bid_ask_spread,
    relative_bid_ask_spread,
)


def test_quote_calculates_spread_and_mid() -> None:
    quote = BidAskQuote(Decimal("99.50"), Decimal("100.50"))
    assert quote.spread == Decimal("1.00")
    assert quote.mid == Decimal("100.00")


def test_relative_spread_is_spread_over_mid() -> None:
    assert relative_bid_ask_spread(Decimal("99"), Decimal("101")) == Decimal("0.02")


def test_absolute_spread_function_matches_quote() -> None:
    assert bid_ask_spread(Decimal("100"), Decimal("100.25")) == Decimal("0.25")


def test_crossed_quote_fails_closed() -> None:
    with pytest.raises(ValueError, match="bid must not exceed ask"):
        BidAskQuote(Decimal("101"), Decimal("100"))


def test_negative_quote_fails_closed() -> None:
    with pytest.raises(ValueError, match="must be non-negative"):
        BidAskQuote(Decimal("-1"), Decimal("1"))


def test_relative_spread_with_zero_mid_fails_closed() -> None:
    with pytest.raises(ValueError, match="mid is zero"):
        relative_bid_ask_spread(Decimal("0"), Decimal("0"))
