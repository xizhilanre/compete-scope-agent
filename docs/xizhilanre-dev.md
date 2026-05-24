# xizhilanre 开发日志

## 2026-05-24 — GitHub 仓库初始化与规范化配置

### 仓库创建

- 在 GitHub 上创建 `xizhilanre/compete-scope-agent` 仓库（Public）
- 编写中英文双语文档（README、产品文档、架构参考文档）
- 初始提交：`Initial commit: CompeteScope — 企业级竞品分析 AI Agent 平台`

### GitHub CLI 配置

- 安装并登录 GitHub CLI（`gh auth login`），Token 权限：`gist`, `read:org`, `repo`

### 仓库基础设置

- 添加 12 个 Topics 标签：`langgraph` `ai-agent` `competitive-analysis` `fastapi` `nextjs` `postgresql` `tavily` `sse` `mcp` `swot-analysis` `llm` `agent-workflow`
- 选择 MIT License
- 关闭 Wiki、Projects、Discussions
- 开启 "Delete branch on merge"（合并后自动删除分支）

### 分支管理

- `main` — 生产分支，受保护：
  - 必须通过 PR 合并
  - 至少 1 个 Reviewer 批准
  - 禁止 force push / 删除分支
  - 必须解决所有 Conversation
  - Stale review 自动 dismiss 并重新请求
- `develop` — 集成分支（日常开发）

### 社区文件

- Issue 模板：Bug Report（英文表单格式）、Feature Request（英文表单格式）
- PR 模板（Summary + Checklist）
- CODEOWNERS：自动指定 `@xizhilanre` 为 Reviewer
- SECURITY.md：安全漏洞报告指南
- CONTRIBUTING.md：贡献流程说明（branch strategy、PR workflow）

### CI/CD（持续集成）

- **是什么**：自动化流水线，每次推送代码或提 PR 时自动运行，充当「自动化代码质检员」
- **触发时机**：Push 到 `develop` / PR 到 `main` 或 `develop`
- **后端检查（Python）**：
  - ruff — 代码格式与 lint（替代 flake8 + isort）
  - mypy — 静态类型检查，提前发现类型错误
  - pytest + coverage — 运行单元测试并生成覆盖率报告
- **前端检查（Node.js）**：
  - ESLint — JS/TS 代码规范
  - tsc --noEmit — TypeScript 类型检查
  - vitest — 运行前端测试（Next.js 生态首选）
- **价值**：
  - 防止坏代码合入主分支（配合 branch protection 强制要求 CI 通过）
  - 替代人工逐项检查，code review 聚焦逻辑而非格式
  - PR 页面直接看到 ✅/❌ 结果，一目了然

### README 增强

- 8 个技术栈 Badge（Python、FastAPI、Next.js、LangGraph、PostgreSQL、Tavily、PRs Welcome）
- ASCII 架构图（Agent DAG 拓扑：Planner → Research → Analysis → Writer → Reviewer）
- Feature 功能表格
- 项目目录结构树
- Quickstart 快速启动指南
- 版本 Roadmap（v0.1 → v1.0）

### 版本发布

- 创建 v0.1.0 Pre-release（Project Bootstrap 里程碑）
- 同步 `develop` 分支到最新

### 文档整理

- 原始设计文档（`产品文档.md`、`借鉴craft agent开发的竞品分析 AI Agent 平台.md`）移入 `docs/` 目录

### 个人 CLAUDE.md 配置

- 创建项目级 `CLAUDE.md`（加入 `.gitignore`，本地生效）
- 约定：开发日志自动更新、提交格式、分支策略、中文沟通

---

## 2026-05-24 — 全栈 Monorepo 脚手架初始化

### 后端（FastAPI + Python 3.12）

- `backend/config.py` — pydantic-settings 读取所有环境变量
- `backend/main.py` — FastAPI 入口，`/api/health` 健康检查 + CORS（localhost:3000）
- `backend/api/health.py` — 健康检查路由
- `backend/api/analyze.py` — 分析任务 API（start / status）
- `backend/agents/graph.py` — LangGraph 5-agent DAG（Planner→Research→Analysis→Writer→Reviewer）
- `backend/core/agent_runner.py` — Graph 执行入口
- `backend/db/session.py` — SQLAlchemy 异步引擎 + session factory
- `backend/db/models.py` — AnalysisJob ORM 模型（PostgreSQL）
- `backend/schemas/analysis.py` — Pydantic 请求/响应模型（AnalysisRequest, SWOTItem, AnalysisResult）
- `backend/tools/search.py` — Tavily 搜索 + Firecrawl 提取 LangChain tools
- `backend/prompts/agents.py` — 5 个 Agent 的 System Prompt 模板

