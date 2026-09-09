from datetime import datetime, timezone
from decimal import Decimal

import pytest

from packages.options.chain import OptionChain, OptionContract
from packages.options.pcr import PutCallRatio, open_interest_pcr


AS_OF = datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc)
EXPIRY = datetime(2026, 9, 24, tzinfo=timezone.utc)


def contract(symbol: str, right: str, oi: int | None) -> OptionContract:
    return OptionContract(
        symbol=symbol,
        expiry=EXPIRY,
        strike=Decimal("25000"),
        right=right,
        open_interest=oi,
    )


def test_open_interest_pcr_uses_supplied_call_and_put_oi() -> None:
    chain = OptionChain.from_contracts(
        "NIFTY",
        AS_OF,
        [
            contract("NIFTY26SEP25000CE", "call", 100),
            contract("NIFTY26SEP25100CE", "call", 300),
            contract("NIFTY26SEP25000PE", "put", 200),
            contract("NIFTY26SEP25100PE", "put", 400),
        ],
    )

    result = open_interest_pcr(chain)

    assert result == PutCallRatio(put_open_interest=600, call_open_interest=400)
    assert result.value == Decimal("1.5")


def test_open_interest_pcr_is_deterministic() -> None:
    chain = OptionChain.from_contracts(
        "NIFTY",
        AS_OF,
        [contract("P", "put", 25), contract("C", "call", 50)],
    )

    assert open_interest_pcr(chain).value == open_interest_pcr(chain).value


def test_missing_oi_fails_closed() -> None:
    chain = OptionChain.from_contracts(
        "NIFTY",
        AS_OF,
        [contract("C", "call", 100), contract("P", "put", None)],
    )

    with pytest.raises(ValueError, match="open_interest is missing"):
        open_interest_pcr(chain)


def test_zero_call_oi_fails_closed() -> None:
    chain = OptionChain.from_contracts(
        "NIFTY",
        AS_OF,
        [contract("C", "call", 0), contract("P", "put", 100)],
    )

    with pytest.raises(ValueError, match="call_open_interest must be positive"):
        open_interest_pcr(chain)
