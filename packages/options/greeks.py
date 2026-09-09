from __future__ import annotations

from dataclasses import dataclass
from math import exp, log, sqrt


@dataclass(frozen=True, slots=True)
class Greeks:
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


def _normal_pdf(x: float) -> float:
    return exp(-0.5 * x * x) / sqrt(2.0 * 3.141592653589793)


def _normal_cdf(x: float) -> float:
    # Abramowitz-Stegun approximation; deterministic and dependency-free.
    sign = 1.0 if x >= 0 else -1.0
    z = abs(x)
    t = 1.0 / (1.0 + 0.2316419 * z)
    poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
    return 0.5 + sign * (0.5 - _normal_pdf(z) * poly)


def black_scholes_greeks(
    spot: float,
    strike: float,
    time_to_expiry: float,
    rate: float,
    volatility: float,
    *,
    right: str,
) -> Greeks:
    """Return European Black-Scholes Greeks using continuous risk-free rate."""
    if spot <= 0 or strike <= 0 or time_to_expiry <= 0 or volatility <= 0:
        raise ValueError("spot, strike, time_to_expiry and volatility must be positive")
    if right not in {"call", "put"}:
        raise ValueError("right must be call or put")

    root_t = sqrt(time_to_expiry)
    d1 = (log(spot / strike) + (rate + 0.5 * volatility * volatility) * time_to_expiry) / (volatility * root_t)
    d2 = d1 - volatility * root_t
    pdf = _normal_pdf(d1)
    discount = exp(-rate * time_to_expiry)
    if right == "call":
        return Greeks(
            delta=_normal_cdf(d1),
            gamma=pdf / (spot * volatility * root_t),
            theta=-(spot * pdf * volatility) / (2 * root_t) - rate * strike * discount * _normal_cdf(d2),
            vega=spot * pdf * root_t,
            rho=strike * time_to_expiry * discount * _normal_cdf(d2),
        )
    return Greeks(
        delta=_normal_cdf(d1) - 1.0,
        gamma=pdf / (spot * volatility * root_t),
        theta=-(spot * pdf * volatility) / (2 * root_t) + rate * strike * discount * _normal_cdf(-d2),
        vega=spot * pdf * root_t,
        rho=-strike * time_to_expiry * discount * _normal_cdf(-d2),
    )
