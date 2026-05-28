# CompeteScope MVP 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 输入产品名 → 5 Agent 线性 DAG → SSE 实时进度 → Markdown 竞品报告，模拟模式先跑通全栈架构，然后接真实 LLM。

**Architecture:** 后端用 FastAPI + LangGraph StateGraph，前端用 Next.js 15 App Router。通过环境变量 `COMPETESCOPE_MOCK` 切换模拟/真实模式。模拟模式 5 节点全上但 sleep + 假数据，真实模式 3 节点（Planner→Research→Writer）接 DeepSeek + Tavily。

**Tech Stack:** Python 3.12+ / FastAPI / LangGraph / SQLAlchemy 2.0 async / DeepSeek API / Tavily Search / Next.js 15 / Tailwind CSS / react-markdown

**Day Plan:** Day 1（Task 1-11）后端全部 | Day 2（Task 12-16）前端全部 | Day 3（Task 17-22）真实 LLM 替换

---

### Task 1: AnalysisState 数据总线

**Files:**
- Create: `backend/core/state.py`

- [ ] **Step 1: 创建 AnalysisState TypedDict**

`backend/core/state.py` 完整内容：

```python
from typing import Annotated, Optional, TypedDict
import operator


class AnalysisState(TypedDict):
    # ---- 输入 ----
    task_id: str
    target_product: str
    analysis_dimensions: list[str]

    # ---- Planner 输出 ----
    search_queries: list[str]
    analysis_plan: str

    # ---- Research 输出 ----
    raw_research: list[dict]

    # ---- Analysis 输出 ----
    structured_analysis: Optional[dict]

    # ---- Writer 输出 ----
    final_report_markdown: str
    metric_cards: Optional[dict]

    # ---- Reviewer 输出 ----
    quality_score: float
    quality_feedback: str

    # ---- Runtime 跟踪 ----
    current_agent: str
    execution_logs: Annotated[list[dict], operator.add]
    token_usage: dict
    llm_call_count: int
    status: str
    error: Optional[str]
```

- [ ] **Step 2: 验证 import 无报错**

```bash
cd /d/MYdesktop/CompeteScopeAgent && PYTHONPATH=. python -c "from backend.core.state import AnalysisState; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add backend/core/state.py
git commit -m "feat(core): add AnalysisState TypedDict with 17 fields"
```

---

### Task 2: LLM 调用封装

**Files:**
- Create: `backend/core/llm.py`

- [ ] **Step 1: 确认 .env 中有 DeepSeek 配置**

检查 `.env` 中以下字段存在且非占位：
```
OPENAI_API_KEY=sk-your-deepseek-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```

- [ ] **Step 2: 创建 llm.py**

```python
import json
import re

from langchain_openai import ChatOpenAI

from backend.config import settings


def get_llm(temperature: float = 0.3, max_tokens: int = 3000) -> ChatOpenAI:
    kwargs = {
        "model": settings.OPENAI_MODEL,
        "api_key": settings.OPENAI_API_KEY,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout": 90,
    }
    if settings.OPENAI_BASE_URL:
        kwargs["base_url"] = settings.OPENAI_BASE_URL
    return ChatOpenAI(**kwargs)


def safe_parse_json(raw: str) -> dict:
    # 直接解析
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # 提取 ```json ... ``` 内内容
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # 提取第一个 { 到最后一个 }
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and start < end:
        try:
            return json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            pass
    return {}
```

- [ ] **Step 3: 验证 import**

```bash
PYTHONPATH=. python -c "from backend.core.llm import get_llm, safe_parse_json; print('OK')"
```
Expected: `OK`

- [ ] **Step 4: 快速验证 LLM 连接（可选，需真实 Key）**

```bash
PYTHONPATH=. python -c "
from backend.core.llm import get_llm
llm = get_llm()
resp = llm.invoke('Say hello in 3 words')
print(resp.content)
"
```
Expected: 3 个英文单词

- [ ] **Step 5: 提交**

```bash
git add backend/core/llm.py
git commit -m "feat(core): add get_llm() and safe_parse_json() utilities"
```

---

### Task 3: Tavily 搜索封装

**Files:**
- Create: `backend/tools/tavily_search.py`

- [ ] **Step 1: 创建 tavily_search.py**

```python
import httpx

from backend.config import settings


def tavily_search_sync(query: str, max_results: int = 5) -> list[dict]:
    resp = httpx.post(
        "https://api.tavily.com/search",
        json={
            "api_key": settings.TAVILY_API_KEY,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": (r.get("content", "") or "")[:300],
            "relevance_score": float(r.get("score", 0.0)),
        }
        for r in data.get("results", [])
    ]
```

- [ ] **Step 2: 验证 import**

```bash
PYTHONPATH=. python -c "from backend.tools.tavily_search import tavily_search_sync; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: 快速验证 Tavily 连接（需真实 Key）**

```bash
PYTHONPATH=. python -c "
from backend.tools.tavily_search import tavily_search_sync
r = tavily_search_sync('Notion competitor analysis', max_results=2)
print(f'Got {len(r)} results')
print(r[0]['title'] if r else 'EMPTY')
"
```
Expected: Got 2 results + 标题

- [ ] **Step 4: 提交**

```bash
git add backend/tools/tavily_search.py
git commit -m "feat(tools): add tavily_search_sync() wrapper"
```

---

### Task 4: ToolRouter 工具注册器

**Files:**
- Create: `backend/tools/registry.py`

- [ ] **Step 1: 创建 registry.py**

```python
import time

from backend.tools.tavily_search import tavily_search_sync


