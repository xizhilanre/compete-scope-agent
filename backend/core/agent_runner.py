import uuid
from backend.agents.graph import AgentState, build_analysis_graph


async def run_analysis(product_name: str) -> str:
    graph = build_analysis_graph()
    job_id = str(uuid.uuid4())

    initial_state: AgentState = {
        "product_name": product_name,
        "search_plan": [],
        "research_results": [],
        "swot": [],
        "report_markdown": "",
        "errors": [],
        "status": "queued",
    }

    final_state = await graph.ainvoke(initial_state)
    return final_state["report_markdown"]
