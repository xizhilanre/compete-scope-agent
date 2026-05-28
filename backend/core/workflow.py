"""
LangGraph DAG that wires the 5 agent nodes into a competitive-analysis pipeline.

Two modes:
  - mock (default): runs all 5 agents with hardcoded data (planner -> research ->
    analysis -> writer -> reviewer).
  - real: runs 3 agents that call the LLM (planner -> research -> writer);
    analysis and reviewer are skipped in the MVP.
"""

import collections.abc as cabc

from langgraph.graph import END
from langgraph.graph import StateGraph

from backend.agents.analysis import run_analysis
from backend.agents.planner import run_planner
from backend.agents.research import run_research
from backend.agents.reviewer import run_reviewer
from backend.agents.writer import run_writer
from backend.core.state import AnalysisState

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_A = AnalysisState


def _node(fn: cabc.Callable[[_A], cabc.Awaitable[dict]], mock: bool):
    """Return an async wrapper so LangGraph can ``await`` the agent node.

    ``lambda s: run_planner(s, mock=True)`` returns a *coroutine object*,
    which LangGraph does not automatically await.  This factory returns a
    proper ``async def`` that LangGraph's ``ainvoke()`` recognises.
    """

    async def wrapper(state: _A) -> dict:
        return await fn(state, mock=mock)  # type: ignore[call-arg]

    return wrapper


def _add_agents(
    workflow: StateGraph,
    agents: list[tuple[str, cabc.Callable[[_A], cabc.Awaitable[dict]]]],
    mock: bool,
) -> None:
    """Register a sequence of agent nodes and wire them linearly.

    The first entry becomes the entry point; each subsequent entry is
    chained after the previous one.
    """
    name0, fn0 = agents[0]
    workflow.add_node(name0, _node(fn0, mock))
    workflow.set_entry_point(name0)

    prev = name0
    for name, fn in agents[1:]:
        workflow.add_node(name, _node(fn, mock))
        workflow.add_edge(prev, name)
        prev = name

    workflow.add_edge(prev, END)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_dag(mock: bool = True) -> StateGraph:
    """Build and compile a LangGraph state graph.

    Args:
        mock: When ``True`` all agent nodes return hardcoded data; when
            ``False`` the real LLM-backed nodes are used.

    Returns:
        A compiled ``StateGraph`` that can be invoked via ``ainvoke()``.
    """
    workflow = StateGraph(AnalysisState)

    if mock:
        _add_agents(workflow, [
            ("planner", run_planner),
            ("research", run_research),
            ("analysis", run_analysis),
            ("writer", run_writer),
            ("reviewer", run_reviewer),
        ], mock=True)
    else:
        _add_agents(workflow, [
            ("planner", run_planner),
            ("research", run_research),
            ("writer", run_writer),
        ], mock=False)

    return workflow.compile()  # type: ignore[return-value]
