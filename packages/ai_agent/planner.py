from __future__ import annotations

from dataclasses import dataclass

from packages.ai_agent.agent import ResearchRequest


@dataclass(frozen=True, slots=True)
class ResearchPlan:
    """Validated, deterministic sequence of research actions."""

    request: ResearchRequest
    steps: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.steps or any(not step.strip() for step in self.steps):
            raise ValueError("steps must contain non-empty actions")


class ResearchPlanner:
    """Create a reproducible research plan without executing research tools."""

    def plan(self, request: ResearchRequest) -> ResearchPlan:
        return ResearchPlan(
            request=request,
            steps=(
                "validate_data_scope",
                "build_features",
                "run_backtest",
                "evaluate_out_of_sample",
                "compare_results",
                "generate_report",
            ),
        )
