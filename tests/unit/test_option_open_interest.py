from datetime import datetime, timezone
from decimal import Decimal

import pytest

from packages.options.chain import OptionContract
from packages.options.open_interest import calculate_oi_changes, open_interest


def contract(symbol: str, oi: int | None) -> OptionContract:
    return OptionContract(
        symbol=symbol,
        expiry=datetime(2026, 9, 24, tzinfo=timezone.utc),
        strike=Decimal("25000"),
        right="call",
        open_interest=oi,
    )


def test_open_interest_change_is_deterministic() -> None:
    changes = calculate_oi_changes(
        [contract("NIFTY26SEP25000CE", 100), contract("NIFTY26SEP25100CE", 0)],
        [contract("NIFTY26SEP25000CE", 125), contract("NIFTY26SEP25100CE", 40)],
    )

    assert [(item.symbol, item.change, item.change_pct) for item in changes] == [
        ("NIFTY26SEP25000CE", 25, 0.25),
        ("NIFTY26SEP25100CE", 40, None),
    ]


def test_missing_symbols_are_not_inferred() -> None:
    changes = calculate_oi_changes(
        [contract("NIFTY26SEP25000CE", 100)],
        [contract("NIFTY26SEP25100CE", 125)],
    )
    assert changes == ()


def test_missing_oi_fails_closed() -> None:
    with pytest.raises(ValueError, match="open_interest is missing"):
        open_interest(contract("NIFTY26SEP25000CE", None))


def test_duplicate_symbols_fail_closed() -> None:
    with pytest.raises(ValueError, match="duplicate option symbol"):
        calculate_oi_changes(
            [contract("NIFTY26SEP25000CE", 100), contract("NIFTY26SEP25000CE", 110)],
            [contract("NIFTY26SEP25000CE", 120)],
        )