class ToolRouter:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self._call_log: list[dict] = []

    def call_sync(self, tool_name: str, **kwargs):
        start = time.time()
        try:
            if tool_name == "tavily_search":
                result = tavily_search_sync(**kwargs)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            duration_ms = int((time.time() - start) * 1000)
            self._call_log.append({
                "tool": tool_name,
                "duration_ms": duration_ms,
                "ok": True,
                "error": None,
            })
            return result
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            self._call_log.append({
                "tool": tool_name,
                "duration_ms": duration_ms,
                "ok": False,
                "error": str(e),
            })
            raise

    def get_call_log(self) -> list[dict]:
        return self._call_log
```

- [ ] **Step 2: 验证 import**

```bash
PYTHONPATH=. python -c "from backend.tools.registry import ToolRouter; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add backend/tools/registry.py
git commit -m "feat(tools): add ToolRouter with call logging"
```

---

### Task 5: 数据库 CRUD 层

**Files:**
- Create: `backend/db/crud.py`
- Context: `backend/db/models.py`, `backend/db/database.py`

- [ ] **Step 1: 创建 crud.py**

```python
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Report, Task, TaskStatus


async def create_task(
    db: AsyncSession, target_product: str, analysis_dimensions: list[str]
) -> Task:
    task = Task(
        id=uuid.uuid4().hex,
        target_product=target_product,
        analysis_dimensions=analysis_dimensions,
        status=TaskStatus.PENDING,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: str) -> Task | None:
    return await db.get(Task, task_id)


async def list_tasks(
    db: AsyncSession, skip: int = 0, limit: int = 20
) -> tuple[list[Task], int]:
    total = await db.scalar(select(func.count(Task.id)))
    rows = (
        (await db.execute(
            select(Task).order_by(Task.created_at.desc()).offset(skip).limit(limit)
        ))
        .scalars()
        .all()
    )
    return list(rows), total


async def update_task_status(
    db: AsyncSession,
    task_id: str,
    status: TaskStatus,
    error: str | None = None,
) -> None:
    task = await db.get(Task, task_id)
    if task:
        task.status = status
        if error:
            task.error = error
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now(timezone.utc)
        await db.commit()


