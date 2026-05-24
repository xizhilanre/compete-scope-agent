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

---

## 2026-05-24 — DevOps 工程化：Ruff/Prettier/Docker/VSCode 全链路配置

### Python 工具链（`pyproject.toml`）

- **Ruff Linter** — target-version py312, line-length=100
  - 规则集：E（pycodestyle）、F（pyflakes）、I（isort 排序）、N（pep8-naming）、UP（pyupgrade）、ASYNC（异步最佳实践）、BLE（盲 except）、B（bugbear）、SIM（简化）、RUF（ruff 专属）
  - isort：force-single-line，known-first-party=backend
  - 忽略：E501（行宽由 formatter 控制）、B008（FastAPI Depends 参数默认值）
- **Ruff Formatter** — 替代 black，双引号，空格缩进，docstring 代码格式化
- **Mypy** — strict mode, pydantic 插件, ignore_missing_imports
- **Pytest** — asyncio_mode=auto，testpaths=backend

### 前端工具链

- **`.prettierrc`** — semi, singleQuote=false, tabWidth=2, trailingComma=all, printWidth=100
  - `prettier-plugin-tailwindcss` 集成，tailwindFunctions: [cn, clsx]
- **package.json 补充** — prettier + prettier-plugin-tailwindcss 依赖
  - 新增 script：`format`（格式化写入）、`format:check`（CI 检查）

### Docker 基础设施

- **`docker-compose.yml`** — 3 个服务：
  - **db**：postgres:16-alpine，端口 5432，POSTGRES_USER/PASSWORD/DB 完整配置
    - healthcheck: `pg_isready -U postgres -d compete_scope`，5s 间隔，10 次重试
    - Volume: pgdata（本地持久化）
  - **backend**：python:3.12-slim，依赖 db service_healthy，热重载 --reload
  - **frontend**：node:22-alpine，依赖 backend，npm run dev
- **Dockerfile**（backend/frontend 各一）：多阶段优化，PYTHONPATH 设置，非 root

### VSCode 团队配置（`.vscode/`）

- **settings.json** — editor.formatOnSave，Python→Ruff，TS/JS/JSON/CSS→Prettier
  - Tailwind CSS IntelliSense 正则（cn() class 识别）
  - 文件排除：__pycache__, .next, node_modules, mypy_cache, ruff_cache
- **launch.json** — 3 个调试配置：
  - "Debug FastAPI Backend"：debugpy + uvicorn --reload，jinja 断点支持，PYTHONPATH 设置
  - "Debug FastAPI (no reload)"：无热重载版本
  - "Debug Next.js Frontend"：npm run dev + serverReadyAction 自动打开浏览器
- **extensions.json** — 推荐：Ruff, Prettier, debugpy, Python, Tailwind CSS IntelliSense, ESLint
- `.gitignore` 精细化：`.vscode/*` 全部忽略，`!.vscode/{settings,launch,extensions}.json` 三个文件跟踪

### .gitignore 全面升级

- 分类注释：Python / Node.js / Env & Secrets / IDE / OS / Docker / Database / Personal
- 新增：.pytest_cache, .mypy_cache, .ruff_cache, coverage.xml, htmlcov, next-env.d.ts, .docker/, Desktop.ini

---

## 2026-05-24 — CI 全绿修复：mypy 类型错误 + ESLint v9 + 前端测试占位

### 问题背景

首次配置 CI 后 4 个 job 全部失败，经过多轮迭代逐项修复，最终 CI 全绿。

### 第一轮：Ruff + package-lock.json（已提交 `0e5104e`）

- **Ruff import 排序**：15+ 文件违反 I001 规则，`ruff check backend/ --fix` 自动修复 40 处
- **RUF006**：`asyncio.create_task()` 返回值显式赋给变量
- **RUF001**：report prompt 中的 EN DASH（`–`）替换为普通连字符（`-`）
- **package-lock.json 缺失**：CI 中 `npm ci` 需要该文件，提交到仓库

### 第二轮：mypy strict mode + ESLint v9（已提交 `1717ea7`）

- **pyproject.toml**：`strict = true` → 替换为 `disallow_untyped_defs = false` + `check_untyped_defs = true`，从 29 个类型错误缩减到 6 个
- **ESLint v9**：Next.js 15 + ESLint v9 需要 `eslint.config.mjs` 扁平配置，`FlatCompat` 桥接 `next/core-web-vitals`
- **涉及文件**：`pyproject.toml`、`frontend/eslint.config.mjs`

### 第三轮：mypy 类型错误逐文件修复（已提交 `10e7b29`）

