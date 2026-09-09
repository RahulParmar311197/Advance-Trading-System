from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from packages.options.chain import OptionContract


@dataclass(frozen=True, slots=True)
class OpenInterestChange:
    """Open-interest observation for one option contract between two snapshots."""

    symbol: str
    previous: int
    current: int

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")
        if self.previous < 0 or self.current < 0:
            raise ValueError("open interest must be non-negative")

    @property
    def change(self) -> int:
        return self.current - self.previous

    @property
    def change_pct(self) -> float | None:
        if self.previous == 0:
            return None
        return self.change / self.previous


def open_interest(contract: OptionContract) -> int:
    """Return the supplied contract's open interest, rejecting missing observations."""
    if contract.open_interest is None:
        raise ValueError(f"open_interest is missing for {contract.symbol}")
    return contract.open_interest


def calculate_oi_changes(
    previous: Iterable[OptionContract],
    current: Iterable[OptionContract],
) -> tuple[OpenInterestChange, ...]:
    """Calculate OI changes for symbols present in both supplied snapshots.

    Missing contracts are excluded rather than inferred. Duplicate symbols or
    conflicting OI observations fail closed.
    """
    previous_map = _index(previous)
    current_map = _index(current)
    changes: list[OpenInterestChange] = []
    for symbol in sorted(previous_map.keys() & current_map.keys()):
        changes.append(
            OpenInterestChange(
                symbol=symbol,
                previous=previous_map[symbol],
                current=current_map[symbol],
            )
        )
    return tuple(changes)


def _index(contracts: Iterable[OptionContract]) -> dict[str, int]:
    indexed: dict[str, int] = {}
    for contract in contracts:
        oi = open_interest(contract)
        if contract.symbol in indexed:
            raise ValueError(f"duplicate option symbol: {contract.symbol}")
        indexed[contract.symbol] = oi
    return indexed
