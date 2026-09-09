import pytest

from packages.ai_agent.agent import ResearchRequest
from packages.ai_agent.planner import ResearchPlan, ResearchPlanner


def request() -> ResearchRequest:
    return ResearchRequest(
        hypothesis="trend persistence improves returns",
        universe=("NIFTY", "BANKNIFTY"),
        timeframe="5m",
    )


def test_planner_returns_deterministic_research_plan():
    planner = ResearchPlanner()
    first = planner.plan(request())
    second = planner.plan(request())

    assert isinstance(first, ResearchPlan)
    assert first == second
    assert first.request == request()
    assert first.steps == (
        "validate_data_scope",
        "build_features",
        "run_backtest",
        "evaluate_out_of_sample",
        "compare_results",
        "generate_report",
    )


def test_research_plan_rejects_empty_steps():
    with pytest.raises(ValueError, match="steps"):
        ResearchPlan(request(), ())


def test_research_plan_rejects_blank_step():
    with pytest.raises(ValueError, match="steps"):
        ResearchPlan(request(), ("validate_data_scope", " "))
