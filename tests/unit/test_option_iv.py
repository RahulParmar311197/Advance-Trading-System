import pytest

from packages.options.iv import black_scholes_price, implied_volatility


def test_implied_volatility_recovers_known_call_volatility() -> None:
    price = black_scholes_price(100, 100, 1, 0.05, 0.20, right="call")
    result = implied_volatility(price, 100, 100, 1, 0.05, right="call")
    assert result == pytest.approx(0.20, abs=1e-7)


def test_implied_volatility_recovers_known_put_volatility() -> None:
    price = black_scholes_price(100, 110, 0.5, 0.03, 0.35, right="put")
    result = implied_volatility(price, 100, 110, 0.5, 0.03, right="put")
    assert result == pytest.approx(0.35, abs=1e-7)


def test_implied_volatility_rejects_invalid_market_price() -> None:
    with pytest.raises(ValueError):
        implied_volatility(0, 100, 100, 1, 0.05, right="call")
    with pytest.raises(ValueError):
        implied_volatility(101, 100, 100, 1, 0.05, right="call")


def test_black_scholes_price_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        black_scholes_price(100, 100, 1, 0.05, 0, right="call")
    with pytest.raises(ValueError):
        black_scholes_price(100, 100, 1, 0.05, 0.2, right="future")
