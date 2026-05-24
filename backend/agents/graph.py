import operator
from typing import Annotated
from typing import TypedDict

from langgraph.graph import END
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    product_name: str
    search_plan: list[str]
    research_results: Annotated[list[dict], operator.add]
    swot: list[dict]
    report_markdown: str
    errors: list[str]
    status: str


def build_analysis_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", lambda s: {**s, "status": "planning"})
    graph.add_node("research", lambda s: {**s, "status": "researching"})
    graph.add_node("analysis", lambda s: {**s, "status": "analyzing"})
    graph.add_node("writer", lambda s: {**s, "status": "writing"})
    graph.add_node("reviewer", lambda s: {**s, "status": "reviewing"})

    graph.set_entry_point("planner")
    graph.add_edge("planner", "research")
    graph.add_edge("research", "analysis")
    graph.add_edge("analysis", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_edge("reviewer", END)

    return graph.compile()