### 前端（Next.js 15 + TypeScript）

- `frontend/package.json` — Next.js 15 + React 19 + Tailwind CSS v4 + TypeScript 5.7
- `frontend/app/layout.tsx` — 根布局（暗色主题）
- `frontend/app/page.tsx` — 首页：输入产品名 → 启动分析 → SSE 实时进度
- `frontend/hooks/useAnalysis.ts` — SSE 流式分析 hook
- `frontend/lib/utils.ts` — apiFetch 封装 + cn 工具函数
- `frontend/types/analysis.ts` — AnalysisJob, SWOTItem, SSEEvent 类型定义
- `frontend/next.config.ts` — standalone 输出模式
- `frontend/tsconfig.json` — strict mode + bundler 模块解析

### 基础设施

- `.env.example` — 全部环境变量模板（DATABASE_URL, OPENAI_API_KEY, TAVILY_API_KEY 等）
- `scripts/setup.sh` — 一键安装：Python venv + pip + npm，bash 可执行
- `docs/api-contract.md` — API 端点文档（health, analyze/start, status, SSE stream）
- `docs/sse-events.md` — SSE 事件类型参考（progress, partial, swot, complete, error）
- `docs/agent-state.md` — Agent 状态机文档（StateGraph schema + 5 node 职责）
- CI 工作流更新：PostgreSQL service container + mypy backend/ + pytest --cov

---

## 2026-05-24 — 异步数据库层 + Alembic 迁移系统

### 数据库层（SQLAlchemy 2.0 Async）

- `backend/db/database.py` — 核心模块：
  - `create_async_engine` + `async_sessionmaker`（pool_size=20, pool_pre_ping, pool_recycle）
  - `Base`（DeclarativeBase）— 所有模型的基类
  - `get_db()` — FastAPI 异步依赖注入生成器（try/yield/commit/rollback/close）
- `backend/db/models.py` — 三张表，完全使用 `Mapped`/`mapped_column` 新语法：
  - **Task** — 分析任务（id: UUID hex 32, target_product, analysis_dimensions JSON, status PENDING/RUNNING/COMPLETED/FAILED, 时间戳, error）
  - **Report** — 分析报告（id, task_id UNIQUE FK→tasks, markdown_content, structured_data JSON, metric_cards JSON, quality_score, citations_data JSON, token_usage JSON）
  - **ExecutionLog** — 执行日志（id autoincrement, task_id FK, agent_name, event_type, data JSON, timestamp, duration_ms）
  - TaskStatus 使用 PostgreSQL 原生 ENUM（`create_type=True`）
  - relationship 使用 `lazy="selectin"` 避免 N+1
- `backend/db/session.py` — 重导出层，保持向后兼容

### Alembic 迁移系统

- `backend/alembic.ini` — 基础配置
- `backend/alembic/env.py` — 异步 env：
  - 从 `config.Settings` 读取 DATABASE_URL（不依赖 alembic.ini 硬编码）
  - `run_migrations_online()` 使用 `create_async_engine` + `run_sync`
  - 自动导入所有 models 以 populating `Base.metadata`
- `backend/alembic/script.py.mako` — 标准迁移模板
- `docs/database-migrations.md` — 完整命令手册（autogenerate / upgrade / downgrade / troubleshooting）

### config.py 修复

- `.env` 路径改为基于 `Path(__file__).resolve().parent.parent` 的绝对路径
- 无论从哪个目录启动都能正确读取项目根目录的 `.env`

---

## 2026-05-24 — Pydantic v2 Schemas + RESTful 路由契约层

### Schema 层（`backend/schemas/`）

- **`base.py`** — 统一信封结构：
  - `Envelope[T]` — Generic wrapper，`{success, data, error}` 三者固定
  - `ok(data)` / `err(message)` — 快捷工厂函数
- **`task.py`** — 任务契约：
  - `TaskCreateRequest` — POST body（target_product + analysis_dimensions）
  - `TaskResponse` — 单任务视图，`from_attributes=True`
  - `TaskListResponse` — 分页列表视图（total, skip, limit, items）
  - `TaskStatusEnum` — 与 DB 层枚举对齐
