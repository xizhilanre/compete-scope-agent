import uuid

from backend.agents.graph import AgentState
from backend.agents.graph import build_analysis_graph


async def run_analysis(product_name: str) -> str:
    graph = build_analysis_graph()
    str(uuid.uuid4())

    initial_state: AgentState = {
        "product_name": product_name,
        "search_plan": [],
        "research_results": [],
        "swot": [],
        "report_markdown": "",
        "errors": [],
        "status": "queued",
    }

    compiled = graph.compile()
    final_state = await compiled.ainvoke(initial_state)
    return str(final_state["report_markdown"])