async def create_report(
    db: AsyncSession,
    task_id: str,
    markdown: str,
    structured: dict,
    quality_score: float,
    token_usage: dict,
) -> Report:
    report = Report(
        id=uuid.uuid4().hex,
        task_id=task_id,
        markdown_content=markdown,
        structured_data=structured,
        quality_score=quality_score,
        token_usage=token_usage,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def get_report(db: AsyncSession, report_id: str) -> Report | None:
    return await db.get(Report, report_id)
```

- [ ] **Step 2: 验证 import**

```bash
PYTHONPATH=. python -c "from backend.db.crud import create_task, get_task, list_tasks, update_task_status, create_report, get_report; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add backend/db/crud.py
git commit -m "feat(db): add async CRUD layer for tasks and reports"
```

---

### Task 6: Planner Agent 节点

**Files:**
- Create: `backend/agents/planner.py`
- Dependencies: Task 1 (state), Task 2 (llm)

- [ ] **Step 1: 创建 planner.py（含 mock 分支）**

```python
import asyncio
import json

from backend.api.routes.events import publish
from backend.core.llm import get_llm, safe_parse_json
from backend.core.state import AnalysisState

MOCK_SEARCH_QUERIES = [
    "{product} competitor analysis 2026",
    "{product} pricing strategy review",
    "{product} market position SWOT",
]
MOCK_ANALYSIS_PLAN = "从功能、定价、市场定位三个维度进行竞品分析"


def run_planner(state: AnalysisState, mock: bool = True) -> dict:
    task_id = state["task_id"]
    product = state["target_product"]

    publish(task_id, "agent_start", {
        "agent": "planner",
        "message": f"正在为 {product} 规划搜索策略...",
    })

    if mock:
        asyncio.run(asyncio.sleep(2))
        queries = [q.format(product=product) for q in MOCK_SEARCH_QUERIES]
        plan = MOCK_ANALYSIS_PLAN
    else:
        llm = get_llm(temperature=0.3)
        prompt = (
            f'你是资深竞品分析规划师。针对产品"{product}"生成搜索计划。\n'
            f'分析维度：{", ".join(state["analysis_dimensions"])}\n'
            f'请生成3-5个英文搜索关键词，每条带2025-2026年份。\n'
            f'严格按JSON格式输出：{{"search_queries": ["query1", "query2"], "analysis_plan": "简短分析计划"}}'
        )
        resp = llm.invoke(prompt)
        result = safe_parse_json(resp.content)
        queries = result.get("search_queries", [
            f"{product} competitor analysis 2026",
            f"{product} pricing features review",
            f"{product} market position SWOT",
        ])
        plan = result.get("analysis_plan", "从多维度进行竞品分析")

    publish(task_id, "agent_complete", {
        "agent": "planner",
        "queries_count": len(queries),
    })

    return {
        "search_queries": queries,
        "analysis_plan": plan,
        "current_agent": "planner",
        "llm_call_count": state["llm_call_count"] + 1,
    }
```

- [ ] **Step 2: 验证 import**

```bash
PYTHONPATH=. python -c "from backend.agents.planner import run_planner; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add backend/agents/planner.py
git commit -m "feat(agent): add Planner node with mock/real branches"
```

---

### Task 7: Research Agent 节点

**Files:**
- Create: `backend/agents/research.py`
- Dependencies: Task 4 (ToolRouter)

- [ ] **Step 1: 创建 research.py**

```python
import asyncio

from backend.api.routes.events import publish
from backend.core.state import AnalysisState
from backend.tools.registry import ToolRouter

MOCK_RESEARCH = [
    {
        "title": "{product} — Best-in-class collaborative workspace",
        "url": "https://example.com/review-1",
        "content": "{product} dominates the collaborative workspace market with over 100M users. Key features include real-time editing, database views, and integrations.",
        "relevance_score": 0.95,
    },
    {
        "title": "{product} Pricing & Plans 2026",
        "url": "https://example.com/pricing-1",
        "content": "Free tier available. Plus plan at $10/user/month. Business plan at $18/user/month. Enterprise custom pricing.",
        "relevance_score": 0.88,
    },
    {
        "title": "Top {product} Competitors & Alternatives",
        "url": "https://example.com/competitors-1",
        "content": "Main competitors include Coda, Confluence, and ClickUp. {product} leads in user experience and integrations.",
        "relevance_score": 0.82,
    },
]


def run_research(state: AnalysisState, mock: bool = True) -> dict:
    task_id = state["task_id"]
    product = state["target_product"]

    publish(task_id, "agent_start", {
        "agent": "research",
        "message": f"正在搜索 {product} 的竞品信息...",
    })

    if mock:
        asyncio.run(asyncio.sleep(2))
        results = []
        for item in MOCK_RESEARCH:
            r = dict(item)
            r["title"] = r["title"].format(product=product)
            r["content"] = r["content"].format(product=product)
            results.append(r)
    else:
        router = ToolRouter(task_id)
        results = []
        seen_urls = set()
        for query in state["search_queries"]:
            try:
                batch = router.call_sync("tavily_search", query=query, max_results=3)
                for item in batch:
                    if item["url"] not in seen_urls:
                        seen_urls.add(item["url"])
                        results.append(item)
            except Exception:
                continue

    publish(task_id, "agent_complete", {
        "agent": "research",
        "results_count": len(results),
    })

    return {
        "raw_research": results,
        "current_agent": "research",
    }
```

- [ ] **Step 2: 验证 import**

```bash
PYTHONPATH=. python -c "from backend.agents.research import run_research; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add backend/agents/research.py
git commit -m "feat(agent): add Research node with Tavily/tool integration"
```

---

### Task 8: Analysis Agent 节点（仅模拟模式）

**Files:**
- Create: `backend/agents/analysis.py`

- [ ] **Step 1: 创建 analysis.py**

```python
import asyncio

from backend.api.routes.events import publish
from backend.core.state import AnalysisState

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


def run_analysis(state: AnalysisState, mock: bool = True) -> dict:
    task_id = state["task_id"]

    publish(task_id, "agent_start", {
        "agent": "analysis",
        "message": "正在执行 SWOT 战略分析...",
    })

    if mock:
        asyncio.run(asyncio.sleep(2))
        result = MOCK_ANALYSIS
    else:
        # MVP 真实模式不使用 Analysis 节点（Writer 直接基于 Research 写作）
        result = MOCK_ANALYSIS

    publish(task_id, "agent_complete", {
        "agent": "analysis",
        "swot_items": len(result.get("swot", [])),
    })

    return {
        "structured_analysis": result,
        "current_agent": "analysis",
        "llm_call_count": state["llm_call_count"] + 1,
    }
```

- [ ] **Step 2: 验证 import**

```bash
PYTHONPATH=. python -c "from backend.agents.analysis import run_analysis; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add backend/agents/analysis.py
git commit -m "feat(agent): add Analysis node (mock mode)"
```

---

### Task 9: Writer Agent 节点

**Files:**
- Create: `backend/agents/writer.py`
- Dependencies: Task 2 (llm)

- [ ] **Step 1: 创建 writer.py**

```python
import asyncio
import json

from backend.api.routes.events import publish
from backend.core.llm import get_llm
from backend.core.state import AnalysisState

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


def run_writer(state: AnalysisState, mock: bool = True) -> dict:
    task_id = state["task_id"]
    product = state["target_product"]

    publish(task_id, "agent_start", {
        "agent": "writer",
        "message": f"正在撰写 {product} 竞品分析报告...",
    })

    if mock:
        asyncio.run(asyncio.sleep(2))
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

    publish(task_id, "agent_complete", {
        "agent": "writer",
        "report_length": len(markdown),
    })

    return {
        "final_report_markdown": markdown,
        "current_agent": "writer",
        "llm_call_count": state["llm_call_count"] + 1,
    }
```

- [ ] **Step 2: 验证 import**

```bash
PYTHONPATH=. python -c "from backend.agents.writer import run_writer; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add backend/agents/writer.py
git commit -m "feat(agent): add Writer node with mock/LLM branches"
```

---

### Task 10: Reviewer Agent 节点（仅模拟模式）

**Files:**
- Create: `backend/agents/reviewer.py`

- [ ] **Step 1: 创建 reviewer.py**

```python
import asyncio

from backend.api.routes.events import publish
from backend.core.state import AnalysisState


def run_reviewer(state: AnalysisState, mock: bool = True) -> dict:
    task_id = state["task_id"]

    publish(task_id, "agent_start", {
        "agent": "reviewer",
        "message": "正在审查报告质量...",
    })

    if mock:
        asyncio.run(asyncio.sleep(1))

    publish(task_id, "agent_complete", {
        "agent": "reviewer",
        "quality_score": 0.85,
    })

    return {
        "quality_score": 0.85,
        "quality_feedback": "报告内容完整，结构清晰，SWOT 分析逻辑合理。",
        "current_agent": "reviewer",
    }
```

- [ ] **Step 2: 验证 import**

```bash
PYTHONPATH=. python -c "from backend.agents.reviewer import run_reviewer; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add backend/agents/reviewer.py
git commit -m "feat(agent): add Reviewer node (mock mode)"
```

---

### Task 11: DAG 工作流 + Runtime 调度

**Files:**
- Create: `backend/core/workflow.py`
- Create: `backend/core/runtime.py`
- Dependencies: Task 1, Task 6-10

- [ ] **Step 1: 创建 workflow.py**

```python
from langgraph.graph import END, StateGraph

from backend.agents.analysis import run_analysis
from backend.agents.planner import run_planner
from backend.agents.research import run_research
from backend.agents.reviewer import run_reviewer
from backend.agents.writer import run_writer
from backend.core.state import AnalysisState


def build_dag(mock: bool = True):
    workflow = StateGraph(AnalysisState)

    if mock:
        workflow.add_node("planner", lambda s: run_planner(s, mock=True))
        workflow.add_node("research", lambda s: run_research(s, mock=True))
        workflow.add_node("analysis", lambda s: run_analysis(s, mock=True))
        workflow.add_node("writer", lambda s: run_writer(s, mock=True))
        workflow.add_node("reviewer", lambda s: run_reviewer(s, mock=True))
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "research")
        workflow.add_edge("research", "analysis")
        workflow.add_edge("analysis", "writer")
        workflow.add_edge("writer", "reviewer")
        workflow.add_edge("reviewer", END)
    else:
        workflow.add_node("planner", lambda s: run_planner(s, mock=False))
        workflow.add_node("research", lambda s: run_research(s, mock=False))
        workflow.add_node("writer", lambda s: run_writer(s, mock=False))
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "research")
        workflow.add_edge("research", "writer")
        workflow.add_edge("writer", END)

    return workflow.compile()
