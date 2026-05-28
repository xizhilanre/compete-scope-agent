# CompeteScope MVP 设计文档

> 日期：2026-05-28
> 版本：v1.0
> 状态：待评审

---

## 1. 目标与范围

### 1.1 一句话定义

输入产品名 → 5 个 Agent 线性 DAG 串联 → 浏览器看实时进度 → 拿到一份 Markdown 竞品报告。

### 1.2 MVP 受众

- 给自己验证技术架构和产品想法
- 给产品搭档展示「整个系统跑起来的样子」

### 1.3 阶段策略：两阶段冲刺

| 阶段 | 时间 | 目标 | 验收 |
|------|------|------|------|
| Day 1 | ~4h | 后端全部：State + CRUD + Tool Registry + 5 Agent（模拟模式）+ DAG + Runtime + 路由改造 | `python test_pipeline.py` 不报错，DB 有 COMPLETED task 和 report |
| Day 2 | ~4h | 前端全部：工作台布局 + Dashboard + 创建表单 + 任务详情 DAG + 报告页 | 浏览器全流程走通，DAG 节点逐一亮起 |
| Day 3 | ~4h | 真实替换：Planner + Research + Writer 接真实 LLM + Tavily，Analysis/Reviewer 跳过 | 输入 "Notion" → 出真实竞品报告 |

### 1.4 明确不做

- 条件重试 / 熔断器
- Firecrawl 深度网页抓取
- Citation 溯源面板
- Agent Trace 详细日志页
- 用户认证 / 多租户
- 错误边界和加载骨架屏等 UI 细节

---

## 2. 架构设计

### 2.1 数据流

```
[用户输入] → POST /api/tasks → create_task(DB) → BackgroundTask(run_dag)
                                                         │
                              ┌──────────────────────────┘
                              ▼
                    [run_dag 初始化 State]
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
      Planner ──────────▶ Research ──────────▶ Writer ──────────▶ END
     (LLM生成搜索词)     (Tavily真实搜索)     (LLM写报告)
          │                   │                   │
          └───────────────────┴───────────────────┘
                              │
                    publish(task_id, events)  →  SSE →  前端 DAG 高亮
                    create_report(DB)                  前端报告渲染
                    update_task_status(COMPLETED)
```

### 2.2 模拟模式 vs 真实模式

通过环境变量 `COMPETESCOPE_MOCK` 控制：

- `true`（Day 1-2）：每个 Agent sleep 2s + 返回硬编码假数据。5 节点全上（Planner/Research/Analysis/Writer/Reviewer）。报告内容为预写的中文 Markdown。
- `false`（Day 3）：Planner 调 DeepSeek → Research 调 Tavily → Writer 调 DeepSeek。3 节点（砍掉 Analysis/Reviewer）。报告内容为 LLM 实时生成。

两种模式共享同一套 Runtime、DAG、SSE 推送、DB 写入逻辑，仅 Agent 节点内部行为不同。

### 2.3 State 数据总线

AnalysisState 包含约 15 个字段，覆盖全链路数据流：

- 输入区：`task_id`、`target_product`、`analysis_dimensions`
- Planner 输出：`search_queries`、`analysis_plan`
- Research 输出：`raw_research`
- Analysis 输出：`structured_analysis`（模拟模式用，真实模式跳过）
- Writer 输出：`final_report_markdown`、`metric_cards`
- Reviewer 输出：`quality_score`、`quality_feedback`
- Runtime 跟踪：`current_agent`、`execution_logs`（Annotated list）、`token_usage`、`llm_call_count`、`status`、`error`

---

## 3. 模块设计

### 3.1 需要新建的文件

**后端核心（6 个）：**

| 文件 | 职责 | 关键接口 |
|------|------|---------|
| `backend/core/state.py` | AnalysisState TypedDict | import 无依赖 |
| `backend/core/llm.py` | get_llm() + safe_parse_json() | 依赖 settings |
| `backend/tools/tavily_search.py` | tavily_search_sync(query, max_results) → list[dict] | 依赖 settings，httpx |
| `backend/tools/registry.py` | ToolRouter(task_id) → call_sync(tool_name, **kwargs) | 依赖 tavily_search |
| `backend/db/crud.py` | 6 个异步 CRUD 函数 | 依赖 models, database |
| `backend/core/runtime.py` | run_dag(task_id, product, dimensions) + get_mock_state() | 依赖 workflow, crud, events |

**Agent 节点（5 个）：**

| 文件 | 函数 | 模拟行为 | 真实行为 |
|------|------|---------|---------|
| `backend/agents/planner.py` | run_planner(state, mock) | sleep 2s → 返回预编 search_queries | 调 LLM 生成搜索词 |
| `backend/agents/research.py` | run_research(state, mock) | sleep 2s → 返回预编 raw_research | 调 Tavily 搜索 |
| `backend/agents/analysis.py` | run_analysis(state, mock) | sleep 2s → 返回预编 SWOT | （Day 3 不进入 DAG） |
| `backend/agents/writer.py` | run_writer(state, mock) | sleep 2s → 返回预编 Markdown | 调 LLM 写报告 |
| `backend/agents/reviewer.py` | run_reviewer(state, mock) | sleep 1s → 返回预编评分 | （Day 3 不进入 DAG） |