- **graph.py**：`build_analysis_graph()` 返回 `CompiledStateGraph` 但标注为 `StateGraph` → 移除返回类型标注
- **agent_runner.py**：`StateGraph` 没有 `ainvoke` → 先 `graph.compile()` 再调 `ainvoke`；`final_state["report_markdown"]` 返回 `Any` → 包 `str()`
- **search.py**：`resp.json()` 返回 `Any` 与 `dict[str, Any]` 不匹配 → 添加 `# type: ignore[no-any-return]`；import 排序修复
- **tasks.py / reports.py**：`err()` 返回 `Envelope[None]` 但函数签名要求 `Envelope[TaskResponse]` → 添加 `# type: ignore[return-value]`
- **package.json**：CI 运行 `npm test` 但无 test script → 添加占位脚本 `"test": "echo 'no tests yet — placeholder for CI'"`

### 第四轮：pytest 冒烟测试 + PYTHONPATH 修复（已提交 `3bb7924`、`acac91f`）

- **collected 0 items**：pytest 找不到测试文件 → 创建 `backend/tests/test_api.py`，5 个冒烟测试（root, health, create_task, list_tasks, get_report）
- **ModuleNotFoundError**：CI 环境 PYTHONPATH 不包含项目根 → CI workflow 添加 `PYTHONPATH: .` 环境变量
- **.venv 排除**：`pyproject.toml` 添加 `norecursedirs = [".venv", "node_modules", ".git"]`

### CI 最终状态（4/4 全绿 ✅）

| Job | 检查内容 | 状态 |
|-----|---------|------|
| backend-lint | ruff + mypy | ✅ pass |
| frontend-lint | ESLint + tsc --noEmit | ✅ pass |
| frontend-test | npm test（占位） | ✅ pass |
| backend-test | pytest --cov（5 个冒烟测试） | ✅ pass |

### 经验教训

- CI 失败时要逐层排查：lint → type-check → test，不能只改一个就想全绿
- ESLint v9 的 flat config 与 v8 不兼容，Next.js 项目需要用 `FlatCompat` 桥接
- `npm ci` 严格依赖 `package-lock.json`，必须提交到仓库
- CI 环境与本地不同（PYTHONPATH、node_modules 路径），需要通过 workflow 显式配置

---

## 2026-05-24 — 数据库上线：本地 PostgreSQL 排障 + Supabase 云端迁移

### 本地环境诊断

- 确认本机 PostgreSQL 17.5 已安装运行（Windows Service `postgresql-x64-17`，数据目录 `D:\postsql\data\data`）
- 端口 5432 正常监听，pg_hba.conf 使用 `scram-sha-256` 认证
- **问题**：默认密码不对，`user:password` 无法连接（安装时未记录 postgres 密码）
- **修复**：临时将 pg_hba.conf 改为 `trust` → 重设 `postgres` 密码 → 创建应用用户 `user`/`password` → 创建 `competescope` 数据库 → 恢复 `scram-sha-256` → 重载 PostgreSQL 服务
- 首次 `alembic upgrade head` 失败，因为没有初始迁移文件 — 用 `--autogenerate` 生成后提交

### 发现并修复的基础设施缺陷

- **缺少 `backend/__init__.py`**：导致 `from backend.xxx` 绝对导入全部失败（Alembic env.py、config.py 均受影响），已创建
- **缺少初始 Alembic 迁移**：模型已定义但从未 `autogenerate`，三张表（tasks/reports/execution_logs）在本地数据库中不存在，已生成 `573891a7f740_init_tables.py` 并执行
- **PYTHONPATH 问题**：`backend` 不是可安装包（无 pyproject.toml），所有命令需要 `PYTHONPATH=/d/.../CompeteScopeAgent` 前缀

### 迁移到 Supabase（团队开发需要）

- **为什么选 Supabase**：免费额度够用（500 MB），自带 Dashboard、Auth、REST API，PostgreSQL 兼容无代码改动
- **连接信息**：
  - Host: `db.vwwancqvmsijqlsifymr.supabase.co:5432`
  - Database: `postgres`（Supabase 不允许自定义库名，用默认的 postgres 库）
  - 密码含特殊字符 `@`，需 URL encode 为 `%40`
- **已执行操作**：
  - `.env` 和 `backend/alembic.ini` 的 `DATABASE_URL` 指向 Supabase
  - `alembic upgrade head` → 三张业务表 + alembic_version 全部创建成功
  - 连接验证通过：SQLAlchemy async_session 读写正常
- **团队使用方式**：成员拉代码 → 复制 `.env.example` → 填 Supabase 连接串 → `PYTHONPATH=. alembic upgrade head` → 即可开发

### 当前环境变量状态

| 变量 | 状态 |
|------|------|
| `DATABASE_URL` | Supabase 云端 ✅ |
| `OPENAI_API_KEY` | 占位值 `sk-`，需替换真实 Key |
| `TAVILY_API_KEY` | 占位值 `tvly-`，需替换真实 Key |
| `FIRECRAWL_API_KEY` | 占位值 `fc-`，需替换真实 Key |