```

- [ ] **Step 2: 验证 import**

```bash
PYTHONPATH=. python -c "from backend.core.workflow import build_dag; d=build_dag(True); print(type(d).__name__)"
```
Expected: `CompiledStateGraph`

- [ ] **Step 3: 创建 runtime.py**

```python
from backend.api.routes.events import publish
from backend.core.workflow import build_dag
from backend.db.crud import create_report, update_task_status
from backend.db.database import async_session_factory
from backend.db.models import TaskStatus


def get_initial_state(task_id: str, target_product: str, analysis_dimensions: list[str]) -> dict:
    return {
        "task_id": task_id,
        "target_product": target_product,
        "analysis_dimensions": analysis_dimensions,
        "search_queries": [],
        "analysis_plan": "",
        "raw_research": [],
        "structured_analysis": None,
        "final_report_markdown": "",
        "metric_cards": None,
        "quality_score": 0.0,
        "quality_feedback": "",
        "current_agent": "",
        "execution_logs": [],
        "token_usage": {},
        "llm_call_count": 0,
        "status": "RUNNING",
        "error": None,
    }


async def run_dag(task_id: str, target_product: str, analysis_dimensions: list[str]) -> None:
    mock = True

    dag = build_dag(mock=mock)
    initial_state = get_initial_state(task_id, target_product, analysis_dimensions)

    async with async_session_factory() as db:
        try:
            await update_task_status(db, task_id, TaskStatus.RUNNING)
            publish(task_id, "task_start", {"task_id": task_id, "product": target_product})

            final_state = await dag.ainvoke(initial_state)

            await create_report(
                db,
                task_id=task_id,
                markdown=final_state["final_report_markdown"],
                structured=final_state.get("structured_analysis") or {},
                quality_score=final_state.get("quality_score", 0.0),
                token_usage=final_state.get("token_usage", {}),
            )
            await update_task_status(db, task_id, TaskStatus.COMPLETED)
            publish(task_id, "task_complete", {
                "task_id": task_id,
                "quality_score": final_state.get("quality_score", 0.0),
            })
        except Exception as e:
            await update_task_status(db, task_id, TaskStatus.FAILED, error=str(e))
            publish(task_id, "task_failed", {"task_id": task_id, "error": str(e)})
```

- [ ] **Step 4: 验证 import**

```bash
PYTHONPATH=. python -c "from backend.core.runtime import run_dag, get_initial_state; print('OK')"
```
Expected: `OK`

- [ ] **Step 5: 提交**

```bash
git add backend/core/workflow.py backend/core/runtime.py
git commit -m "feat(core): add DAG builder + async runtime with mock/real support"
```

---

### Task 12: 后端路由改造 + CLI 测试脚本

**Files:**
- Modify: `backend/api/routes/tasks.py`
- Modify: `backend/api/routes/reports.py`
- Create: `backend/test_pipeline.py`
- Dependencies: Task 5 (CRUD), Task 11 (runtime)

- [ ] **Step 1: 改造 tasks.py — POST /api/tasks 真实调用**

找到 POST /api/tasks 路由处理函数，替换为：

```python
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.runtime import run_dag
from backend.db.crud import create_task as create_task_db
from backend.db.crud import get_task, list_tasks
from backend.db.database import get_db
from backend.schemas.base import err, ok
from backend.schemas.task import TaskCreateRequest, TaskListResponse, TaskResponse

router = APIRouter(tags=["tasks"], prefix="/tasks")


