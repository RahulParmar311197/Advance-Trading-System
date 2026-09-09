from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class ResearchReport:
    title: str
    methodology: str
    findings: tuple[str, ...]
    limitations: tuple[str, ...]

    def as_markdown(self) -> str:
        lines = [f"# {self.title}", "", "## Methodology", self.methodology, "", "## Findings"]
        lines.extend(f"- {finding}" for finding in self.findings)
        lines.extend(["", "## Limitations"])
        lines.extend(f"- {limitation}" for limitation in self.limitations)
        return "\n".join(lines) + "\n"


def generate_report(comparisons: Iterable[Any], *, title: str = "Research Comparison Report") -> ResearchReport:
    """Generate a factual Markdown report from already-computed comparison results."""
    rows = list(comparisons)
    if not rows:
        raise ValueError("comparisons must not be empty")
    best = rows[0]
    return ResearchReport(
        title=title,
        methodology="Experiments are compared using their persisted metrics. Results are presented in the deterministic comparison order.",
        findings=(
            f"Top-ranked experiment: {best.experiment_id} ({best.strategy_version}).",
            f"Top-ranked total return: {Decimal(best.total_return)}.",
            f"Top-ranked maximum drawdown: {Decimal(best.max_drawdown)}.",
            f"Compared {len(rows)} experiment result(s).",
        ),
        limitations=(
            "The report summarizes supplied experiment results; it does not create new backtests.",
            "Ranking is inherited from the comparison function and is not a claim of future performance.",
            "No causal or statistical significance claim is inferred from the reported metrics.",
        ),
    )