- **`report.py`** — 报告契约（全部 `from_attributes=True`）：
  - `ReportResponse` — 顶层报告视图
  - `SWOTItem` — SWOT 条目（category, point, confidence, citations）
  - `MetricCard` — 指标卡片（label, value, trend, competitor_count）
  - `CitationEntry` — 引用溯源（url, title, snippet, retrieved_at）
  - `TokenUsage` — Token 消耗统计（含 cost_estimate_usd）

### 路由层（`backend/api/routes/`）

- **`tasks.py`** — 3 个端点，全部返回 `Envelope` 包裹的 mock 数据：
  - `POST /api/tasks` → 201 + Envelope[TaskResponse]
  - `GET /api/tasks?skip=0&limit=20` → Envelope[TaskListResponse]
  - `GET /api/tasks/{task_id}` → Envelope[TaskResponse] 或 404 envelope
- **`reports.py`** — 1 个端点：
  - `GET /api/reports/{report_id}` → Envelope[ReportResponse]（含完整 SWOT、MetricCards、Citations、TokenUsage）

### 设计决策

- 所有响应体统一走 `Envelope[T]`，前端只需检查 `success` 字段即可分流
- `from_attributes=True` 确保后续可直接传入 SQLAlchemy ORM 对象，不需要 `.model_validate()`
- 日期时间使用 Python `datetime` + Pydantic 默认序列化，输出标准 ISO-8601
- 路由层使用 mock 数据，不依赖 DB，当前即可通过 `/api/docs` 测试全部端点
- `backend/main.py` 已更新，include 了新的 routes 模块

---

## 2026-05-24 — SSE 实时事件推送底座（全栈）

### 后端事件 Schema（`backend/schemas/events.py`）

- 8 种事件类型字面量：`task_start | agent_start | agent_complete | tool_call | tool_result | task_complete | task_failed | heartbeat`
- 5 种 Agent 名称：`planner | research | analysis | writer | reviewer`
- 每种事件独立的 Pydantic 模型，`event` 字段用 `Literal` 做 discriminated union
- `SSEEvent` 联合类型 — `publish()` 的类型安全入参
- `iso_now()` — UTC ISO-8601 时间戳工厂

### 后端 SSE 路由（`backend/api/routes/events.py`）

- 全局 `_sse_queues: dict[str, asyncio.Queue]` — 零外部依赖，纯内存
- `ensure_queue(task_id)` — 惰性创建队列（maxsize=256）
- `publish(task_id, event)` — Agent 节点推送事件，队列满时丢弃 + 警告日志
- `remove_queue(task_id)` — 任务结束/客户端断开时清理
- `GET /api/analyze/{task_id}/stream` — SSE StreamingResponse：
  - `_event_generator` 异步生成器，`asyncio.wait_for(queue.get(), timeout=30)`
  - 30 秒无事件 → 自动发送 heartbeat
  - `task_complete` / `task_failed` → 跳出循环 → finally 清理队列
  - `CancelledError` → 客户端断开 → finally 清理
  - SSE 格式化 `event: <type>\ndata: <json>\n\n`

### 前端类型（`frontend/types/sse-events.ts`）

- 与后端 Pydantic 逐字段对齐，每个 interface 字段名、类型、可选性严格一致
- `SSEEventType` 字面量联合、`AgentName` 联合、`ALL_AGENTS` 常量数组
- `SSEEvent` discriminated union — `event` 字段为判别键
- `AgentState` / `AgentStateMap` — UI 层状态类型（waiting/running/completed）

### 前端 React Hook（`frontend/hooks/useSSE.ts`）

- `useSSE()` → `{ connect, disconnect, isConnected, taskStatus, agentStates, events, ... }`
- **Agent 状态机**：agent_start → agent 变为 "running"，agent_complete → "completed"
- **指数退避重连**：1s → 2s → 4s → ... → 30s 上限，仅 running/idle 状态下重连
- **Stale-closure 安全**：`handleMessageRef` + `taskStatusRef` 避免 EventSource 回调中的闭包过期
- **生命周期管理**：unmount 自动断开，disconnect 取消重连计时器
- 旧 `analysis.ts` 中的 `SSEEvent` 接口已移除，统一使用新类型
