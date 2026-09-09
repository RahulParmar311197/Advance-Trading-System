from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


ToolCallable = Callable[..., Any]


@dataclass(frozen=True, slots=True)
class ResearchTool:
    """Named callable exposed to the research agent."""

    name: str
    description: str
    handler: ToolCallable

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if not callable(self.handler):
            raise TypeError("handler must be callable")


class ToolRegistry:
    """Deterministic registry for explicitly supplied research tools."""

    def __init__(self, tools: tuple[ResearchTool, ...] = ()) -> None:
        self._tools: dict[str, ResearchTool] = {}
        for tool in tools:
            self.register(tool)

    def register(self, tool: ResearchTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ResearchTool:
        if not name.strip():
            raise ValueError("name must not be empty")
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"unknown research tool: {name}") from exc

    def names(self) -> tuple[str, ...]:
        """Return registered names in deterministic lexical order."""
        return tuple(sorted(self._tools))

    def invoke(self, name: str, **kwargs: Any) -> Any:
        """Invoke only a registered callable; no implicit tools are created."""
        return self.get(name).handler(**kwargs)
