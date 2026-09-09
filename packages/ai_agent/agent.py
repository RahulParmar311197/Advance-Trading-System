from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ResearchAgent(Protocol):
    """Stable interface for an AI research orchestrator."""

    def research(self, request: "ResearchRequest") -> "ResearchResponse": ...


@dataclass(frozen=True, slots=True)
class ResearchRequest:
    """Explicit research request supplied to an agent implementation."""

    hypothesis: str
    universe: tuple[str, ...]
    timeframe: str

    def __post_init__(self) -> None:
        if not self.hypothesis.strip():
            raise ValueError("hypothesis must not be empty")
        if not self.universe or any(not symbol.strip() for symbol in self.universe):
            raise ValueError("universe must contain non-empty symbols")
        if not self.timeframe.strip():
            raise ValueError("timeframe must not be empty")


@dataclass(frozen=True, slots=True)
class ResearchResponse:
    """Structured result returned by a research agent implementation."""

    summary: str
    proposed_steps: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.summary.strip():
            raise ValueError("summary must not be empty")
        if not self.proposed_steps or any(not step.strip() for step in self.proposed_steps):
            raise ValueError("proposed_steps must contain non-empty steps")


@dataclass(frozen=True, slots=True)
class DeterministicResearchAgent:
    """Deterministic research planner that never executes trades."""

    def research(self, request: ResearchRequest) -> ResearchResponse:
        """Propose a reproducible research workflow from explicit inputs."""
        return ResearchResponse(
            summary=(
                f"Evaluate hypothesis '{request.hypothesis}' on "
                f"{', '.join(request.universe)} at {request.timeframe}."
            ),
            proposed_steps=(
                "Validate the requested market-data universe and timeframe.",
                "Build deterministic features from the supplied data.",
                "Run an out-of-sample backtest with explicit costs and slippage.",
                "Compare results against an appropriate non-ML baseline.",
            ),
        )
