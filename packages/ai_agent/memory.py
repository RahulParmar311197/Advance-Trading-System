from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import re


@dataclass(frozen=True, slots=True)
class ExperimentMemoryEntry:
    """A factual, human-supplied research lesson linked to one experiment."""

    experiment_id: str
    hypothesis: str
    outcome: str
    lessons: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.experiment_id.strip():
            raise ValueError("experiment_id must not be empty")
        if not self.hypothesis.strip():
            raise ValueError("hypothesis must not be empty")
        if not self.outcome.strip():
            raise ValueError("outcome must not be empty")
        if any(not lesson.strip() for lesson in self.lessons):
            raise ValueError("lessons must contain non-empty text")
        if any(not tag.strip() for tag in self.tags):
            raise ValueError("tags must contain non-empty text")
        if len(set(self.tags)) != len(self.tags):
            raise ValueError("tags must not contain duplicates")

    def as_record(self) -> dict[str, object]:
        return {
            "experiment_id": self.experiment_id,
            "hypothesis": self.hypothesis,
            "outcome": self.outcome,
            "lessons": list(self.lessons),
            "tags": list(self.tags),
        }


@dataclass(frozen=True, slots=True)
class MemoryMatch:
    """A deterministic relevance result for a recalled experiment."""

    entry: ExperimentMemoryEntry
    score: int


class ExperimentMemory:
    """Append-only deterministic memory for explicitly recorded experiments."""

    def __init__(self, entries: Iterable[ExperimentMemoryEntry] = ()) -> None:
        self._entries: dict[str, ExperimentMemoryEntry] = {}
        for entry in entries:
            self.remember(entry)

    def remember(self, entry: ExperimentMemoryEntry) -> None:
        """Store one factual experiment lesson; duplicate IDs fail closed."""
        if entry.experiment_id in self._entries:
            raise ValueError(f"experiment already remembered: {entry.experiment_id}")
        self._entries[entry.experiment_id] = entry

    def get(self, experiment_id: str) -> ExperimentMemoryEntry:
        if not experiment_id.strip():
            raise ValueError("experiment_id must not be empty")
        try:
            return self._entries[experiment_id]
        except KeyError as exc:
            raise KeyError(f"unknown experiment: {experiment_id}") from exc

    def entries(self) -> tuple[ExperimentMemoryEntry, ...]:
        """Return remembered experiments in stable experiment-ID order."""
        return tuple(self._entries[key] for key in sorted(self._entries))

    def recall(self, query: str, *, limit: int = 5) -> tuple[MemoryMatch, ...]:
        """Rank memories by exact token overlap, with deterministic tie-breaking."""
        if not query.strip():
            raise ValueError("query must not be empty")
        if limit < 1:
            raise ValueError("limit must be >= 1")
        query_tokens = _tokens(query)
        matches = []
        for entry in self._entries.values():
            searchable = " ".join((entry.hypothesis, entry.outcome, *entry.lessons, *entry.tags))
            score = len(query_tokens & _tokens(searchable))
            if score:
                matches.append(MemoryMatch(entry, score))
        matches.sort(key=lambda match: (-match.score, match.entry.experiment_id))
        return tuple(matches[:limit])


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 1}
