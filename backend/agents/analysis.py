"""
Analysis Agent -- performs SWOT analysis on the collected research data.

MVP note: real mode is not yet implemented; both mock and real paths return
the same hardcoded SWOT data.  A future iteration will invoke the LLM to
produce a structured analysis from ``raw_research``.
"""

import asyncio

from backend.api.routes.events import publish
from backend.core.state import AnalysisState
from backend.schemas.events import AgentStartEvent, AgentCompleteEvent, iso_now

MOCK_ANALYSIS = {
    "swot": [
        {"category": "strength", "point": "市场占有率领先，品牌认知度高", "confidence": 0.92},
        {"category": "strength", "point": "产品体验和集成生态完善", "confidence": 0.88},
        {"category": "weakness", "point": "高端定价限制了中小团队市场", "confidence": 0.85},
        {"category": "weakness", "point": "离线功能支持不足", "confidence": 0.75},
        {"category": "opportunity", "point": "AI 功能集成带来新增长点", "confidence": 0.90},
        {"category": "opportunity", "point": "企业级市场的数字化转型需求增加", "confidence": 0.82},
        {"category": "threat", "point": "竞品在特定垂直领域快速追赶", "confidence": 0.80},
        {"category": "threat", "point": "开源替代品对价格敏感用户的吸引力", "confidence": 0.72},
    ],
    "competitors": ["Coda", "Confluence", "ClickUp", "Slack", "Microsoft Loop"],
}


async def run_analysis(state: AnalysisState, mock: bool = True) -> dict:
    task_id = state["task_id"]

    await publish(
        task_id,
        AgentStartEvent(task_id=task_id, agent="analysis", timestamp=iso_now()),
    )

    if mock:
        await asyncio.sleep(2)
        result = MOCK_ANALYSIS
    else:
        # MVP 真实模式暂不使用 Analysis（Writer 直接基于 Research 结果写作）
        result = MOCK_ANALYSIS

    await publish(
        task_id,
        AgentCompleteEvent(
            task_id=task_id,
            agent="analysis",
            timestamp=iso_now(),
            duration_ms=2000,
            output_summary=f"生成了 {len(result.get('swot', []))} 条 SWOT 分析项",
        ),
    )

    return {
        "structured_analysis": result,
        "current_agent": "analysis",
        "llm_call_count": state["llm_call_count"] + 1,
    }
