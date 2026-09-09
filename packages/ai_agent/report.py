from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from packages.ai_agent.strategy_comparison import StrategyComparisonResult


@dataclass(frozen=True, slots=True)
class ResearchAgentReport:
    """Factual Markdown report derived only from computed comparison results."""

    title: str
    findings: tuple[str, ...]
    limitations: tuple[str, ...]

    def as_markdown(self) -> str:
        lines = [f"# {self.title}", "", "## Findings"]
        lines.extend(f"- {finding}" for finding in self.findings)
        lines.extend(["", "## Limitations"])
        lines.extend(f"- {limitation}" for limitation in self.limitations)
        return "\n".join(lines) + "\n"


def generate_report(
    comparison: StrategyComparisonResult, *, title: str = "Strategy Comparison Report"
) -> ResearchAgentReport:
    """Generate a report without running new research or inventing conclusions."""
    if not comparison.rows:
        raise ValueError("comparison must contain at least one strategy result")
    top = comparison.rows[0]
    findings = (
        f"Top-ranked strategy: {top.strategy_name}.",
        f"Top-ranked total return: {Decimal(top.result.metrics['total_return'])}.",
        f"Top-ranked maximum drawdown: {Decimal(top.result.metrics['max_drawdown'])}.",
        f"Compared {len(comparison.rows)} strategy result(s).",
    )
    limitations = (
        "The report summarizes supplied backtest results and does not create new market data or trades.",
        "Ranking is deterministic and is not a claim of future performance.",
        "No causal, statistical-significance, or live-trading conclusion is inferred.",
    )
    return ResearchAgentReport(title, findings, limitations)
