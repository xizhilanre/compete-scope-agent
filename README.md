# 🚀 CompeteScope Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/xizhilanre/compete-scope-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/xizhilanre/compete-scope-agent/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/xizhilanre/compete-scope-agent?include_prereleases&label=release)](https://github.com/xizhilanre/compete-scope-agent/releases)
[![Issues](https://img.shields.io/github/issues/xizhilanre/compete-scope-agent)](https://github.com/xizhilanre/compete-scope-agent/issues)

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15+-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-DAG-orange?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tavily](https://img.shields.io/badge/Search-Tavily-6C5CE7)](https://tavily.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/xizhilanre/compete-scope-agent/blob/main/CONTRIBUTING.md)

> 输入一个产品名，5 个 Agent 协同工作 10 分钟，自动生成企业级竞品分析报告。
>
> Input a product name, get an enterprise-grade competitive analysis report in 10 minutes.

---

## 🧠 Agent Workflow (DAG)

```
  [User Input: 产品名]
         │
         ▼
   ┌──────────┐
   │  Planner  │  分解搜索计划 → 生成关键词矩阵
   └────┬─────┘
        │
   ┌────┴────┐
   ▼         ▼
┌────────┐ ┌────────┐
│Research│ │Research│  Tavily 实时搜索 → 竞品信息采集
└───┬────┘ └───┬────┘
    │          │
    └────┬─────┘
         ▼
   ┌──────────┐
   │ Analysis  │  SWOT + 多维指标提取 + Citation 溯源
   └────┬─────┘
        │
        ▼
   ┌──────────┐
   │  Writer   │  结构化报告生成 (Markdown / JSON)
   └────┬─────┘
        │
        ▼
   ┌──────────┐
   │ Reviewer  │  QA 审核 → 幻觉检测 → 输出质量评分
   └────┬─────┘
        │
        ▼
  [SSE Live Replay + 可观测性面板]
```

## ✨ Key Features

| 模块 | 功能 |
|------|------|
| **Multi-Agent Orchestration** | LangGraph DAG, 5-agent pipeline, parallel research nodes |
| **Real-time Search** | Tavily Search API, full citation traceability |
| **Structured Output** | SWOT analysis, multi-dimension metric cards |
| **SSE Live Replay** | Real-time progress streaming, token cost tracking |
| **Observability** | Agent timeline, execution replay, cost breakdown |
| **Tech Stack** | FastAPI (backend) + Next.js 15 (frontend) + PostgreSQL 16 |

## 📦 Project Structure

```
compete-scope-agent/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # REST + SSE endpoints
│   │   ├── agents/            # LangGraph DAG: Planner, Research, Analysis, Writer, Reviewer
│   │   ├── services/          # Tavily client, report generator
│   │   └── models/            # Pydantic schemas
│   ├── tests/
│   └── requirements.txt
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   ├── components/       # React components (SSE progress, SWOT viz)
│   │   └── lib/              # API client, hooks
│   └── package.json
├── docs/                      # Documentation
├── .github/                   # CI/CD, issue templates
└── README.md
```

## 🚀 Quickstart

> ⚠️ **In active development.** Quickstart guide coming with v0.1 release.

```bash
# Prerequisites: Python 3.12+, Node 22+, PostgreSQL 16+

# 1. Clone
git clone https://github.com/xizhilanre/compete-scope-agent.git
cd compete-scope-agent

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # add your TAVILY_API_KEY
uvicorn app.main:app --reload

# 3. Frontend
cd ../frontend
npm install
cp .env.example .env.local
npm run dev
```

## 🗺️ Roadmap

- [ ] **v0.1.0** — Core 5-agent DAG, Tavily search, SWOT output, SSE streaming
- [ ] **v0.2.0** — Citation traceability, agent timeline visualization
- [ ] **v0.3.0** — Multi-language reports, PDF export
- [ ] **v0.4.0** — Custom search sources (MCP connectors), report comparison
- [ ] **v1.0.0** — Enterprise auth, team workspaces, PostgreSQL persistence

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for branch strategy and PR workflow.

1. Fork the repo
2. Branch from `develop` → `feature/your-feature`
3. Open a PR to `develop`
4. CI must pass + 1 review approval

## 📄 License

MIT © CompeteScope Agent Contributors
