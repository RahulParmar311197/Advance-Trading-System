from decimal import Decimal

import pytest

from research.experiments.comparison import compare_results


def test_compare_results_ranks_return_then_drawdown():
    results = compare_results([
        {"experiment_id": "EXP-B", "strategy_version": "B:v1", "metrics": {"total_return": "0.10", "max_drawdown": "0.20", "trade_count": 4, "win_rate": "0.5", "profit_factor": "1.2"}},
        {"experiment_id": "EXP-A", "strategy_version": "A:v1", "metrics": {"total_return": Decimal("0.10"), "max_drawdown": Decimal("0.05"), "trade_count": 6, "win_rate": "0.6", "profit_factor": "1.5"}},
    ])
    assert [item.experiment_id for item in results] == ["EXP-A", "EXP-B"]


def test_compare_results_requires_identity():
    with pytest.raises(ValueError, match="experiment_id"):
        compare_results([{"metrics": {"total_return": "0.1"}}])