@router.post("", status_code=201)
async def create_task(
    body: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    task = await create_task_db(db, body.target_product, body.analysis_dimensions)
    background_tasks.add_task(run_dag, task.id, task.target_product, task.analysis_dimensions)
    return ok(TaskResponse.model_validate(task))


@router.get("")
async def list_task_routes(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_tasks(db, skip, limit)
    return ok(TaskListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[TaskResponse.model_validate(t) for t in items],
    ))


@router.get("/{task_id}")
async def get_task_route(task_id: str, db: AsyncSession = Depends(get_db)):
    task = await get_task(db, task_id)
    if not task:
        return err("任务不存在")
    return ok(TaskResponse.model_validate(task))
```

- [ ] **Step 2: 改造 reports.py — GET /api/reports/{id} 真实查询**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.crud import get_report
from backend.db.database import get_db
from backend.schemas.base import err, ok
from backend.schemas.report import ReportResponse

router = APIRouter(tags=["reports"], prefix="/reports")


@router.get("/{report_id}")
async def get_report_route(report_id: str, db: AsyncSession = Depends(get_db)):
    report = await get_report(db, report_id)
    if not report:
        return err("报告不存在")
    return ok(ReportResponse.model_validate(report))
```

- [ ] **Step 3: 创建 test_pipeline.py**

```python
import asyncio
import sys

from backend.core.runtime import run_dag


async def main():
    product = sys.argv[1] if len(sys.argv) > 1 else "Notion"
    task_id = "test-" + product.lower().replace(" ", "-")
    print(f"Starting analysis for: {product} (task_id={task_id})")
    await run_dag(task_id, product, ["功能分析", "定价策略", "SWOT分析", "市场定位"])
    print(f"Done! Check database for task_id={task_id}")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 4: 验证 CLI 端到端**

先确认数据库连接正常（已在用 Supabase），然后运行：

```bash
cd /d/MYdesktop/CompeteScopeAgent && PYTHONPATH=. python backend/test_pipeline.py "Notion"
```

Expected: 约 10 秒后打印 `Done! Check database for task_id=test-notion`，无报错。然后检查数据库：

```bash
PYTHONPATH=. python -c "
import asyncio
from backend.db.database import async_session_factory
from backend.db.models import Task, Report
from sqlalchemy import select

async def check():
    async with async_session_factory() as db:
        task = (await db.execute(select(Task).where(Task.id == 'test-notion'))).scalar_one_or_none()
        if task:
            print(f'Task status: {task.status.value}')
        report = (await db.execute(select(Report).where(Report.task_id == 'test-notion'))).scalar_one_or_none()
        if report:
            print(f'Report exists, markdown length: {len(report.markdown_content)}')
asyncio.run(check())
"
```

Expected: `Task status: COMPLETED` + `Report exists, markdown length: > 100`

- [ ] **Step 5: 提交**

```bash
git add backend/api/routes/tasks.py backend/api/routes/reports.py backend/test_pipeline.py
git commit -m "feat(api): wire real CRUD + BackgroundTask into routes, add CLI test"
```

---

### Task 13: 前端工作台布局 + Sidebar

**Files:**
- Create: `frontend/app/(workspace)/layout.tsx`
- Create: `frontend/components/workspace/Sidebar.tsx`
- Context: 现有 `frontend/app/layout.tsx`（根布局，暗色主题）、`frontend/app/globals.css`

- [ ] **Step 1: 安装 react-markdown（提前安装，后续才用）**

```bash
cd /d/MYdesktop/CompeteScopeAgent/frontend && npm install react-markdown
```

- [ ] **Step 2: 创建 Sidebar.tsx**

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard" },
  { href: "/tasks/new", label: "新建任务" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-60 flex-col border-r border-zinc-800 bg-[#0f1117]">
      <div className="px-6 py-5">
        <h1 className="text-lg font-bold tracking-tight text-white">
          Compete<span className="text-indigo-400">Scope</span>
        </h1>
      </div>

      <nav className="flex-1 px-3 py-2 space-y-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-lg px-3 py-2 text-sm transition ${
                active
                  ? "bg-[#1a1d2e] text-indigo-400"
                  : "text-zinc-400 hover:bg-[#1a1d2e] hover:text-zinc-200"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="px-6 py-4 text-xs text-zinc-600">v0.1.0 MVP</div>
    </aside>
  );
}
```

- [ ] **Step 3: 创建 layout.tsx**

```tsx
import Sidebar from "@/components/workspace/Sidebar";

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-[#0f1117] text-zinc-200">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">{children}</main>
    </div>
  );
}
```

- [ ] **Step 4: 验证编译**

```bash
cd /d/MYdesktop/CompeteScopeAgent/frontend && npx tsc --noEmit 2>&1 | head -20
```

Expected: 无新错误（本项目已有的错误不算）

- [ ] **Step 5: 提交**

```bash
git add frontend/app/\(workspace\)/layout.tsx frontend/components/workspace/Sidebar.tsx frontend/package.json frontend/package-lock.json
git commit -m "feat(frontend): add workspace layout with sidebar navigation"
```

---

### Task 14: Dashboard 任务列表页 + TaskCard

**Files:**
- Create: `frontend/app/(workspace)/page.tsx`
- Create: `frontend/components/workspace/TaskCard.tsx`
- Context: `frontend/lib/utils.ts` (apiFetch), `frontend/types/analysis.ts` (AnalysisJob)

- [ ] **Step 1: 创建 TaskCard.tsx**

```tsx
"use client";

import Link from "next/link";

interface TaskCardProps {
  id: string;
  target_product: string;
  status: string;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  PENDING: "bg-zinc-600 text-zinc-300",
  RUNNING: "bg-blue-600 text-blue-100",
  COMPLETED: "bg-green-600 text-green-100",
  FAILED: "bg-red-600 text-red-100",
};

const STATUS_LABELS: Record<string, string> = {
  PENDING: "等待中",
  RUNNING: "执行中",
  COMPLETED: "已完成",
  FAILED: "失败",
};

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "刚刚";
  if (mins < 60) return `${mins} 分钟前`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} 小时前`;
  return `${Math.floor(hours / 24)} 天前`;
}

export default function TaskCard({ id, target_product, status, created_at }: TaskCardProps) {
  const color = STATUS_COLORS[status] || "bg-zinc-600 text-zinc-300";
  const label = STATUS_LABELS[status] || status;

  return (
    <Link
      href={`/tasks/${id}`}
      className="block rounded-xl border border-zinc-800 bg-[#1a1d2e] p-5 transition hover:border-zinc-600"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">{target_product}</h3>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${color}`}>{label}</span>
      </div>
      <p className="mt-2 text-sm text-zinc-500">{timeAgo(created_at)}</p>
    </Link>
  );
}
```

- [ ] **Step 2: 创建 Dashboard page.tsx**

```tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/utils";
import TaskCard from "@/components/workspace/TaskCard";

