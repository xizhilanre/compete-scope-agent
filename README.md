# 🚀 compete-scope-agent

输入一个产品名，5 个 Agent 协同工作 10 分钟，自动生成企业级竞品分析报告。

- **核心架构**：基于 LangGraph 的 `Planner` → `Research` → `Analysis` → `Writer` → `Reviewer` 五节点 DAG 异步工作流。
- **数据与输出**：集成 Tavily 实时网络搜索，输出结构化 SWOT 分析与多维指标卡片，支持全链路 Citation 原文溯源。
- **用户体验**：基于 SSE（Server-Sent Events）的实时进度可视化，提供完整的 Token 消耗与 Agent Timeline 可观测性面板。
- **技术全栈**：FastAPI + Next.js + PostgreSQL。

---

Input a product name, get an enterprise-grade competitive analysis report in 10 minutes.

- **Core Architecture**: Powered by a 5-Agent LangGraph DAG (`Planner` → `Research` → `Analysis` → `Writer` → `Reviewer`).
- **Data & Output**: Real-time web search via Tavily, structured output with SWOT + MetricCards, and full citation traceability.
- **UX & Observability**: SSE-driven live progress visualization with full observability (token cost, agent timeline, execution replay).
- **Tech Stack**: FastAPI + Next.js + PostgreSQL.
