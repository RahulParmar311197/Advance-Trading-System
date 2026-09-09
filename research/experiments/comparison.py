from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class StrategyComparison:
    experiment_id: str
    strategy_version: str
    trade_count: int
    total_return: Decimal
    max_drawdown: Decimal
    win_rate: Decimal
    profit_factor: Decimal | None


def compare_results(results: Iterable[dict[str, Any]]) -> list[StrategyComparison]:
    """Normalize reproducible experiment results into a deterministic ranking."""
    comparisons: list[StrategyComparison] = []
    for result in results:
        metrics = result.get("metrics") or {}
        experiment_id = str(result.get("experiment_id", "")).strip()
        strategy_version = str(result.get("strategy_version", "")).strip()
        if not experiment_id or not strategy_version:
            raise ValueError("experiment_id and strategy_version are required")
        comparisons.append(StrategyComparison(
            experiment_id=experiment_id,
            strategy_version=strategy_version,
            trade_count=int(metrics.get("trade_count", 0)),
            total_return=Decimal(str(metrics.get("total_return", "0"))),
            max_drawdown=Decimal(str(metrics.get("max_drawdown", "0"))),
            win_rate=Decimal(str(metrics.get("win_rate", "0"))),
            profit_factor=None if metrics.get("profit_factor") is None else Decimal(str(metrics["profit_factor"])),
        ))
    return sorted(comparisons, key=lambda item: (item.total_return, -item.max_drawdown), reverse=True)