interface TaskItem {
  id: string;
  target_product: string;
  status: string;
  created_at: string;
}

export default function DashboardPage() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    apiFetch<{ data: { items: TaskItem[] } }>("/api/tasks?skip=0&limit=20")
      .then((res) => setTasks(res.data.items || []))
      .catch(() => setTasks([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold text-white">任务列表</h2>
        <button
          onClick={() => router.push("/tasks/new")}
          className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 transition"
        >
          新建任务
        </button>
      </div>

      {loading ? (
        <p className="text-zinc-500">加载中...</p>
      ) : tasks.length === 0 ? (
        <p className="text-zinc-500">暂无任务，点击右上角创建第一个分析任务</p>
      ) : (
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
          {tasks.map((t) => (
            <TaskCard key={t.id} {...t} />
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: 验证编译**

```bash
cd /d/MYdesktop/CompeteScopeAgent/frontend && npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 4: 提交**

```bash
git add frontend/app/\(workspace\)/page.tsx frontend/components/workspace/TaskCard.tsx
git commit -m "feat(frontend): add dashboard page with task list"
```

---

### Task 15: 创建任务表单页

**Files:**
- Create: `frontend/app/(workspace)/tasks/new/page.tsx`

- [ ] **Step 1: 创建 page.tsx**

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/utils";

const DIMENSIONS = ["功能分析", "定价策略", "SWOT分析", "市场定位", "用户口碑"];

export default function NewTaskPage() {
  const [product, setProduct] = useState("");
  const [selected, setSelected] = useState<string[]>(["SWOT分析"]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const toggle = (dim: string) => {
    setSelected((prev) =>
      prev.includes(dim) ? prev.filter((d) => d !== dim) : [...prev, dim]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!product.trim() || selected.length === 0) return;
    setSubmitting(true);
    setError("");

    try {
      const res = await apiFetch<{ data: { id: string } }>("/api/tasks", {
        method: "POST",
        body: JSON.stringify({ target_product: product.trim(), analysis_dimensions: selected }),
      });
      router.push(`/tasks/${res.data.id}`);
    } catch {
      setError("创建任务失败，请检查后端服务是否运行");
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-xl">
      <h2 className="text-2xl font-bold text-white mb-8">新建分析任务</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">目标产品</label>
          <input
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            placeholder="例如：Notion、Figma、Linear..."
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-3 text-sm text-white outline-none focus:border-indigo-400"
            autoFocus
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">分析维度（至少选一项）</label>
          <div className="flex flex-wrap gap-2">
            {DIMENSIONS.map((dim) => (
              <button
                key={dim}
                type="button"
                onClick={() => toggle(dim)}
                className={`rounded-full px-4 py-1.5 text-sm transition ${
                  selected.includes(dim)
                    ? "bg-indigo-600 text-white"
                    : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
                }`}
              >
                {dim}
              </button>
            ))}
          </div>
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={submitting || !product.trim() || selected.length === 0}
          className="w-full rounded-lg bg-indigo-600 py-3 text-sm font-medium text-white hover:bg-indigo-500 transition disabled:opacity-50"
        >
          {submitting ? "正在创建任务..." : "开始分析"}
        </button>
      </form>
    </div>
  );
}
```

- [ ] **Step 2: 验证编译**

```bash
cd /d/MYdesktop/CompeteScopeAgent/frontend && npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 3: 提交**

```bash
git add frontend/app/\(workspace\)/tasks/new/page.tsx
git commit -m "feat(frontend): add task creation form page"
```

---

### Task 16: 任务详情页 + DAGVisualizer + 报告页

**Files:**
- Create: `frontend/components/dag/DAGVisualizer.tsx`
- Create: `frontend/app/(workspace)/tasks/[id]/page.tsx`
- Create: `frontend/components/report/ReportViewer.tsx`
- Create: `frontend/app/(workspace)/reports/[id]/page.tsx`
- Context: `frontend/types/sse-events.ts` (SSEEvent, AgentState)

- [ ] **Step 1: 创建 DAGVisualizer.tsx**

```tsx
"use client";

interface DAGVisualizerProps {
  agentStates: Record<string, { status: string }>;
}

const AGENT_NAMES: Record<string, string> = {
  planner: "规划师",
  research: "研究员",
  analysis: "分析师",
  writer: "撰稿人",
  reviewer: "审查员",
};

const AGENT_COLORS: Record<string, string> = {
  planner: "#3b82f6",
  research: "#f59e0b",
  analysis: "#8b5cf6",
  writer: "#22c55e",
  reviewer: "#64748b",
};

export default function DAGVisualizer({ agentStates }: DAGVisualizerProps) {
  const agents = Object.keys(agentStates);
  if (agents.length === 0) return null;

  const NODE_H = 48;
  const NODE_W = 140;
  const GAP = 24;
  const PADDING = 20;
  const totalH = agents.length * NODE_H + (agents.length - 1) * GAP + PADDING * 2;
  const centerX = NODE_W / 2 + PADDING;
  const viewBoxW = NODE_W + PADDING * 2;
  const viewBoxH = totalH;

  return (
    <div className="flex justify-center">
      <svg viewBox={`0 0 ${viewBoxW} ${viewBoxH}`} className="w-48 h-auto">
        {agents.map((agent, i) => {
          const y = PADDING + i * (NODE_H + GAP);
          const label = AGENT_NAMES[agent] || agent;
          const state = agentStates[agent]?.status || "waiting";

          let borderColor = "#374151";
          let textColor = "#6b7280";
          let pulse = false;
          let icon = "";

          if (state === "running") {
            borderColor = AGENT_COLORS[agent] || "#6366f1";
            textColor = borderColor;
            pulse = true;
          } else if (state === "completed") {
            borderColor = "#22c55e";
            textColor = "#4ade80";
            icon = "✓";
          } else if (state === "failed") {
            borderColor = "#ef4444";
            textColor = "#f87171";
            icon = "✗";
          }

          return (
            <g key={agent}>
              <rect
                x={PADDING}
                y={y}
                width={NODE_W}
                height={NODE_H}
                rx={8}
                ry={8}
                fill="#1a1d2e"
                stroke={borderColor}
                strokeWidth={2}
                className={pulse ? "animate-pulse" : ""}
              />
              <text
                x={centerX}
                y={y + NODE_H / 2 + 1}
                textAnchor="middle"
                dominantBaseline="middle"
                fill={textColor}
                fontSize={14}
                fontWeight={500}
              >
                {label} {icon}
              </text>
              {i < agents.length - 1 && (
                <line
                  x1={centerX}
                  y1={y + NODE_H}
                  x2={centerX}
                  y2={y + NODE_H + GAP}
                  stroke="#374151"
                  strokeWidth={2}
                />
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
```

- [ ] **Step 2: 创建任务详情页 page.tsx**

```tsx
"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import DAGVisualizer from "@/components/dag/DAGVisualizer";

const STATUS_MESSAGES: Record<string, string> = {
  planner: "规划师正在制定搜索策略...",
  research: "研究员正在全网搜索竞品信息...",
  analysis: "分析师正在提炼 SWOT 洞察...",
  writer: "撰稿人正在撰写分析报告...",
  reviewer: "审查员正在审核报告质量...",
};

export default function TaskDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [agentStates, setAgentStates] = useState<Record<string, { status: string }>>({});
  const [statusMessage, setStatusMessage] = useState("任务已提交，等待启动...");
  const [error, setError] = useState("");
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const es = new EventSource(`${base}/api/analyze/${id}/stream`);
    esRef.current = es;

    es.addEventListener("agent_start", (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setAgentStates((prev) => ({ ...prev, [data.agent]: { status: "running" } }));
      setStatusMessage(STATUS_MESSAGES[data.agent] || `${data.agent} 正在执行...`);
    });

    es.addEventListener("agent_complete", (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setAgentStates((prev) => ({ ...prev, [data.agent]: { status: "completed" } }));
    });

    es.addEventListener("task_complete", () => {
      es.close();
      // 短暂延迟后跳转到报告页
      setTimeout(() => router.push(`/reports/${id}`), 500);
    });

    es.addEventListener("task_start", () => {
      setStatusMessage("Agent 工作流已启动...");
    });

    es.addEventListener("task_failed", (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setError(data.error || "任务执行失败");
      es.close();
    });

    es.onerror = () => {
      // EventSource 会自动重连，这里不关闭
    };

    return () => {
      es.close();
    };
  }, [id, router]);

  return (
    <div className="mx-auto max-w-xl">
      <h2 className="text-2xl font-bold text-white mb-8">任务执行中</h2>

      <DAGVisualizer agentStates={agentStates} />

      <div className="mt-8 text-center">
        {error ? (
          <p className="text-red-400">{error}</p>
        ) : (
          <p className="text-zinc-400">{statusMessage}</p>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: 创建 ReportViewer.tsx**

```tsx
"use client";

import ReactMarkdown from "react-markdown";

interface ReportViewerProps {
  markdown: string;
}

export default function ReportViewer({ markdown }: ReportViewerProps) {
  return (
    <div className="prose prose-invert prose-zinc max-w-none">
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </div>
  );
}
```

- [ ] **Step 4: 创建报告页 page.tsx**

```tsx
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/utils";
import ReportViewer from "@/components/report/ReportViewer";

interface ReportData {
  id: string;
  markdown_content: string;
  quality_score: number;
}

export default function ReportPage() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<{ data: ReportData }>(`/api/reports/${id}`)
      .then((res) => setReport(res.data))
      .catch(() => setError("报告未找到"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p className="text-zinc-500">加载中...</p>;
  if (error) return <p className="text-red-400">{error}</p>;
  if (!report) return null;

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-8 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">分析报告</h2>
        <span className="rounded-full bg-green-600/20 px-4 py-1 text-sm text-green-400">
          质量评分 {(report.quality_score * 100).toFixed(0)}%
        </span>
      </div>

      <ReportViewer markdown={report.markdown_content} />
    </div>
  );
}
```

- [ ] **Step 5: 验证编译**

```bash
cd /d/MYdesktop/CompeteScopeAgent/frontend && npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 6: 启动前后端，浏览器验证全流程**

启动后端：
```bash
cd /d/MYdesktop/CompeteScopeAgent && PYTHONPATH=. uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

启动前端（另一个终端）：
```bash
cd /d/MYdesktop/CompeteScopeAgent/frontend && npm run dev
```

浏览器访问 `http://localhost:3000`：
1. 看到 Dashboard 空列表 → 点击「新建任务」
2. 输入 "Notion" → 勾选维度 → 点击「开始分析」
3. 自动跳转任务详情页 → DAG 节点逐个高亮（约每 2 秒一个）
4. 全部完成后自动跳转报告页 → 渲染 Markdown

- [ ] **Step 7: 提交**

```bash
git add frontend/components/dag/DAGVisualizer.tsx frontend/app/\(workspace\)/tasks/ frontend/components/report/ReportViewer.tsx frontend/app/\(workspace\)/reports/
git commit -m "feat(frontend): add task detail, DAG visualizer, and report view"
```

---

### Task 17（Day 3）: 环境变量开关 + Runtime 接入真实模式

**Files:**
- Modify: `backend/core/runtime.py`
- Context: 已有 `COMPETESCOPE_MOCK` 在 `.env` 中

- [ ] **Step 1: 在 config.py 中添加 COMPETESCOPE_MOCK 设置**

检查 `backend/config.py`，确认有：

```python
COMPETESCOPE_MOCK: bool = True
```

如果没有，在 Settings 类中添加。`.env` 中设置 `COMPETESCOPE_MOCK=false`。

- [ ] **Step 2: 改造 runtime.py 读取环境变量**

修改 `run_dag()` 函数的 `mock = True` 为：

```python
from backend.config import settings
mock = settings.COMPETESCOPE_MOCK
```

- [ ] **Step 3: 提交**

```bash
git add backend/core/runtime.py backend/config.py
git commit -m "feat(core): wire COMPETESCOPE_MOCK env var to runtime"
```

---

### Task 18（Day 3）: 验证真实 LLM 模式 — Planner

**Files:**
- Modify: `backend/agents/planner.py`（已在 Task 6 写好 mock/real 分支，无需改动）

- [ ] **Step 1: 设置环境变量并测试**

```bash
cd /d/MYdesktop/CompeteScopeAgent
# 确认 .env 中 COMPETESCOPE_MOCK=false
grep COMPETESCOPE_MOCK .env
```

```bash
PYTHONPATH=. python -c "
import asyncio
from backend.core.state import AnalysisState

# 手动模拟 state
state: AnalysisState = {
    'task_id': 'test-real',
    'target_product': 'Notion',
    'analysis_dimensions': ['功能分析', 'SWOT分析'],
    'search_queries': [],
    'analysis_plan': '',
    'raw_research': [],
    'structured_analysis': None,
    'final_report_markdown': '',
    'metric_cards': None,
    'quality_score': 0.0,
    'quality_feedback': '',
    'current_agent': '',
    'execution_logs': [],
    'token_usage': {},
    'llm_call_count': 0,
    'status': '',
    'error': None,
}

from backend.agents.planner import run_planner
result = run_planner(state, mock=False)
print('Search queries:', result['search_queries'])
print('Analysis plan:', result['analysis_plan'])
"
```

Expected: 3-5 个真实的英文搜索关键词，分析计划为中文。

- [ ] **Step 2: 提交**（如有修改）

---

### Task 19（Day 3）: 验证真实模式 — Research + Writer 端到端

**Files:**
- 无需新建，已在 Task 7 和 Task 9 写好

- [ ] **Step 1: 完整 CLI 测试**

```bash
cd /d/MYdesktop/CompeteScopeAgent
# 确保 COMPETESCOPE_MOCK=false
PYTHONPATH=. python backend/test_pipeline.py "Notion"
```

Expected: 约 30-90 秒后完成（会真实调用 DeepSeek + Tavily），无报错。

- [ ] **Step 2: 检查报告内容是否为真实生成**

```bash
PYTHONPATH=. python -c "
import asyncio
from backend.db.database import async_session_factory
from backend.db.models import Report
from sqlalchemy import select

async def check():
    async with async_session_factory() as db:
        report = (await db.execute(select(Report).order_by(Report.created_at.desc()).limit(1))).scalar_one_or_none()
        if report:
            print('Report preview (first 300 chars):')
            print(report.markdown_content[:300])
            print(f'... (total {len(report.markdown_content)} chars)')
asyncio.run(check())
"
```

Expected: 报告中包含 "Notion" 相关内容，不是硬编码的 `{product}` 占位符。

- [ ] **Step 3: 提交**

```bash
git add backend/test_pipeline.py
git commit -m "feat: verify real LLM + Tavily end-to-end pipeline"
```

---

### Task 20（Day 3）: 浏览器全流程 — 真实模式

**Files:**
- 无需改动，前端不变

- [ ] **Step 1: 启动后端（真实模式）**

确保 `.env` 中 `COMPETESCOPE_MOCK=false`，启动：

```bash
cd /d/MYdesktop/CompeteScopeAgent && PYTHONPATH=. uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

- [ ] **Step 2: 启动前端**

```bash
cd /d/MYdesktop/CompeteScopeAgent/frontend && npm run dev
```

- [ ] **Step 3: 浏览器端到端测试**

1. `http://localhost:3000` → Dashboard
2. 新建任务 → "Notion" → 勾选维度 → 提交
3. 任务详情页 → DAG 3 节点（真实模式）逐个高亮
4. 等待 30-90 秒 → 报告页 → 渲染真实 Markdown 报告

- [ ] **Step 4: 切回模拟模式验证**

```bash
# 改 .env：COMPETESCOPE_MOCK=true，重启后端
```

重复 Step 3，确认切回 5 节点 DAG，报告内容为预写中文 Markdown。

- [ ] **Step 5: 最终提交**

```bash
git add .env.example
git commit -m "docs: update .env.example with COMPETESCOPE_MOCK setting"
```

---

## 验收检查清单

- [ ] `COMPETESCOPE_MOCK=true` → 5 节点 DAG → 约 10 秒完成 → 浏览器全流程
- [ ] `COMPETESCOPE_MOCK=false` → 3 节点 DAG → 30-90 秒完成 → 浏览器全流程
- [ ] 数据库中 tasks 和 reports 表有记录
- [ ] 模拟模式：报告为预写中文 Markdown
- [ ] 真实模式：报告包含产品相关真实内容（不是占位符）
- [ ] Dashboard 历史列表可看到已创建的任务
- [ ] DAG 节点状态正确高亮（waiting → running → completed）
- [ ] CI 通过（ruff + mypy + ESLint）
