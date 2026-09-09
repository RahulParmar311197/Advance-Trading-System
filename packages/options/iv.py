from __future__ import annotations

from math import exp, log, sqrt

from packages.options.greeks import _normal_cdf


def black_scholes_price(
    spot: float,
    strike: float,
    time_to_expiry: float,
    rate: float,
    volatility: float,
    *,
    right: str,
) -> float:
    """Return a European Black-Scholes option price with continuous rate."""
    _validate_inputs(spot, strike, time_to_expiry, volatility, right)
    root_t = sqrt(time_to_expiry)
    d1 = (log(spot / strike) + (rate + 0.5 * volatility * volatility) * time_to_expiry) / (volatility * root_t)
    d2 = d1 - volatility * root_t
    discount = exp(-rate * time_to_expiry)
    if right == "call":
        return spot * _normal_cdf(d1) - strike * discount * _normal_cdf(d2)
    return strike * discount * _normal_cdf(-d2) - spot * _normal_cdf(-d1)


def implied_volatility(
    option_price: float,
    spot: float,
    strike: float,
    time_to_expiry: float,
    rate: float,
    *,
    right: str,
    tolerance: float = 1e-8,
    max_iterations: int = 100,
) -> float:
    """Solve Black-Scholes implied volatility by deterministic bisection.

    The supplied option price is treated as an observed input; this function
    does not source or fabricate market quotes. Raises ValueError when the
    price is outside the European no-arbitrage bounds or no volatility bracket
    can reproduce it.
    """
    _validate_inputs(spot, strike, time_to_expiry, 1.0, right)
    if option_price <= 0:
        raise ValueError("option_price must be positive")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    discount = exp(-rate * time_to_expiry)
    if right == "call":
        lower_bound = max(0.0, spot - strike * discount)
        upper_bound = spot
    else:
        lower_bound = max(0.0, strike * discount - spot)
        upper_bound = strike * discount
    if option_price < lower_bound or option_price >= upper_bound:
        raise ValueError("option_price is outside the strict European no-arbitrage bounds")

    low = 1e-10
    high = 1.0
    while black_scholes_price(spot, strike, time_to_expiry, rate, high, right=right) < option_price:
        high *= 2.0
        if high > 64.0:
            raise ValueError("option_price cannot be bracketed by a finite volatility")

    for _ in range(max_iterations):
        mid = (low + high) / 2.0
        model_price = black_scholes_price(spot, strike, time_to_expiry, rate, mid, right=right)
        if abs(model_price - option_price) <= tolerance:
            return mid
        if model_price < option_price:
            low = mid
        else:
            high = mid

    return (low + high) / 2.0


def _validate_inputs(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    right: str,
) -> None:
    if spot <= 0 or strike <= 0 or time_to_expiry <= 0 or volatility <= 0:
        raise ValueError("spot, strike, time_to_expiry and volatility must be positive")
    if right not in {"call", "put"}:
        raise ValueError("right must be call or put")
