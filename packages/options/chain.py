from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True, slots=True)
class OptionContract:
    """Normalized option quote for a single expiry/strike/right."""

    symbol: str
    expiry: datetime
    strike: Decimal
    right: str
    bid: Decimal | None = None
    ask: Decimal | None = None
    last: Decimal | None = None
    open_interest: int | None = None

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")
        if self.strike <= 0:
            raise ValueError("strike must be positive")
        if self.right not in {"call", "put"}:
            raise ValueError("right must be call or put")
        for name, value in (("bid", self.bid), ("ask", self.ask), ("last", self.last)):
            if value is not None and value < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.bid is not None and self.ask is not None and self.bid > self.ask:
            raise ValueError("bid must not exceed ask")
        if self.open_interest is not None and self.open_interest < 0:
            raise ValueError("open_interest must be non-negative")


@dataclass(frozen=True, slots=True)
class OptionChain:
    """Immutable collection of normalized option contracts for one underlying snapshot."""

    underlying: str
    as_of: datetime
    contracts: tuple[OptionContract, ...]

    @classmethod
    def from_contracts(
        cls, underlying: str, as_of: datetime, contracts: Iterable[OptionContract]
    ) -> "OptionChain":
        if not underlying.strip():
            raise ValueError("underlying must not be empty")
        values = tuple(contracts)
        if not values:
            raise ValueError("contracts must not be empty")
        return cls(underlying=underlying, as_of=as_of, contracts=values)

    def strikes(self) -> tuple[Decimal, ...]:
        return tuple(sorted({contract.strike for contract in self.contracts}))

    def calls(self) -> tuple[OptionContract, ...]:
        return tuple(contract for contract in self.contracts if contract.right == "call")

    def puts(self) -> tuple[OptionContract, ...]:
        return tuple(contract for contract in self.contracts if contract.right == "put")
