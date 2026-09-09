from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class ExperimentManifest:
    experiment_id: str
    data_version: str
    strategy_version: str
    code_version: str
    parameters: dict[str, Any]
    universe: list[str]
    timeframe: str
    start_date: datetime
    end_date: datetime
    transaction_costs: dict[str, Any]
    slippage: dict[str, Any]
    random_seed: int | None = None

    def __post_init__(self) -> None:
        if not self.experiment_id.strip():
            raise ValueError("experiment_id must not be empty")
        if not self.data_version.strip() or not self.strategy_version.strip() or not self.code_version.strip():
            raise ValueError("version fields must not be empty")
        if not self.universe:
            raise ValueError("universe must not be empty")
        if self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")

    def as_record(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "data_version": self.data_version,
            "strategy_version": self.strategy_version,
            "code_version": self.code_version,
            "parameters": self.parameters,
            "universe": self.universe,
            "timeframe": self.timeframe,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "transaction_costs": self.transaction_costs,
            "slippage": self.slippage,
            "random_seed": self.random_seed,
        }
