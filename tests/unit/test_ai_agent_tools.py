import pytest

from packages.ai_agent.tools import ResearchTool, ToolRegistry


def test_registry_registers_and_invokes_explicit_tool():
    registry = ToolRegistry()
    registry.register(
        ResearchTool(
            name="echo",
            description="Return supplied text.",
            handler=lambda text: text,
        )
    )

    assert registry.names() == ("echo",)
    assert registry.get("echo").description == "Return supplied text."
    assert registry.invoke("echo", text="NIFTY") == "NIFTY"


def test_registry_names_are_sorted_deterministically():
    registry = ToolRegistry(
        (
            ResearchTool("zeta", "z", lambda: 1),
            ResearchTool("alpha", "a", lambda: 2),
        )
    )
    assert registry.names() == ("alpha", "zeta")


def test_registry_rejects_duplicate_names_and_unknown_tools():
    tool = ResearchTool("echo", "Return supplied text.", lambda text: text)
    registry = ToolRegistry((tool,))

    with pytest.raises(ValueError, match="already registered"):
        registry.register(tool)
    with pytest.raises(KeyError, match="unknown research tool"):
        registry.get("missing")


def test_tool_validation_fails_closed():
    with pytest.raises(ValueError, match="name"):
        ResearchTool(" ", "description", lambda: None)
    with pytest.raises(ValueError, match="description"):
        ResearchTool("tool", " ", lambda: None)
    with pytest.raises(TypeError, match="callable"):
        ResearchTool("tool", "description", object())
    with pytest.raises(ValueError, match="name"):
        ToolRegistry().get(" ")
