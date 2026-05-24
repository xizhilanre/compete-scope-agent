# Agent State Machine

CompeteScope uses LangGraph's `StateGraph` with a typed state object flowing through 5 nodes.

## State Schema

```python
class AgentState(TypedDict):
    product_name: str
    search_plan: list[str]
    research_results: Annotated[list[dict], operator.add]
    swot: list[dict]
    report_markdown: str
    errors: list[str]
    status: str
```

## Node Sequence (DAG)

```
Planner → Research → Analysis → Writer → Reviewer
```

### 1. Planner
- Input: `product_name`
- Action: Generates search queries and analysis dimensions via LLM
- Output: populates `search_plan`
- Prompt: `prompts/agents.py::PLANNER_SYSTEM`

### 2. Research
- Input: `search_plan`
- Action: Executes parallel Tavily searches + Firecrawl deep extraction
- Output: appends to `research_results`
- Tools: `tools/search.py::tavily_search`, `firecrawl_extract`

### 3. Analysis
- Input: `research_results`
- Action: Synthesizes findings into SWOT items with confidence scores
- Output: populates `swot`
- Prompt: `prompts/agents.py::ANALYSIS_SYSTEM`

### 4. Writer
- Input: `swot`, `research_results`
- Action: Generates structured Markdown report
- Output: populates `report_markdown`

### 5. Reviewer
- Input: `report_markdown`, `research_results`
- Action: QA pass — checks citations, detects hallucinations, scores quality
- Output: potentially corrects `report_markdown`, appends `errors`

## Status Lifecycle

```
queued → running (planning → researching → analyzing → writing → reviewing) → completed
                                                                              ↘ failed
```

`status` field on `AnalysisJob` (PostgreSQL) tracks high-level state.
`current_agent` field updates in real-time via SSE.
