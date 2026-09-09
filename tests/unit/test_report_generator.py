from decimal import Decimal

import pytest

from research.experiments.comparison import StrategyComparison
from research.reports.generator import generate_report


def test_generate_report_is_markdown_and_factual():
    report = generate_report([StrategyComparison("EXP-A", "A:v1", 10, Decimal("0.12"), Decimal("0.08"), Decimal("0.6"), Decimal("1.5"))])
    markdown = report.as_markdown()
    assert "# Research Comparison Report" in markdown
    assert "EXP-A" in markdown
    assert "0.12" in markdown
    assert "does not create new backtests" in markdown


def test_generate_report_rejects_empty_results():
    with pytest.raises(ValueError, match="comparisons"):
        generate_report([])
