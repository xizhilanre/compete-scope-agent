# CompeteScope — 企业级竞品分析 AI Agent 平台
## 完整 Spec 开发文档 · 可直接 Vibecoding

> **版本**：v3.0（全 Python 后端版）
> **定位**：企业级 AI Agent 工作台，不是聊天机器人 Demo
> **工期**：20 天 MVP
> **团队**：C（Agent/架构）· A（前端）· B（后端/联调）
> **后端技术栈**：FastAPI + Python（API 与 Agent 合并为单一 Python 服务）
> **直接可用于**：Cursor / Claude Code / Trae / Vibecoding 上下文

---

## 目录

1. [项目定位与核心价值](#1-项目定位与核心价值)
2. [参考 Craft Agents 的改造策略](#2-参考-craft-agents-的改造策略)
3. [完整系统架构](#3-完整系统架构)
4. [Monorepo 目录结构](#4-monorepo-目录结构)
5. [Agent Runtime 设计](#5-agent-runtime-设计)
6. [Tool Ecosystem Layer](#6-tool-ecosystem-layer)
7. [数据库设计（SQLAlchemy + Alembic）](#7-数据库设计sqlalchemy--alembic)
8. [FastAPI 后端设计](#8-fastapi-后端设计)
9. [SSE 事件协议](#9-sse-事件协议)
10. [Prompt 管理结构](#10-prompt-管理结构)
11. [前端页面架构（AI Native Workspace）](#11-前端页面架构ai-native-workspace)
12. [Observability 架构](#12-observability-架构)
13. [MVP 功能边界与优先级](#13-mvp-功能边界与优先级)
14. [20 天每日开发计划](#14-20-天每日开发计划)
15. [团队协作规范](#15-团队协作规范)
16. [Docker 部署结构](#16-docker-部署结构)
17. [环境变量完整清单](#17-环境变量完整清单)
18. [Demo 演示路线](#18-demo-演示路线)
19. [风险控制与应急方案](#19-风险控制与应急方案)

---

## 1. 项目定位与核心价值

### 1.1 一句话定位

> 输入一个产品名，10 分钟内多 Agent 协同自动生成企业级竞品分析报告。

### 1.2 和普通 Demo 的本质区别

| 维度 | 普通 LLM Demo | CompeteScope |
|---|---|---|
| 执行方式 | 用户一问一答 | Agent 自主串联执行完整 DAG |
| 数据来源 | 模型记忆 | Tavily 实时搜索 + 网页抓取 |
| 输出形式 | 一段文字 | JSON 驱动结构化报告（SWOT + 指标卡片）|
| 可观测性 | 黑盒 | 每个 Agent 的 Trace / Tool Call 可见 |
| 工程架构 | 单文件脚本 | Multi-Agent Runtime + DAG Workflow |
| 企业感 | 无 | B 端工作台 UI，Citation 溯源，Eval 评分 |

### 1.3 技术含金量亮点（评审/简历用）

- **LangGraph DAG Workflow** — 条件边 + 重试机制 + 状态机
- **Multi-Agent Runtime** — Planner → Research → Analysis → Writer → Reviewer
- **FastAPI 异步后端** — async/await + SSE Streaming + BackgroundTask
- **Tool Ecosystem** — Tool Registry + Tool Router + Tool Trace
- **Structured Output** — JSON Schema 驱动的 Agent 输出验证
- **Citation Traceability** — 每条结论绑定信息来源
- **Observability** — Agent Timeline + Token Cost + Execution Replay
- **全栈 Python** — 前后端解耦，后端完全统一为 Python 生态

---

## 2. 参考 Craft Agents 的改造策略

### 2.1 复用 vs 改造对照表

| 模块 | 操作 | 说明 |
|---|---|---|
| Agent Runtime 分层思想 | ✅ 参考 | Core / Tool / Orchestration 分层 |
| DAG Workflow 编排 | ✅ 参考 + 改造 | LangGraph 实现，节点对应竞品分析流程 |
| Tool Registry 模式 | ✅ 参考 + 实现 | Tavily / Firecrawl 统一注册 |
| AI Workspace UI 思路 | ✅ 参考风格 | Next.js + Shadcn B 端工作台 |
| 业务逻辑（竞品分析） | 🔧 全部改造 | Agent 职责、Prompt、输出格式全部业务化 |
| 后端 API 层 | 🔧 自建 | **FastAPI 统一实现，不拆分微服务** |
| 数据库 | 🔧 自建 | SQLAlchemy async + PostgreSQL + Alembic |
| Observability | 🔧 简化版 | 自建 ExecutionLog 表，MVP 不依赖 LangSmith |

### 2.2 架构简化决策：为什么合并 API + Agent 为一个 Python 服务

**原方案（v2.0）**：NestJS API + Python Agent 两个独立服务，通过 HTTP 互调。

**新方案（v3.0）**：FastAPI 同时承担 API Gateway 和 Agent 调度，消除跨语言调用。

优势：
- 消除 NestJS ↔ Python 之间的 HTTP 内部调用和类型不一致问题
- B 只需要写 Python，降低学习成本
- 部署更简单，一个 Python 进程搞定
- SSE 直接在 FastAPI 里推送，不需要内部回调机制
- 数据库操作统一用 SQLAlchemy，类型安全一致

---

## 3. 完整系统架构

### 3.1 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                            │
│         Next.js AI Native Workspace (B端工作台)              │
│  Task Dashboard · DAG Viz · Agent Trace · Report · Monitor  │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST + SSE
┌──────────────────────────▼──────────────────────────────────┐
│              Python Backend (FastAPI · Port 8000)            │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │               API Layer (FastAPI Routers)            │    │
│  │  /tasks  /reports  /traces  /events(SSE)  /health   │    │
│  └─────────────────────────┬───────────────────────────┘    │
│                            │ asyncio.create_task            │
│  ┌─────────────────────────▼───────────────────────────┐    │
│  │             Agent Runtime (LangGraph)                │    │
│  │  Planner → Research → Analysis → Writer → Reviewer  │    │
│  └─────────────────────────┬───────────────────────────┘    │
│                            │                                 │
│  ┌─────────────────────────▼───────────────────────────┐    │
│  │               Tool Layer                             │    │
│  │  ToolRegistry · Tavily · Firecrawl                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │ asyncpg
┌──────────────────────────▼──────────────────────────────────┐
│                  PostgreSQL                                  │
│  tasks · reports · execution_logs                           │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 执行数据流

```
用户提交表单（产品名 + 分析维度）
  ↓
POST /api/tasks
  → 创建 Task 记录（status=PENDING）
  → asyncio.create_task(run_dag(task_id))  ← 异步启动，立即返回
  → 返回 {task_id}
  ↓
前端建立 SSE: GET /api/tasks/{id}/events
  ↓ (FastAPI StreamingResponse，持续推送)
DAG 执行中，每步直接写入 SSE 队列：
  ├── event: agent_start   {agent: "planner", message: "分解分析目标..."}
  ├── event: agent_start   {agent: "research"}
  ├── event: tool_call     {tool: "tavily_search", query: "..."}
  ├── event: tool_result   {count: 7, latency_ms: 1200}
  ├── event: agent_complete {agent: "research", items: 7}
  ├── event: agent_start   {agent: "analysis"}
  ├── event: agent_complete {agent: "analysis"}
  ├── event: agent_start   {agent: "writer"}
  ├── event: agent_complete {agent: "writer"}
  ├── event: agent_start   {agent: "reviewer"}
  └── event: task_complete {report_id: "xxx", quality_score: 0.87}
  ↓
前端跳转 → /reports/{id}
```

### 3.3 LangGraph DAG 图

```
START
  │
  ▼
┌─────────────┐
│  planner    │  分解目标 → 生成搜索词列表
└──────┬──────┘
       ▼
┌─────────────┐     ┌──────────────────┐
│  research   │────▶│  tavily_search   │
└──────┬──────┘     │  firecrawl(可选) │
       │            └──────────────────┘
       │ [info_count < 5 且 retry < 2 → 重试]
       ▼
┌─────────────┐
│  analysis   │  提炼 SWOT + 结构化 JSON
└──────┬──────┘
       │ [JSON 解析失败 且 retry < 1 → 重试]
       ▼
┌─────────────┐
│   writer    │  生成 Markdown 报告 + MetricCards
└──────┬──────┘
       │ [字数 < 500 且 retry < 1 → 重试]
       ▼
┌─────────────┐
│  reviewer   │  质量评分 + Citation 绑定
└──────┬──────┘
       ▼
      END（写入数据库 + 推送 task_complete SSE）
```

---

## 4. Monorepo 目录结构

```
compete-scope/
├── backend/                          # B 和 C 的主战场（Python）
│   ├── api/                          # FastAPI 路由层（B 负责）
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── tasks.py              # POST/GET /api/tasks
│   │   │   ├── reports.py            # GET /api/reports
│   │   │   ├── traces.py             # GET /api/traces
│   │   │   └── events.py             # GET /api/tasks/{id}/events (SSE)
│   │   └── deps.py                   # FastAPI 依赖注入（DB session 等）
│   │
│   ├── agents/                       # LangGraph Agent 层（C 负责）
│   │   ├── planner.py
│   │   ├── research.py
│   │   ├── analysis.py
│   │   ├── writer.py
│   │   └── reviewer.py
│   │
│   ├── core/                         # 核心基础设施（C 负责）
│   │   ├── state.py                  # ⚠️ 共享 State Schema
│   │   ├── runtime.py                # DAG 执行入口 + SSE 队列管理
│   │   └── workflow.py               # LangGraph DAG 定义
│   │
│   ├── tools/                        # Tool Ecosystem（C 负责）
│   │   ├── registry.py               # Tool Registry
│   │   ├── tavily_search.py
│   │   └── firecrawl.py
│   │
│   ├── db/                           # 数据库层（B 负责）
│   │   ├── database.py               # SQLAlchemy async engine
│   │   ├── models.py                 # ORM 模型
│   │   └── crud.py                   # CRUD 操作
│   │
│   ├── prompts/                      # Prompt 文件（C 负责）
│   │   ├── planner/v1.txt
│   │   ├── research/v1.txt
│   │   ├── analysis/v1.txt
│   │   ├── writer/v1.txt
│   │   └── reviewer/v1.txt
│   │
│   ├── schemas/                      # Pydantic 模型（B/C 共用）
│   │   ├── task.py
│   │   ├── report.py
│   │   └── events.py                 # ⚠️ SSE 事件 Schema
│   │
│   ├── tests/
│   │   ├── test_agents.py
│   │   ├── test_api.py
│   │   └── fixtures/
│   │
│   ├── alembic/                      # 数据库迁移（B 负责）
│   │   ├── env.py
│   │   └── versions/
│   │
│   ├── main.py                       # FastAPI app 入口
│   ├── config.py                     # 配置（从环境变量读取）
│   ├── requirements.txt
│   └── alembic.ini
│
├── frontend/                         # A 的主战场（Next.js）
│   ├── app/
│   │   ├── (workspace)/
│   │   │   ├── layout.tsx            # 工作台布局（Sidebar + TopNav）
│   │   │   ├── page.tsx              # Dashboard（任务列表）
│   │   │   ├── tasks/
│   │   │   │   ├── new/page.tsx      # 创建任务
│   │   │   │   └── [id]/page.tsx     # 任务执行详情 + DAG 进度
│   │   │   ├── reports/
│   │   │   │   └── [id]/page.tsx     # 报告详情
│   │   │   ├── traces/
│   │   │   │   └── [id]/page.tsx     # Agent Trace 详情
│   │   │   └── monitor/
│   │   │       └── page.tsx          # Runtime Monitor
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                       # shadcn/ui 组件
│   │   ├── workspace/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── TopNav.tsx
│   │   │   └── WorkspaceLayout.tsx
│   │   ├── dag/
│   │   │   ├── DAGVisualizer.tsx     # ⭐ DAG 执行可视化
│   │   │   ├── AgentNode.tsx
│   │   │   └── AgentTimeline.tsx
│   │   ├── report/
│   │   │   ├── ReportViewer.tsx
│   │   │   ├── SWOTChart.tsx
│   │   │   ├── MetricCards.tsx
│   │   │   └── CitationPanel.tsx
│   │   └── trace/
│   │       ├── TraceViewer.tsx
│   │       ├── ToolCallCard.tsx
│   │       └── TokenUsageBar.tsx
│   ├── hooks/
│   │   ├── useSSE.ts
│   │   ├── useTask.ts
│   │   └── useReport.ts
│   ├── lib/
│   │   ├── api.ts                    # API 客户端（fetch 封装）
│   │   └── utils.ts
│   ├── types/
│   │   ├── task.ts
│   │   ├── report.ts
│   │   └── sse-events.ts             # ⚠️ SSE 事件类型（与 backend/schemas/events.py 对齐）
│   └── package.json
│
├── docs/
│   ├── api-contract.md               # ⚠️ API 契约（改动需全员确认）
│   ├── sse-events.md                 # ⚠️ SSE 事件格式
│   └── agent-state.md               # ⚠️ State Schema 文档
│
├── scripts/
│   ├── setup.sh
│   └── seed-demo-data.py            # 预置演示数据
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── CLAUDE.md
├── AGENTS.md
└── README.md
```

### 团队分区说明

| 目录 | 主要负责人 | 说明 |
|---|---|---|
| `backend/agents/` | C | Agent 实现，不动 API |
| `backend/core/` | C | Runtime 核心，与 B 协商 SSE 接口 |
| `backend/tools/` | C | Tool Ecosystem |
| `backend/prompts/` | C | Prompt 版本管理 |
| `backend/api/` | B | FastAPI 路由 |
| `backend/db/` | B | 数据库模型和 CRUD |
| `backend/schemas/` | B + C | **共同维护**，改动需全员确认 |
| `frontend/` | A | 前端全部 |

---

## 5. Agent Runtime 设计

### 5.1 State Schema（backend/core/state.py）

```python
from typing import TypedDict, Optional
from dataclasses import dataclass, field


@dataclass
class ResearchItem:
    title: str
    content: str
    url: str
    source: str
    relevance_score: float = 0.5
    category: str = "general"  # feature|pricing|users|strength|weakness


@dataclass
class SWOTAnalysis:
    strengths: list[str]      # 3-5 条
    weaknesses: list[str]     # 3-5 条
    opportunities: list[str]  # 3-5 条
    threats: list[str]        # 3-5 条


@dataclass
class StructuredAnalysis:
    product_name: str
    product_summary: str
    core_features: list[str]
    pricing: str
    target_users: str
    swot: SWOTAnalysis
    key_insights: list[str]
    citations: list[dict] = field(default_factory=list)


@dataclass
class MetricCards:
    market_size: str
    user_scale: str
    pricing_range: str
    threat_level: int  # 1-5


class AnalysisState(TypedDict):
    # 输入
    task_id: str
    target_product: str
    analysis_dimensions: list[str]

    # Planner 输出
    search_queries: list[str]
    analysis_plan: str

    # Research 输出
    raw_research: list[dict]        # ResearchItem 序列化后
    research_retry_count: int

    # Analysis 输出
    structured_analysis: Optional[dict]
    analysis_retry_count: int

    # Writer 输出
    final_report_markdown: str
    metric_cards: Optional[dict]
    writer_retry_count: int

    # Reviewer 输出
    quality_score: float
    quality_feedback: str
    citations_verified: bool

    # Runtime 状态
    current_agent: str
    execution_logs: list[dict]      # 每个 Agent 步骤的结构化日志
    tool_calls: list[dict]          # Tool 调用记录
    token_usage: dict               # {agent_name: {prompt, completion, total}}
    status: str                     # PENDING/RUNNING/COMPLETED/FAILED
    error: Optional[str]
```

### 5.2 DAG 定义（backend/core/workflow.py）

```python
from langgraph.graph import StateGraph, END
from core.state import AnalysisState
from agents.planner import run_planner
from agents.research import run_research
from agents.analysis import run_analysis
from agents.writer import run_writer
from agents.reviewer import run_reviewer


def should_retry_research(state: AnalysisState) -> str:
    if (len(state["raw_research"]) < 5
            and state["research_retry_count"] < 2):
        return "retry"
    return "continue"


def should_retry_analysis(state: AnalysisState) -> str:
    if (state["structured_analysis"] is None
            and state["analysis_retry_count"] < 1):
        return "retry"
    return "continue"


def should_retry_writer(state: AnalysisState) -> str:
    if (len(state.get("final_report_markdown", "")) < 500
            and state["writer_retry_count"] < 1):
        return "retry"
    return "continue"


def build_dag() -> StateGraph:
    workflow = StateGraph(AnalysisState)

    workflow.add_node("planner",  run_planner)
    workflow.add_node("research", run_research)
    workflow.add_node("analysis", run_analysis)
    workflow.add_node("writer",   run_writer)
    workflow.add_node("reviewer", run_reviewer)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "research")

    workflow.add_conditional_edges(
        "research", should_retry_research,
        {"retry": "research", "continue": "analysis"}
    )
    workflow.add_conditional_edges(
        "analysis", should_retry_analysis,
        {"retry": "analysis", "continue": "writer"}
    )
    workflow.add_conditional_edges(
        "writer", should_retry_writer,
        {"retry": "writer", "continue": "reviewer"}
    )
    workflow.add_edge("reviewer", END)

    return workflow.compile()


compiled_dag = build_dag()
```

### 5.3 Runtime 核心：SSE 队列机制（backend/core/runtime.py）

这是全栈 Python 的关键设计——DAG 和 SSE 在同一进程内，通过 `asyncio.Queue` 通信，消除了 v2.0 中 Agent 服务回调后端的 HTTP 开销。

```python
import asyncio
from datetime import datetime, UTC
from typing import AsyncGenerator
from core.workflow import compiled_dag
from core.state import AnalysisState
from db.crud import create_report, update_task_status, append_execution_log

# task_id → asyncio.Queue
# SSE 路由监听 Queue，DAG 执行时往 Queue 写事件
_sse_queues: dict[str, asyncio.Queue] = {}


def get_or_create_queue(task_id: str) -> asyncio.Queue:
    if task_id not in _sse_queues:
        _sse_queues[task_id] = asyncio.Queue()
    return _sse_queues[task_id]


def cleanup_queue(task_id: str):
    _sse_queues.pop(task_id, None)


async def push_event(task_id: str, event_type: str, data: dict):
    """由 Agent 节点调用，往 SSE 队列推事件"""
    queue = get_or_create_queue(task_id)
    await queue.put({
        "event": event_type,
        "task_id": task_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "data": data,
    })


async def sse_stream(task_id: str) -> AsyncGenerator[str, None]:
    """FastAPI SSE 路由消费此 Generator"""
    queue = get_or_create_queue(task_id)
    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(event)}\n\n"
                if event["event"] in ("task_complete", "task_failed"):
                    break
            except asyncio.TimeoutError:
                yield "data: {\"event\": \"heartbeat\"}\n\n"
    finally:
        cleanup_queue(task_id)


async def run_dag(task_id: str, target_product: str,
                  analysis_dimensions: list[str], db_session):
    """在 BackgroundTask 中执行，整个 DAG 生命周期"""
    initial_state: AnalysisState = {
        "task_id": task_id,
        "target_product": target_product,
        "analysis_dimensions": analysis_dimensions,
        "search_queries": [],
        "analysis_plan": "",
        "raw_research": [],
        "research_retry_count": 0,
        "structured_analysis": None,
        "analysis_retry_count": 0,
        "final_report_markdown": "",
        "metric_cards": None,
        "writer_retry_count": 0,
        "quality_score": 0.0,
        "quality_feedback": "",
        "citations_verified": False,
        "current_agent": "planner",
        "execution_logs": [],
        "tool_calls": [],
        "token_usage": {},
        "status": "RUNNING",
        "error": None,
    }

    await update_task_status(db_session, task_id, "RUNNING")

    try:
        # LangGraph 同步执行，在线程池中跑避免阻塞事件循环
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: compiled_dag.invoke(
                initial_state,
                config={"callbacks": [SSECallbackHandler(task_id)]}
            )
        )
        # 保存报告
        report = await create_report(db_session, task_id, result)
        await update_task_status(db_session, task_id, "COMPLETED")
        await push_event(task_id, "task_complete", {
            "report_id": report.id,
            "quality_score": result.get("quality_score", 0),
        })

    except Exception as e:
        await update_task_status(db_session, task_id, "FAILED", error=str(e))
        await push_event(task_id, "task_failed", {"error": str(e)})
```

### 5.4 各 Agent 节点（以 Research Agent 为例）

```python
# backend/agents/research.py
import asyncio
from core.state import AnalysisState
from core.runtime import push_event
from tools.registry import ToolRouter


def run_research(state: AnalysisState) -> dict:
    """LangGraph 节点函数（同步，在线程池中运行）"""
    task_id = state["task_id"]
    retry_count = state["research_retry_count"]

    # 同步方式推 SSE 事件（线程池中无法直接 await）
    _sync_push(task_id, "agent_start", {
        "agent": "research",
        "message": f"正在搜索竞品信息... (第{retry_count + 1}次)",
    })

    router = ToolRouter(task_id, state)
    all_items = []

    for query in state["search_queries"]:
        items = router.call_sync("tavily_search", query=query, max_results=5)
        all_items.extend(items)

    _sync_push(task_id, "agent_complete", {
        "agent": "research",
        "summary": f"采集到 {len(all_items)} 条信息",
    })

    return {
        "raw_research": [item.__dict__ for item in all_items],
        "research_retry_count": retry_count + 1,
        "execution_logs": state["execution_logs"] + [{
            "agent": "research",
            "items_count": len(all_items),
            "timestamp": datetime.utcnow().isoformat(),
        }],
        "tool_calls": state["tool_calls"] + router.get_call_log(),
    }


def _sync_push(task_id: str, event_type: str, data: dict):
    """在线程池中同步推送 SSE 事件"""
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(
        push_event(task_id, event_type, data), loop
    )
```

---

## 6. Tool Ecosystem Layer

### 6.1 Tool Registry（backend/tools/registry.py）

```python
import time
from datetime import datetime

TOOL_REGISTRY = {
    "tavily_search": {
        "description": "Real-time web search optimized for AI",
        "requires_key": "TAVILY_API_KEY",
        "timeout_seconds": 15,
        "retry_on_fail": True,
    },
    "firecrawl_scrape": {
        "description": "Extract structured content from URLs",
        "requires_key": "FIRECRAWL_API_KEY",
        "timeout_seconds": 30,
        "retry_on_fail": True,
    },
}


class ToolRouter:
    def __init__(self, task_id: str, state: dict):
        self.task_id = task_id
        self.state = state
        self._call_log = []

    def call_sync(self, tool_name: str, **kwargs) -> any:
        start = time.time()
        try:
            if tool_name == "tavily_search":
                from tools.tavily_search import tavily_search_sync
                result = tavily_search_sync(**kwargs)
            elif tool_name == "firecrawl_scrape":
                from tools.firecrawl import firecrawl_scrape_sync
                result = firecrawl_scrape_sync(**kwargs)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            latency_ms = int((time.time() - start) * 1000)
            self._call_log.append({
                "tool": tool_name,
                "input": kwargs,
                "output_summary": str(result)[:200],
                "latency_ms": latency_ms,
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
            })
            _sync_push(self.task_id, "tool_result", {
                "tool": tool_name,
                "success": True,
                "latency_ms": latency_ms,
                "result_summary": f"返回 {len(result) if hasattr(result, '__len__') else 1} 条结果",
            })
            return result

        except Exception as e:
            self._call_log.append({
                "tool": tool_name,
                "input": kwargs,
                "error": str(e),
                "success": False,
                "timestamp": datetime.utcnow().isoformat(),
            })
            raise

    def get_call_log(self) -> list:
        return self._call_log
```

---

## 7. 数据库设计（SQLAlchemy + Alembic）

### 7.1 ORM 模型（backend/db/models.py）

```python
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer,
    DateTime, JSON, Enum as SAEnum
)
from sqlalchemy.orm import DeclarativeBase
import enum


class Base(DeclarativeBase):
    pass


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Task(Base):
    __tablename__ = "tasks"

    id                  = Column(String, primary_key=True)  # cuid / uuid
    target_product      = Column(String, nullable=False)
    analysis_dimensions = Column(JSON, default=list)
    status              = Column(SAEnum(TaskStatus), default=TaskStatus.PENDING)
    created_at          = Column(DateTime, default=datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at          = Column(DateTime, nullable=True)
    completed_at        = Column(DateTime, nullable=True)
    error               = Column(Text, nullable=True)


class Report(Base):
    __tablename__ = "reports"

    id               = Column(String, primary_key=True)
    task_id          = Column(String, nullable=False, unique=True)

    markdown_content = Column(Text, nullable=False)
    structured_data  = Column(JSON)      # StructuredAnalysis dict
    metric_cards     = Column(JSON)      # MetricCards dict

    quality_score    = Column(Float, nullable=True)
    quality_feedback = Column(Text, nullable=True)
    citations_data   = Column(JSON)      # [{text, url, agent}]
    token_usage      = Column(JSON)      # {agent_name: {prompt, completion}}

    created_at       = Column(DateTime, default=datetime.utcnow)


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    task_id     = Column(String, nullable=False, index=True)

    agent_name  = Column(String, nullable=False)
    event_type  = Column(String, nullable=False)  # agent_start/complete/tool_call/error
    data        = Column(JSON)
    timestamp   = Column(DateTime, default=datetime.utcnow)
    duration_ms = Column(Integer, nullable=True)
```

### 7.2 数据库连接（backend/db/database.py）

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import settings

engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """FastAPI 依赖注入"""
    async with AsyncSessionLocal() as session:
        yield session
```

### 7.3 Alembic 初始化

```bash
cd backend
alembic init alembic
# 修改 alembic/env.py 导入 models.Base
alembic revision --autogenerate -m "init"
alembic upgrade head
```

---

## 8. FastAPI 后端设计

### 8.1 应用入口（backend/main.py）

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import tasks, reports, traces, events
from db.database import engine
from db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时建表（开发环境；生产用 alembic）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="CompeteScope API",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router,   prefix="/api/tasks",   tags=["tasks"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(traces.router,  prefix="/api/traces",  tags=["traces"])
app.include_router(events.router,  prefix="/api",         tags=["sse"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "compete-scope-api"}
```

### 8.2 Tasks 路由（backend/api/routes/tasks.py）

```python
import uuid
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db.crud import create_task, get_task, list_tasks
from schemas.task import TaskCreateRequest, TaskResponse, TaskListResponse
from core.runtime import run_dag

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=201)
async def create_analysis_task(
    body: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    task_id = str(uuid.uuid4())
    task = await create_task(db, task_id, body.target_product, body.analysis_dimensions)

    # 异步触发 DAG，立即返回 task_id
    background_tasks.add_task(
        run_dag,
        task_id=task_id,
        target_product=body.target_product,
        analysis_dimensions=body.analysis_dimensions,
        db_session=db,
    )

    return TaskResponse.model_validate(task)


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    tasks, total = await list_tasks(db, page=page, page_size=page_size)
    return TaskListResponse(items=tasks, total=total, page=page, page_size=page_size)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_detail(task_id: str, db: AsyncSession = Depends(get_db)):
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.post("/{task_id}/retry")
async def retry_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    task = await get_task(db, task_id)
    if not task or task.status not in ("FAILED",):
        raise HTTPException(status_code=400, detail="Only FAILED tasks can be retried")
    background_tasks.add_task(run_dag, task_id=task_id,
                              target_product=task.target_product,
                              analysis_dimensions=task.analysis_dimensions,
                              db_session=db)
    return {"message": "Retry started"}
```

### 8.3 SSE 路由（backend/api/routes/events.py）

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from core.runtime import sse_stream, get_or_create_queue

router = APIRouter()


@router.get("/tasks/{task_id}/events")
async def task_events(task_id: str):
    """SSE 端点，前端用 EventSource 连接"""
    return StreamingResponse(
        sse_stream(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # 关闭 nginx 缓冲
        },
    )
```

### 8.4 Pydantic Schemas（backend/schemas/task.py）

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from db.models import TaskStatus


class TaskCreateRequest(BaseModel):
    target_product: str
    analysis_dimensions: list[str] = ["功能", "定价", "用户定位", "SWOT"]
    my_product: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    target_product: str
    analysis_dimensions: list[str]
    status: TaskStatus
    created_at: datetime
    completed_at: Optional[datetime]
    error: Optional[str]

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
```

### 8.5 统一响应格式（所有接口）

```python
# 所有接口遵循此格式
{
    "success": true,
    "data": { ... },      # 实际数据
    "error": null         # 失败时填错误信息
}
```

---

## 9. SSE 事件协议

> 完整版见 `docs/sse-events.md`。
> Python 定义在 `backend/schemas/events.py`，前端类型在 `frontend/types/sse-events.ts`。
> **两处必须严格对齐，修改需全员确认。**

```typescript
// frontend/types/sse-events.ts

type AgentName = 'planner' | 'research' | 'analysis' | 'writer' | 'reviewer';

type SSEEventType =
  | 'task_start'
  | 'agent_start'
  | 'agent_complete'
  | 'tool_call'
  | 'tool_result'
  | 'task_complete'
  | 'task_failed'
  | 'heartbeat';

interface BaseSSEEvent {
  event: SSEEventType;
  task_id: string;
  timestamp: string;
}

interface AgentStartEvent extends BaseSSEEvent {
  event: 'agent_start';
  data: { agent: AgentName; message: string; };
}

interface AgentCompleteEvent extends BaseSSEEvent {
  event: 'agent_complete';
  data: {
    agent: AgentName;
    duration_ms: number;
    summary: string;
    token_usage?: { prompt: number; completion: number; };
  };
}

interface ToolCallEvent extends BaseSSEEvent {
  event: 'tool_call';
  data: { tool: string; input: Record<string, unknown>; call_id: string; };
}

interface ToolResultEvent extends BaseSSEEvent {
  event: 'tool_result';
  data: {
    call_id: string;
    tool: string;
    success: boolean;
    result_summary: string;
    latency_ms: number;
  };
}

interface TaskCompleteEvent extends BaseSSEEvent {
  event: 'task_complete';
  data: {
    report_id: string;
    quality_score: number;
    total_duration_ms: number;
    total_tokens: number;
  };
}

interface TaskFailedEvent extends BaseSSEEvent {
  event: 'task_failed';
  data: { error: string; };
}

type SSEEvent =
  | AgentStartEvent | AgentCompleteEvent
  | ToolCallEvent | ToolResultEvent
  | TaskCompleteEvent | TaskFailedEvent;
```

---

## 10. Prompt 管理结构

> 所有 Prompt 文件在 `backend/prompts/{agent}/v{N}.txt`，版本化管理。
> 修改必须更新 `AGENTS.md` 版本表，并运行三标准案例回归测试。

### 10.1 Planner Prompt (backend/prompts/planner/v1.txt)

```
你是专业的竞品调研策略师。

目标产品：【{target_product}】
分析维度：【{analysis_dimensions}】

生成 3-5 个高质量搜索词，覆盖：产品官网/功能介绍、用户评测/社区讨论、定价策略、竞品对比、最新动态（2024-2025）。

要求：
- 搜索词必须具体，不只是产品名
- 包含年份词确保时效性
- 同时生成中英文搜索词
- 只输出 JSON，不包含任何其他内容

输出格式：
{"search_queries": ["搜索词1", ...], "analysis_plan": "50字以内的分析计划"}
```

### 10.2 Research Prompt (backend/prompts/research/v1.txt)

```
你是专业竞品调研专家。目标产品：【{target_product}】

以下是搜索结果原始数据：
{raw_search_results}

从中提炼 5-8 条最有价值的信息，每条标注来源 URL。
聚焦：产品定位、核心功能、定价、目标用户、优劣势。

只输出 JSON：
{"research_items": [{"title":"","content":"100字内","url":"","category":"feature|pricing|users|strength|weakness","relevance":0.9}]}
```

### 10.3 Analysis Prompt (backend/prompts/analysis/v1.txt)

```
你是战略分析师。基于以下竞品调研数据生成结构化分析：
{raw_research_json}

{my_product_context}

要求：SWOT 每项 3-5 条（每条 30 字内），core_features 5-8 个，key_insights 3 条战略洞察。
只输出 JSON，字段名必须是英文 snake_case：

{"product_name":"","product_summary":"","core_features":[],"pricing":"","target_users":"","swot":{"strengths":[],"weaknesses":[],"opportunities":[],"threats":[]},"key_insights":[],"citations":[{"text":"","url":"","agent":"analysis"}]}
```

### 10.4 Writer Prompt (backend/prompts/writer/v1.txt)

```
你是专业报告撰写者。将以下结构化分析转为 Markdown 报告：
{structured_analysis_json}

报告结构（严格按顺序）：
## 执行摘要（3句话）
## 产品概况
## 核心功能分析
## SWOT 分析
## 市场机会与威胁
## 建议行动（3-5条）

要求：每节不超过 200 字，语言简洁专业。

报告末尾必须输出（不要省略）：
<!-- METRICS_JSON: {"market_size":"","user_scale":"","pricing_range":"","threat_level":3} -->
```

### 10.5 Reviewer Prompt (backend/prompts/reviewer/v1.txt)

```
你是报告质量审核员。评估以下竞品分析报告：
{report_markdown}

评分维度（总分 1.0）：
- 信息完整性 0.3（功能/定价/用户/SWOT 是否齐全）
- 结构清晰度 0.3（章节清晰，逻辑通顺）
- 洞察价值 0.2（有无真正有价值的战略洞察）
- Citation 覆盖 0.2（关键结论是否有来源）

只输出 JSON：
{"quality_score":0.85,"quality_feedback":"优点：...不足：...","citations_verified":true,"suggestions":[]}
```

---

## 11. 前端页面架构（AI Native Workspace）

### 11.1 页面路由

```
/               → redirect → /(workspace)
/(workspace)    → Task Dashboard（任务列表 + 快速创建入口）
/tasks/new      → 创建新分析任务
/tasks/[id]     → 任务执行详情（DAGVisualizer + 实时日志）
/reports/[id]   → 报告详情（Markdown + SWOT + 指标卡片 + Citation）
/traces/[id]    → Agent Trace 详情（Tool Calls + Token 消耗 + Timeline）
/monitor        → Runtime Monitor（运行中任务 + 系统健康状态）
```

### 11.2 API 客户端（frontend/lib/api.ts）

```typescript
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const json = await res.json();
  if (!json.success) throw new Error(json.error ?? "Unknown error");
  return json.data as T;
}

export const api = {
  createTask: (body: TaskCreateRequest) =>
    request<TaskResponse>("/tasks", { method: "POST", body: JSON.stringify(body) }),
  getTasks: (page = 1) =>
    request<TaskListResponse>(`/tasks?page=${page}`),
  getTask: (id: string) =>
    request<TaskResponse>(`/tasks/${id}`),
  getReport: (id: string) =>
    request<ReportResponse>(`/reports/${id}`),
  getTrace: (taskId: string) =>
    request<TraceResponse>(`/traces/${taskId}`),
  retryTask: (id: string) =>
    request(`/tasks/${id}/retry`, { method: "POST" }),
};
```

### 11.3 useSSE Hook（frontend/hooks/useSSE.ts）

```typescript
import { useState, useEffect, useRef } from "react";
import type { SSEEvent, AgentName } from "@/types/sse-events";

type AgentStatus = "waiting" | "running" | "completed" | "failed";

interface AgentState {
  status: AgentStatus;
  startTime?: string;
  endTime?: string;
  durationMs?: number;
  summary?: string;
  tokenUsage?: { prompt: number; completion: number };
}

const AGENTS: AgentName[] = ["planner", "research", "analysis", "writer", "reviewer"];

export function useSSE(taskId: string | null) {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [agentStates, setAgentStates] = useState<Record<AgentName, AgentState>>(
    () => Object.fromEntries(AGENTS.map(a => [a, { status: "waiting" }])) as any
  );
  const [isComplete, setIsComplete] = useState(false);
  const [isFailed, setIsFailed] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!taskId) return;
    const es = new EventSource(
      `${process.env.NEXT_PUBLIC_API_URL}/tasks/${taskId}/events`
    );
    esRef.current = es;

    es.onmessage = (e) => {
      const event = JSON.parse(e.data) as SSEEvent;
      setEvents(prev => [...prev, event]);

      if (event.event === "agent_start") {
        setAgentStates(prev => ({
          ...prev,
          [event.data.agent]: { status: "running", startTime: event.timestamp },
        }));
      } else if (event.event === "agent_complete") {
        setAgentStates(prev => ({
          ...prev,
          [event.data.agent]: {
            status: "completed",
            endTime: event.timestamp,
            durationMs: event.data.duration_ms,
            summary: event.data.summary,
            tokenUsage: event.data.token_usage,
          },
        }));
      } else if (event.event === "task_complete") {
        setIsComplete(true);
        es.close();
      } else if (event.event === "task_failed") {
        setIsFailed(true);
        es.close();
      }
    };

    es.onerror = () => es.close();
    return () => es.close();
  }, [taskId]);

  return { events, agentStates, isComplete, isFailed };
}
```

### 11.4 DAGVisualizer 组件规划

```tsx
// frontend/components/dag/DAGVisualizer.tsx
// 五节点线性 DAG，用 SVG + CSS 手绘，不引入 React Flow
// 节点状态颜色：
//   waiting:   border-slate-600, text-slate-500
//   running:   border-blue-400, text-blue-400, animate-pulse
//   completed: border-green-500, text-green-400, ✓ 图标
//   failed:    border-red-500, text-red-400, ✗ 图标
// 节点间连接线：根据状态变色

const AGENT_LABELS: Record<AgentName, string> = {
  planner:  "📋 Planner\n分解目标",
  research: "🔍 Research\n搜索采集",
  analysis: "📊 Analysis\nSWOT分析",
  writer:   "✍️ Writer\n报告生成",
  reviewer: "✅ Reviewer\n质量审核",
};
```

### 11.5 UI 设计规范

```
主题：深色 B 端工作台

颜色：
  背景：     #0f1117
  卡片：     #1a1d2e
  边框：     #2d3148
  主色：     #6366f1 (Indigo)
  成功：     #22c55e
  警告：     #f59e0b
  危险：     #ef4444
  文字主：   #e2e8f0
  文字次：   #94a3b8

Agent 颜色：
  planner:  #3b82f6 (blue)
  research: #f59e0b (amber)
  analysis: #8b5cf6 (violet)
  writer:   #22c55e (green)
  reviewer: #64748b (slate)
```

---

## 12. Observability 架构

### 12.1 自建轻量 Observability（MVP）

不引入 LangSmith / Langfuse（避免依赖过重拖累工期），用 PostgreSQL `execution_logs` 表 + 前端 Trace 页实现。

收集的数据：
- 每个 Agent 的开始/结束时间 + 耗时
- 每个 Tool Call 的输入/输出/耗时/是否成功
- 每次 LLM 调用的 Token 消耗（prompt + completion）
- 重试次数和原因
- 最终质量评分

展示位置：
- `/traces/[id]`：完整 Trace 详情
- `/monitor`：运行中任务实时状态
- 报告页底部：Token 消耗汇总卡片

### 12.2 Langfuse 接入（P1 阶段）

```python
# backend/config.py 中控制开关
ENABLE_LANGFUSE = os.getenv("ENABLE_LANGFUSE", "false") == "true"

# backend/core/runtime.py 中条件启用
if settings.ENABLE_LANGFUSE:
    from langfuse.callback import CallbackHandler
    langfuse_handler = CallbackHandler(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
    )
    config["callbacks"] = [langfuse_handler]
```

---

## 13. MVP 功能边界与优先级

### P0：必须完成（没有就无法演示）

- [ ] 任务创建：输入产品名 + 分析维度
- [ ] 五节点 LangGraph DAG 跑通（Planner → Research → Analysis → Writer → Reviewer）
- [ ] Tavily Search 真实搜索
- [ ] FastAPI SSE 实时进度推送
- [ ] DAGVisualizer：五节点状态可视化
- [ ] 报告页：Markdown 渲染 + SWOT 四象限 + MetricCards
- [ ] 任务列表页
- [ ] PostgreSQL 数据持久化

### P1：加分项（有时间就做）

- [ ] Agent Trace 详情页（Tool Calls + Token 消耗柱状图）
- [ ] Firecrawl 网页抓取
- [ ] Citation 来源面板
- [ ] 任务失败重试按钮
- [ ] Runtime Monitor 页面
- [ ] Agent Timeline 可视化
- [ ] Langfuse 集成

### P2：二期（演示中提到即可）

- [ ] Qdrant 向量知识库
- [ ] PDF 导出
- [ ] 用户登录 / RBAC
- [ ] 多模型对比

### Mock 策略

| 功能 | Mock 方案 |
|---|---|
| Human-in-the-loop | Reviewer Agent 自动放行，前端展示"审查"节点装饰 |
| Knowledge Base 页 | 静态 UI + 预置几条固定记录 |
| 多 Agent 并行 | DAG 图展示并行箭头，实际串行 |
| Evaluation 历史 | quality_score 字段渲染折线图 |

---

## 14. 20 天每日开发计划

### Week 1：核心 Pipeline 跑通

| Day | C（Agent/架构） | A（前端） | B（后端/联调） |
|---|---|---|---|
| 1 | Monorepo 初始化 + Python 虚拟环境 + LangGraph 安装 + State Schema 定义（state.py）+ DAG 骨架 | Next.js 初始化 + Tailwind + Shadcn + WorkspaceLayout + 路由结构 | FastAPI 初始化 + SQLAlchemy + Alembic + Task/Report/ExecutionLog 表建立 |
| 2 | Planner + Research Agent 实现 + Tavily 集成 + 单节点 CLI 测试 | Dashboard 骨架 + TaskCard 组件 + Sidebar 导航 | Task CRUD（create/get/list）+ Pydantic Schemas + 统一响应格式 |
| 3 | Analysis Agent + Planner→Research→Analysis 三节点 DAG 联调 | 任务创建表单 + 提交逻辑 + 表单验证 | BackgroundTasks 接入 DAG + asyncio Queue SSE 基础框架 |
| 4 | Writer + Reviewer Agent + **五节点完整 DAG CLI 端到端测试**（python test_pipeline.py "Notion"）| 任务详情页骨架 + DAGVisualizer 静态版（手绘五节点）+ Markdown 渲染组件 | SSE StreamingResponse 实现 + 事件推送测试 |
| 5 | 封装 run_dag() + 错误处理 + push_event() 回调完善 | useSSE hook + 接入真实 SSE + DAGVisualizer 动态状态更新 | 前后端联调第一轮（Postman 创建任务 → SSE 事件正常推送）|
| 6 | Prompt 优化（JSON 输出稳定性）+ 重试逻辑验证 | 报告页基础版（Markdown + SWOT 四象限 CSS）+ 加载 / 错误状态 | 联调第二轮：浏览器走完全流程 + ExecutionLog 写入验证 |
| 7 | **全流程演示验收（Notion 案例）+ 记录 Top5 问题** | 同左 | 同左 |

### Week 2：企业级特性增强

| Day | C | A | B |
|---|---|---|---|
| 8 | Tool Registry 完善 + Firecrawl 集成 + Research 质量提升 | MetricCards 组件 + 报告样式精修 + 进度条动画 | 任务历史 API + ExecutionLog 查询接口 |
| 9 | Citation 绑定逻辑（Reviewer Agent 增强）| Agent Trace 页 + ToolCallCard + TokenUsageBar | 报告 JSONB 查询 + Trace 数据 API |
| 10 | token_usage 统计完善 + Agent Timeline 数据输出 | AgentTimeline 组件 + 实时执行日志展示 | SSE 所有事件类型联调 |
| 11 | 超时处理 + 指数退避重试 + 异常兜底 | 失败状态页 + 重试按钮 + 空状态页 | 健康检查 + 异常日志告警 |
| 12 | Prompt 最终优化 + 三标准案例质量对齐 | Runtime Monitor 页 + CitationPanel | 查询缓存 + 性能优化 |
| 13 | AGENTS.md 更新 + 回归测试全通过 | 整体视觉统一 + 移动端基础适配 | 全流程压测 + Bug 修复 |
| 14 | **第二周验收 + Demo 流程录制 v1** | 同左 | 同左 |

### Week 3：Demo 冲刺

| Day | C | A | B |
|---|---|---|---|
| 15 | 三个标准案例 Prompt 微调（Notion / Linear / Figma）| 演示模式优化 + 首页介绍文案 | 演示环境数据预置 + seed 脚本 |
| 16 | 生产环境配置 + API Key 管理 | 生产构建 + 静态优化 | docker-compose.prod.yml + 部署测试 |
| 17 | 架构文档 + Agent 设计思路 | 用户操作文档 + 截图集 | README + 部署文档 + FAQ |
| 18 | **全员回归测试 + 边界 Case + Bug 清零** | | |
| 19 | **演示彩排（计时 6 分钟）+ 讲解词 + 应急预案演练** | | |
| 20 | **最终环境确认 + main 封版 + 庆祝 🎉** | | |

---

## 15. 团队协作规范

### 15.1 分支策略

```
main  ←  只有演示稳定版，不能坏
  └── dev  ←  每日集成，下班前合入
        ├── feat/agent-xxx    C 的分支
        ├── feat/web-xxx      A 的分支
        └── feat/api-xxx      B 的分支
```

### 15.2 Commit 规范

```bash
feat(agent): 实现 Research Agent Tavily 搜索集成
feat(web):   完成 DAGVisualizer 动态状态展示
feat(api):   实现 SSE StreamingResponse 事件推送
fix(agent):  修复 JSON 解析失败未触发重试的 Bug
prompt(agent): research v2 增加多关键词搜索策略
chore(db):   添加 ExecutionLog 表 Alembic Migration
test(agent): 添加 Notion 案例端到端回归测试
```

类型：`feat` `fix` `chore` `docs` `test` `refactor` `prompt` `perf`

### 15.3 共享文件变更规则（必须通知全队）

| 文件 | 负责人 | 影响方 |
|---|---|---|
| `backend/core/state.py` | C | B（DB 存储结构）、A（前端类型） |
| `backend/schemas/events.py` | B+C | A（SSE 消费端） |
| `frontend/types/sse-events.ts` | A | 需与 backend/schemas/events.py 对齐 |
| `docs/api-contract.md` | B | A（API 调用） |
| `backend/prompts/*/v*.txt` | C | 需运行三案例回归测试 |
| `backend/db/models.py` | B | C（数据写入）、A（查询字段） |

### 15.4 关键里程碑

| 里程碑 | 验收标准 | 日期 |
|---|---|---|
| 三服务独立启动 | Hello World 跑通 | Day 1 结束 |
| CLI 端到端出报告 | `python -m pytest tests/test_pipeline.py` | Day 4 结束 |
| API 触发完整流程 | Postman → 报告写入 DB | Day 5 结束 |
| 浏览器走完全流程 | 虽然丑但能用 | Day 6 结束 |
| 标准案例 100% 通过 | Notion + Linear + Figma | Day 15 |

---

## 16. Docker 部署结构

### 16.1 开发环境（docker-compose.yml）

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: compete_scope
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  # 开发阶段：只 Docker 跑 PostgreSQL
  # backend 和 frontend 本地跑，便于热重载和调试

volumes:
  postgres_data:
```

### 16.2 生产环境（docker-compose.prod.yml）

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      TAVILY_API_KEY: ${TAVILY_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000/api
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 16.3 Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN alembic upgrade head

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 17. 环境变量完整清单

```bash
# .env.example（提交到 git，不含真实 key）

# ========= 数据库 =========
DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/compete_scope"
POSTGRES_DB="compete_scope"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="password"

# ========= AI 模型 =========
DEEPSEEK_API_KEY="sk-请填入"
LLM_MODEL="deepseek-chat"
LLM_MAX_TOKENS="3000"
LLM_TEMPERATURE="0.3"
LLM_TIMEOUT_SECONDS="90"

# ========= 搜索工具 =========
TAVILY_API_KEY="tvly-请填入"
FIRECRAWL_API_KEY="fc-请填入（P1 阶段）"

# ========= 服务地址 =========
NEXT_PUBLIC_API_URL="http://localhost:8000/api"

# ========= 功能开关 =========
ENABLE_FIRECRAWL="false"
ENABLE_LANGFUSE="false"
DEBUG="true"

# ========= Observability（P1） =========
LANGFUSE_PUBLIC_KEY="pk-请填入（P1 阶段）"
LANGFUSE_SECRET_KEY="sk-请填入（P1 阶段）"
```

---

## 18. Demo 演示路线

### 18.1 演示脚本（6 分钟）

```
0:00 - 1:00  问题陈述
  "传统竞品分析要半天。我们做到 10 分钟。
   不是普通 AI 对话，是 Multi-Agent 协同的企业级调研工作台。"

1:00 - 1:30  现场输入（不要提前填好）
  → /tasks/new → 输入 "Notion" → 勾选分析维度 → 点击开始

1:30 - 4:00  实时 Agent 执行（最抓眼球）
  → 切到 /tasks/{id}
  → DAGVisualizer 逐节点点亮（每个 Agent 亮起来有动画）
  → 展示 Tool Call 卡片："正在搜索 Notion vs Obsidian 2024..."
  → 口述每个 Agent 在做什么

4:00 - 5:30  报告展示
  → 自动跳转 /reports/{id}
  → SWOT 四象限
  → MetricCards（市场规模 / 威胁等级）
  → Citation 面板：每条结论有来源链接
  → 切到 /traces/{id}：Token 消耗 + Tool Call 记录

5:30 - 6:00  技术总结
  → "真正的 LangGraph DAG，不是假的"
  → 架构图快速过：五 Agent + Tool Registry + SSE + Observability
```

### 18.2 标准演示案例

| 案例 | 理由 |
|---|---|
| Notion vs Obsidian | 资料多，SWOT 对比明显，报告质量高 |
| Linear vs Jira | 企业感强，技术评委熟悉 |
| Figma vs Sketch | 设计工具，视觉好看 |

### 18.3 评委高频问题

| 问题 | 回答要点 |
|---|---|
| "和直接问 ChatGPT 有什么区别？" | 真实搜索（不是记忆）+ DAG 自主执行 + 结构化输出 + Citation + Observability |
| "为什么用 LangGraph？" | DAG 状态管理 + 条件边重试 + 节点间 State 共享 + 可扩展编排 |
| "后端为什么选 FastAPI？" | 全栈 Python 一致，async 原生支持 SSE，与 LangGraph 零摩擦集成 |
| "如何保证报告质量？" | Reviewer Agent 评分 + Citation 验证 + 阈值门控重试 |

---

## 19. 风险控制与应急方案

### 19.1 主要风险

| 风险 | 概率 | 对策 |
|---|---|---|
| Tavily 配额耗尽 | 中 | 演示前检查余额，备用账号 |
| Deepseek API 不稳定 | 低 | 备用：切换 OpenAI 兼容接口（LiteLLM 统一层）|
| LLM 输出 JSON 解析失败 | 中 | safe_parse_json() + 重试机制 |
| asyncio Queue 内存泄漏 | 低 | cleanup_queue() 在 SSE 流结束时调用 |
| SSE 连接中断 | 低 | 前端 EventSource 自动重连 |
| 演示现场网络问题 | 低 | 预置离线演示数据 |

### 19.2 应急预案

```
Level 1（轻度）：API 偶尔慢
  → 切到预缓存的 "Notion" 案例（提前存入 DB）

Level 2（中度）：API 不可用
  → 演示模式：前端展示预置好的完整报告
  → 说："这是我们昨晚跑好的结果，展示核心功能"

Level 3（严重）：整个系统挂了
  → 播放录制好的演示视频
  → 重点讲架构设计和技术亮点
```

### 19.3 代码质量底线

每天结束前：
- `dev` 分支三个服务必须可以正常启动
- 不往 `dev` 合入导致他人无法启动的代码
- Prompt 修改必须通过 Notion / Linear / Figma 三案例

---

## 附录 A：requirements.txt

```txt
# backend/requirements.txt

# Web 框架
fastapi==0.111.0
uvicorn[standard]==0.30.0

# 数据库
sqlalchemy[asyncio]==2.0.30
asyncpg==0.29.0
alembic==1.13.1

# Agent 框架
langgraph==0.1.19
langchain==0.2.5
langchain-community==0.2.5

# LLM
langchain-openai==0.1.8   # Deepseek 兼容 OpenAI 接口

# 工具
tavily-python==0.3.3
firecrawl-py==0.0.16       # P1 阶段使用

# 工具库
pydantic==2.7.1
pydantic-settings==2.3.0
python-dotenv==1.0.1
httpx==0.27.0

# 可选（P1）
langfuse==2.30.0
```

---

## 附录 B：CLAUDE.md（AI 工具开发上下文）

```markdown
# CLAUDE.md

## 项目概述
CompeteScope：企业级 AI 竞品分析 Agent 平台
全栈 Python 后端（FastAPI + LangGraph）+ Next.js 前端

## 技术栈
- backend/: Python 3.11 + FastAPI + LangGraph + SQLAlchemy async + PostgreSQL
- frontend/: Next.js 14 + TypeScript + TailwindCSS + Shadcn UI

## 关键文件
- Agent State:   backend/core/state.py      ⚠️ 改动需全员确认
- DAG 定义:      backend/core/workflow.py
- Runtime:       backend/core/runtime.py    SSE Queue 在这里
- Tool Registry: backend/tools/registry.py
- SSE 事件类型:  backend/schemas/events.py  ⚠️ 与前端 types/sse-events.ts 对齐
- API 路由:      backend/api/routes/
- DB 模型:       backend/db/models.py
- Prompts:       backend/prompts/{agent}/v{N}.txt

## 编码规范
### Python
- 所有数据结构用 TypedDict 或 dataclass 定义
- LLM 调用必须有 timeout 和 safe_parse_json()
- 每个 Agent 节点向 state["execution_logs"] 追加日志
- Prompt 文件命名：v1.txt / v2.txt（不覆盖旧版本）
- JSON 结构化输出的 temperature <= 0.3
- 字段名必须是英文 snake_case

### TypeScript
- 严格模式
- API 响应统一格式：{ success, data, error }
- SSE 事件类型与 backend/schemas/events.py 严格对齐

## 接口文档
- API 契约: docs/api-contract.md
- SSE 事件: docs/sse-events.md
- Agent State: docs/agent-state.md
```

---

## 附录 C：第一天每人的第一步

### C（Agent/架构）

```bash
mkdir -p compete-scope/backend/{agents,core,tools,prompts/{planner,research,analysis,writer,reviewer},tests}
cd compete-scope/backend
python -m venv .venv && source .venv/bin/activate
pip install langgraph langchain-community langchain-openai tavily-python fastapi uvicorn sqlalchemy asyncpg alembic pydantic-settings

# 创建 core/state.py（参考 Section 5.1）
# 创建 core/workflow.py（参考 Section 5.2）
# 验证：python -c "from core.workflow import compiled_dag; print('DAG OK')"
```

### A（前端）

```bash
mkdir -p compete-scope/frontend
cd compete-scope/frontend
npx create-next-app@latest . --typescript --tailwind --app
npx shadcn-ui@latest init
pnpm add react-markdown rehype-highlight

# 创建 WorkspaceLayout（深色 B 端布局，参考 Section 11.5）
# 创建路由结构（参考 Section 11.1）
# 创建 useSSE hook 骨架（参考 Section 11.3）
```

### B（后端/联调）

```bash
cd compete-scope/backend

# 创建 db/models.py（参考 Section 7.1）
# 创建 db/database.py（参考 Section 7.2）
# 创建 main.py（参考 Section 8.1）
# 创建 api/routes/tasks.py 骨架

alembic init alembic
# 修改 alembic/env.py 导入 Base
alembic revision --autogenerate -m "init"
alembic upgrade head

uvicorn main:app --reload --port 8000
# 验证：curl http://localhost:8000/api/health
```

---

*文档版本：v3.0（全 Python 后端）*
*项目：CompeteScope*
*原则：完成比完美重要。Day 4 必须有 CLI 端到端流程，浏览器流程 Day 6 跑通。*


# TODO：

## 1. 核心架构缺陷：多并发下的性能灾难

### ❌ 隐患：BackgroundTasks + 线程池会锁死服务

文档在 5.3 和 8.2 中使用 FastAPI 的 `BackgroundTasks` 在主进程中直接通过 `run_in_executor`（线程池）启动 LangGraph DAG。

- **后果**：AI Agent 的任务属于 **长耗时（Long-running）、高延迟（10 分钟）** 的重度任务。如果有 5 个用户同时提交任务，FastAPI 的工作线程/线程池会瞬间被占满，导致整个后端的 REST API（如路由 `/api/tasks`、健康检查 `/health`）全部卡死、超时。
    
- **企业级标准**：必须**计算与 API 解耦**。使用分布式任务队列（如 **Celery** 或 **Redis Queue / RQ**）。 Fastapi 只负责投递任务到 Redis，由独立的 Worker 进程去跑 LangGraph DAG。
    

### ❌ 隐患：内存级 SSE 队列（`_sse_queues`）导致单点故障与无法水平扩展

后端用 `_sse_queues: dict[str, asyncio.Queue] = {}` 将事件存放在进程内存中。

- **后果**：
    
    1. 如果后端实例因为任何原因重启，所有正在运行的任务的前端 SSE 连接全部断开，事件丢失。
        
    2. 无法做到企业级的水平扩展（Scale Out）。如果部署了 2 个后台实例（Workers），用户连接的是实例 A 的 SSE，但 LangGraph 任务可能在实例 B 上运行，实例 A 的内存队列里根本没有事件，前端会一直白屏等待。
        
- **企业级标准**：使用 **Redis Pub/Sub（发布订阅）** 作为进程间的事件总线。Agent 将事件 `PUBLISH` 到 Redis，FastAPI 路由从 Redis `SUBSCRIBE` 并推送到 SSE。
    

## 2. Agent 鲁棒性与 LLM 滥用风险

### ❌ 隐患：条件边重试（Conditional Edges）容易陷入死循环或 Token 暴风雨

在 5.2 的 DAG 定义中，如果 Research 采集到的信息不够，或者 Analysis 的 JSON 解析失败，会直接连回原节点重试。

- **后果**：如果某款产品在网上确实没有任何资料，或者 LLM 持续遭遇格式 Bug，这个 DAG 会变成死循环，或者在短时间内疯狂调用 LLM，**几分钟内烧光上百美金的 Token 额度**。
    
- **企业级标准**：LangGraph 的 State 中虽然有 `retry_count`，但条件边逻辑中缺乏对单次死循环的绝对熔断控制。应当引入 **Max Retry 强制熔断节点**，重试失败后转向一个 `fallback_node`（降级节点），利用已有残缺数据生成一份“不完美但可用”的报告，而不是直接崩溃或死循环。
    

### ❌ 隐患：数据结构设计缺乏防御性

在 `AnalysisState` 中，`raw_research` 是一个 `list[dict]`。

- **后果**：海量搜索结果直接塞进 State 并在节点间传来传去，随着长达 10 分钟的链路流转，State 会变得极其庞大。这不仅占用内存，如果是分布式 LangGraph，序列化和反序列化这个大状态会带来巨大的性能开销。
    
- **企业级标准**：**State 只留轻量级 Metadata 和 ID**。原始 Research 到的长文本应该在落地到数据库（PostgreSQL）或向量库后，仅在 State 中传递 `doc_ids`，或者对文本进行极致的清洗、去重和分块（Chunking）。
    

## 3. 企业级数据合规与安全漏洞

### ❌ 隐患：完全暴露的 Web 抓取（Firecrawl）引发的法务与 IP 封禁风险

文档中提到 P1 阶段引入 Firecrawl 抓取竞品官网。

- **后果**：企业级客户如果配置抓取某些具有严格反爬或法律条款（ToS）的竞品网站，可能导致你的平台 IP 被拉黑，甚至引发法律纠纷（如未经授权的商业数据抓取）。
    
- **企业级标准**：
    
    1. 必须建立 **Proxy Pool（动态代理池）** 或使用带抗封锁能力的商业抓取服务。
        
    2. 必须实现 **Robots.txt 尊重机制** 与 **Rate Limiting（对单个域名的抓取频率限制）**，防止把竞品网站挂掉演变成 DDoS 攻击。
        

### ❌ 隐患：客户数据隔离（Multi-Tenancy）只字未提

所有表（`tasks`, `reports`）均以 `task_id` 或 `id` 作为主键，没有租户（Tenant ID）或用户（User ID）维度。

- **后果**：这是典型的单机 Demo 逻辑。在企业级 B 端场景下，A 公司的员工绝对不能看到 B 公司提交的竞品分析任务和报告。
    
- **企业级标准**：数据库模型必须引入 `tenant_id` 和 `user_id`，所有 CRUD 操作必须带上作用域隔离（Row-Level Security 或 强制 Context 过滤器）。
    

## 4. 商业价值与“企业感”的缺失（评审加分点）

评委或高管在看这个项目时，除了技术实现，更看重**商业闭环**。目前的设计缺少两个让老板愿意掏钱的“杀手级”企业功能：

- **缺少“增量更新与监控”机制（Delta Analysis）**：
    
    - _现状_：每次分析都是“单点触发”，输入名字，等 10 分钟，出报告。
        
    - _企业级痛点_：竞品的动态是**持续发生**的。企业真正需要的是：我关注了 Notion，平台每天/每周自动帮我跑 Research Agent，**只抓取过去 7 天的新闻、更新日志（Changelog）和定价变化**，并与上一份报告做对比，生成一份《Notion 本周动态差量分析》。
        
- **Human-in-the-loop (HITL) 被完全 Mock**：
    
    - _现状_：为了赶工期，Reviewer 自动放行。
        
    - _企业级痛点_：AI 生成的 SWOT 经常包含常识性错误或幻觉。企业级工作台必须允许专业分析师在 Writer 节点之后、Reviewer 节点之前进行**人工干预（Intervention）**——例如“一键驳回重跑”、“人工修正核心指标卡片”后再正式归档发布。
        

## 💡 怎么改？（高性价比的改造方案）

如果距离你的评审或上线时间有限，无需全盘推翻，优先做以下 **3 项性价比最高** 的企业级改造：

1. **引入 Redis 彻底重构事件流**：
    
    抛弃内存 `asyncio.Queue`，改用 Redis Pub/Sub。FastAPI 通过 Redis 监听事件推给前端。这一步能让你的系统瞬间具备水平扩展能力，从 “Demo” 跨入 “分布式可用”。
    
2. **给 LangGraph 加上绝对死循环熔断**：
    
    在 `AnalysisState` 中严格限制总的 `llm_call_count`，在条件边路由前加一个硬性判断：如果总调用次数超过 15 次，直接强行流转到 `writer` 或 `end`，并标记 `status="COMPLETED_WITH_WARNINGS"`。
    
3. **补充租户隔离字段**：
    
    在 `models.py` 的 `Task` 和 `Report` 表中加上 `user_id` 和 `organization_id`，哪怕 MVP 阶段写死一个默认值，也能在评审时向评委证明“我的底层架构已经做好了 B 端多租户隔离的准备”。