from decimal import Decimal

import pytest

from packages.options.payoff import OptionLeg, strategy_payoff


def leg(right: str, position: str, strike: str = "100", premium: str = "5") -> OptionLeg:
    return OptionLeg(
        strike=Decimal(strike),
        premium=Decimal(premium),
        quantity=Decimal("1"),
        right=right,
        position=position,
    )


def test_long_call_expiry_payoff_includes_premium() -> None:
    assert leg("call", "long").payoff(Decimal("110")) == Decimal("5")
    assert leg("call", "long").payoff(Decimal("100")) == Decimal("-5")


def test_short_put_is_inverse_of_long_put() -> None:
    long_pnl = leg("put", "long").payoff(Decimal("90"))
    short_pnl = leg("put", "short").payoff(Decimal("90"))
    assert long_pnl == Decimal("5")
    assert short_pnl == Decimal("-5")


def test_strategy_payoff_sums_supplied_legs() -> None:
    legs = (leg("call", "long"), leg("put", "long"))

    assert strategy_payoff(legs, Decimal("100")) == Decimal("-10")
    assert strategy_payoff(legs, Decimal("120")) == Decimal("10")


def test_payoff_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="legs must not be empty"):
        strategy_payoff((), Decimal("100"))
    with pytest.raises(ValueError, match="underlying_price must be non-negative"):
        leg("call", "long").payoff(Decimal("-1"))
    with pytest.raises(ValueError, match="right must be call or put"):
        OptionLeg(Decimal("100"), Decimal("5"), Decimal("1"), "future", "long")