**DAG 组装（1 个）：**

| 文件 | 函数 | 说明 |
|------|------|------|
| `backend/core/workflow.py` | build_dag(mock: bool) → CompiledStateGraph | mock=True 时 5 节点线性，mock=False 时 3 节点线性 |

**前端（7 个）：**

| 文件 | 类型 | 说明 |
|------|------|------|
| `app/(workspace)/layout.tsx` | 页面 | Sidebar + 内容区 |
| `app/(workspace)/page.tsx` | 页面 | Dashboard 任务列表 |
| `app/(workspace)/tasks/new/page.tsx` | 页面 | 创建任务表单 |
| `app/(workspace)/tasks/[id]/page.tsx` | 页面 | 任务详情 + DAG |
| `app/(workspace)/reports/[id]/page.tsx` | 页面 | 报告查看 |
| `components/dag/DAGVisualizer.tsx` | 组件 | SVG 五/三节点拓扑图 |
| `components/report/ReportViewer.tsx` | 组件 | Markdown 渲染（react-markdown） |

### 3.2 需要改造的文件

| 文件 | 改动 |
|------|------|
| `backend/api/routes/tasks.py` | POST 切 create_task + BackgroundTask(run_dag)；GET 切 CRUD 真实查询 |
| `backend/api/routes/reports.py` | GET 切 get_report 真实查询 |

### 3.3 不新建/不改动的文件

- `backend/db/models.py` — 三张表已完成，不变
- `backend/db/database.py` — 异步引擎已完成，不变
- `backend/schemas/` — Pydantic 契约已完成，不变
- `backend/prompts/agents.py` — 已有 Prompt 模板，MVP 不引用（Agent 内嵌 Prompt）
- `backend/api/routes/events.py` — SSE 底座已完成，不变
- `frontend/hooks/useSSE.ts` — SSE hook 已完成，不变

---

## 4. 前端页面数据流

```
Dashboard (/)
  mount → GET /api/tasks?skip=0&limit=20
  → 渲染 TaskCard 列表
  → 点击卡片 → router.push(/tasks/[id])
  → 点击「新建」→ router.push(/tasks/new)

创建任务 (/tasks/new)
  提交表单 → POST /api/tasks {target_product, analysis_dimensions}
  → 响应 201 + task_id
  → router.push(/tasks/[task_id])

任务详情 (/tasks/[id])
  mount → new EventSource(GET /api/analyze/[id]/stream)
  → 监听 agent_start / agent_complete → 更新 DAG 节点状态
  → 监听 task_complete → router.push(/reports/[report_id])
  → 监听 task_failed → 显示错误

报告查看 (/reports/[id])
  mount → GET /api/reports/[id]
  → ReportViewer 渲染 markdown_content
  → SWOTChart 渲染 structured_data.swot（如有）
```

---

## 5. 风险与对策

| 风险 | 概率 | 对策 |
|------|------|------|
| Day 3 LLM 返回 JSON 格式不规范，safe_parse_json 失败 | 中 | Planner 失败回退到预设默认搜索词；Writer 不解析 JSON 直接取文本 |
| Tavily 搜索限流或返回空 | 低 | Research 结果为空时 Writer 用产品名直接让 LLM 基于知识写报告 |
| 前端 SSE 连接不稳定 | 中 | useSSE hook 已有指数退避重连，断开时任务详情页显示「重连中」文案 |
| 时间不够 Day 3 完不成 | 低 | 降级：只做 Planner + Writer（跳过 Research），Tavily 换成第二轮 LLM 假装搜到了东西 |
| LangGraph ainvoke 超时 | 低 | DeepSeek 设置 timeout=90s，单次 LLM 调用不跨节点 |

---

## 6. 验收标准

### Day 1 验收
- `python backend/test_pipeline.py "Notion"` 执行无报错
- 数据库 tasks 表有 COMPLETED 记录
- 数据库 reports 表有对应报告记录，markdown_content 不为空
- POST /api/tasks 返回 201 + task_id

### Day 2 验收
- 浏览器完整路径：/ → 新建任务 → 输入产品名 → 提交 → 看 DAG 节点高亮 → 自动跳转报告页 → 渲染 Markdown
- SSE 连接不中断，节点逐个从 waiting → running → completed
- 所有页面不报错

### Day 3 验收
- `COMPETESCOPE_MOCK=false python backend/test_pipeline.py "Notion"` 输出真实报告
- 可在 Dashboard 历史列表看到该条记录
- 报告内容包含 Notion 相关的真实竞品信息（不是硬编码的假数据）
- 可切回 `COMPETESCOPE_MOCK=true` 恢复模拟模式
