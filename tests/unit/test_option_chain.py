from datetime import datetime, timezone
from decimal import Decimal

import pytest

from packages.options.chain import OptionChain, OptionContract


def contract(right: str = "call") -> OptionContract:
    return OptionContract(
        symbol="NIFTY26SEP25000CE",
        expiry=datetime(2026, 9, 24, tzinfo=timezone.utc),
        strike=Decimal("25000"),
        right=right,
        bid=Decimal("100"),
        ask=Decimal("101"),
        last=Decimal("100.5"),
        open_interest=1000,
    )


def test_chain_groups_contracts_and_strikes() -> None:
    call = contract("call")
    put = OptionContract(
        symbol="NIFTY26SEP25000PE",
        expiry=call.expiry,
        strike=call.strike,
        right="put",
    )
    chain = OptionChain.from_contracts("NIFTY", call.expiry, [call, put])

    assert chain.strikes() == (Decimal("25000"),)
    assert chain.calls() == (call,)
    assert chain.puts() == (put,)


def test_option_contract_rejects_invalid_market_fields() -> None:
    with pytest.raises(ValueError, match="right must be call or put"):
        OptionContract("NIFTY", datetime.now(timezone.utc), Decimal("25000"), "future")

    with pytest.raises(ValueError, match="bid must not exceed ask"):
        OptionContract(
            "NIFTY", datetime.now(timezone.utc), Decimal("25000"), "call",
            bid=Decimal("101"), ask=Decimal("100"),
        )
