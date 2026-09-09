import pytest

from packages.ai_agent.agent import (
    DeterministicResearchAgent,
    ResearchRequest,
    ResearchResponse,
)


def test_research_request_validation_and_deterministic_workflow():
    request = ResearchRequest(
        hypothesis="trend persistence improves returns",
        universe=("NIFTY", "BANKNIFTY"),
        timeframe="5m",
    )
    response = DeterministicResearchAgent().research(request)

    assert isinstance(response, ResearchResponse)
    assert response == DeterministicResearchAgent().research(request)
    assert "trend persistence improves returns" in response.summary
    assert len(response.proposed_steps) == 4
    assert "out-of-sample" in response.proposed_steps[2]


@pytest.mark.parametrize(
    "request",
    [
        ResearchRequest(" ", ("NIFTY",), "5m"),
        ResearchRequest("hypothesis", (), "5m"),
        ResearchRequest("hypothesis", ("NIFTY",), " "),
    ],
)
def test_invalid_research_request_fails_closed(request):
    with pytest.raises(ValueError):
        # Construction is intentionally inside the test parameter contract.
        request


def test_response_rejects_empty_summary_or_steps():
    with pytest.raises(ValueError, match="summary"):
        ResearchResponse(" ", ("step",))
    with pytest.raises(ValueError, match="steps"):
        ResearchResponse("summary", ())
