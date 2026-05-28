"""
Writer Agent -- composes the final competitive-analysis report in Markdown.

In mock mode a hardcoded template (formatted with the product name) is
returned.  In real mode the LLM is invoked with the research results as
context.
"""

import asyncio

from backend.api.routes.events import publish
from backend.core.llm import get_llm
from backend.core.state import AnalysisState
from backend.schemas.events import AgentStartEvent, AgentCompleteEvent, iso_now

MOCK_REPORT = """# {product} 竞品分析报告

## 执行摘要

{product} 在其细分市场中处于领先地位，凭借出色的产品体验和强大的集成生态建立了坚实的竞争壁垒。然而，在定价策略和特定垂直领域面临来自新兴竞品的挑战。

## 竞品全景

主要竞争对手包括 Coda、Confluence、ClickUp 等，各有差异化优势。

## SWOT 分析

| 维度 | 分析 |
|------|------|
| **优势 (S)** | 品牌认知度高、集成生态完善、用户体验优秀 |
| **劣势 (W)** | 高端定价受限、离线功能不足 |
| **机会 (O)** | AI 集成新增长、企业数字化转型需求 |
| **威胁 (T)** | 垂直领域竞争者追赶、开源替代品崛起 |

## 战略建议

1. 加速 AI 功能集成，建立技术护城河
2. 考虑推出中小团队定价方案，扩大用户基数
3. 增强离线功能，满足企业安全合规需求

## 信息来源

- 综合行业分析数据
- 公开定价页面
- 竞品对比评测
"""


async def run_writer(state: AnalysisState, mock: bool = True) -> dict:
    task_id = state["task_id"]
    product = state["target_product"]

    await publish(
        task_id,
        AgentStartEvent(task_id=task_id, agent="writer", timestamp=iso_now()),
    )

    if mock:
        await asyncio.sleep(2)
        markdown = MOCK_REPORT.format(product=product)
    else:
        llm = get_llm(temperature=0.4)
        research_items = state.get("raw_research", [])
        research_text = "\n".join(
            f"- [{r['title']}]({r['url']}): {r.get('content', '')[:200]}"
            for r in research_items[:8]
        )
        prompt = (
            "你是专业商业分析师。根据搜索结果撰写一份竞品分析报告。\n\n"
            f"产品：{product}\n"
            f"分析维度：{', '.join(state['analysis_dimensions'])}\n\n"
            f"搜索结果参考：\n{research_text}\n\n"
            "请使用中文 Markdown 格式输出，包含以下段落：\n"
            "1. # 竞品分析报告：(产品名)\n"
            "2. ## 执行摘要（3-5句话概述核心发现）\n"
            "3. ## 竞品全景（列出主要竞品及其差异化优势）\n"
            "4. ## SWOT 分析（四栏表格或列表）\n"
            "5. ## 战略建议（3条核心行动建议）\n"
            "6. ## 信息来源（列出参考 URL）\n\n"
            "注意：基于搜索结果写作，避免凭空编造。如果搜索结果不足，基于你对产品的了解补充，但注明是'基于公开信息推断'。"
        )
        resp = llm.invoke(prompt)
        markdown = resp.content

    await publish(
        task_id,
        AgentCompleteEvent(
            task_id=task_id,
            agent="writer",
            timestamp=iso_now(),
            duration_ms=2000,
            output_summary=f"生成了 {len(markdown)} 字符的报告",
        ),
    )

    return {
        "final_report_markdown": markdown,
        "current_agent": "writer",
        "llm_call_count": state["llm_call_count"] + 1,
    }
