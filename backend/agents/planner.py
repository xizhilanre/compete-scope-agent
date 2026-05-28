"""
Planner Agent -- generates search queries and an analysis plan for the given
target product.  In mock mode it returns hardcoded data (with a 2 s delay);
in real mode it calls the LLM via ``get_llm``.
"""

import asyncio

from backend.api.routes.events import publish
from backend.core.llm import get_llm, safe_parse_json
from backend.core.state import AnalysisState
from backend.schemas.events import AgentStartEvent, AgentCompleteEvent, iso_now

MOCK_SEARCH_QUERIES = [
    "{product} competitor analysis 2026",
    "{product} pricing strategy review",
    "{product} market position SWOT",
]
MOCK_ANALYSIS_PLAN = "从功能、定价、市场定位三个维度进行竞品分析"


async def run_planner(state: AnalysisState, mock: bool = True) -> dict:
    task_id = state["task_id"]
    product = state["target_product"]

    await publish(
        task_id,
        AgentStartEvent(task_id=task_id, agent="planner", timestamp=iso_now()),
    )

    if mock:
        await asyncio.sleep(2)
        queries = [q.format(product=product) for q in MOCK_SEARCH_QUERIES]
        plan = MOCK_ANALYSIS_PLAN
    else:
        llm = get_llm(temperature=0.3)
        prompt = (
            f'你是资深竞品分析规划师。针对产品"{product}"生成搜索计划。\n'
            f'分析维度：{", ".join(state["analysis_dimensions"])}\n'
            f'请生成3-5个英文搜索关键词，每条带2025-2026年份。\n'
            f'严格按JSON格式输出：{{"search_queries": ["query1", "query2"],'
            f' "analysis_plan": "简短分析计划"}}'
        )
        resp = llm.invoke(prompt)
        result = safe_parse_json(resp.content)
        queries = result.get(
            "search_queries",
            [
                f"{product} competitor analysis 2026",
                f"{product} pricing features review",
                f"{product} market position SWOT",
            ],
        )
        plan = result.get("analysis_plan", "从多维度进行竞品分析")

    await publish(
        task_id,
        AgentCompleteEvent(
            task_id=task_id,
            agent="planner",
            timestamp=iso_now(),
            duration_ms=2000,
            output_summary=f"生成了 {len(queries)} 条搜索查询",
        ),
    )

    return {
        "search_queries": queries,
        "analysis_plan": plan,
        "current_agent": "planner",
        "llm_call_count": state["llm_call_count"] + 1,
    }
