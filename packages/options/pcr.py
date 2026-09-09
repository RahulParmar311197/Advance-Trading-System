from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from packages.options.chain import OptionChain
from packages.options.open_interest import open_interest


@dataclass(frozen=True, slots=True)
class PutCallRatio:
    """Open-interest put/call ratio for one supplied option-chain snapshot."""

    put_open_interest: int
    call_open_interest: int

    def __post_init__(self) -> None:
        if self.put_open_interest < 0:
            raise ValueError("put_open_interest must be non-negative")
        if self.call_open_interest <= 0:
            raise ValueError("call_open_interest must be positive for PCR")

    @property
    def value(self) -> Decimal:
        """Return put OI divided by call OI without introducing float rounding."""
        return Decimal(self.put_open_interest) / Decimal(self.call_open_interest)


def open_interest_pcr(chain: OptionChain) -> PutCallRatio:
    """Calculate the OI-based put/call ratio from a supplied chain.

    Every contract must carry an explicit open-interest observation. Missing OI
    is rejected rather than inferred as zero, and a chain with no positive call
    OI cannot produce a meaningful PCR.
    """
    put_oi = sum(open_interest(contract) for contract in chain.puts())
    call_oi = sum(open_interest(contract) for contract in chain.calls())
    return PutCallRatio(put_open_interest=put_oi, call_open_interest=call_oi)
