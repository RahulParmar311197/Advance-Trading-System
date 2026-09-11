import pytest

from packages.ai_agent.memory import ExperimentMemory, ExperimentMemoryEntry


def _entry(experiment_id: str, hypothesis: str, outcome: str) -> ExperimentMemoryEntry:
    return ExperimentMemoryEntry(
        experiment_id=experiment_id,
        hypothesis=hypothesis,
        outcome=outcome,
        lessons=("Keep transaction costs explicit.",),
        tags=("nifty", "5m"),
    )


def test_memory_recall_is_deterministic_and_relevant():
    memory = ExperimentMemory(
        (
            _entry("EXP-002", "liquidity sweep improves entries", "positive expectancy"),
            _entry("EXP-001", "momentum improves returns", "negative expectancy"),
        )
    )

    first = memory.recall("liquidity expectancy")
    second = memory.recall("liquidity expectancy")

    assert first == second
    assert first[0].entry.experiment_id == "EXP-002"
    assert first[0].score == 2
    assert memory.entries()[0].experiment_id == "EXP-001"


def test_memory_rejects_duplicate_ids_and_invalid_queries():
    entry = _entry("EXP-001", "momentum improves returns", "negative expectancy")
    memory = ExperimentMemory((entry,))

    with pytest.raises(ValueError, match="already remembered"):
        memory.remember(entry)
    with pytest.raises(ValueError, match="query"):
        memory.recall(" ")
    with pytest.raises(ValueError, match="limit"):
        memory.recall("momentum", limit=0)


def test_memory_entry_validation_is_fail_closed():
    with pytest.raises(ValueError, match="experiment_id"):
        ExperimentMemoryEntry(" ", "hypothesis", "outcome")
    with pytest.raises(ValueError, match="hypothesis"):
        ExperimentMemoryEntry("EXP-1", " ", "outcome")
    with pytest.raises(ValueError, match="outcome"):
        ExperimentMemoryEntry("EXP-1", "hypothesis", " ")
    with pytest.raises(ValueError, match="duplicates"):
        ExperimentMemoryEntry("EXP-1", "hypothesis", "outcome", tags=("nifty", "nifty"))
