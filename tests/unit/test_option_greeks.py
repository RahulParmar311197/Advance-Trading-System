import pytest

from packages.options.greeks import black_scholes_greeks


def test_call_and_put_delta_have_expected_parity() -> None:
    call = black_scholes_greeks(100, 100, 1, 0.05, 0.2, right="call")
    put = black_scholes_greeks(100, 100, 1, 0.05, 0.2, right="put")
    assert call.gamma == pytest.approx(put.gamma)
    assert call.vega == pytest.approx(put.vega)
    assert call.delta - put.delta == pytest.approx(1.0)


def test_invalid_greek_inputs_fail_closed() -> None:
    with pytest.raises(ValueError):
        black_scholes_greeks(100, 100, 1, 0.05, 0, right="call")
    with pytest.raises(ValueError):
        black_scholes_greeks(100, 100, 1, 0.05, 0.2, right="future")
