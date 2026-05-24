# SSE Events Reference

CompeteScope uses Server-Sent Events for live progress streaming during analysis.

## Connection
```
GET /api/analyze/{job_id}/stream
Accept: text/event-stream
```

## Event Types

### progress
Fired when an agent node begins or completes.
```
event: progress
data: {"agent": "planner", "status": "started", "timestamp": "2026-05-24T12:00:00Z"}
data: {"agent": "planner", "status": "completed", "timestamp": "2026-05-24T12:00:05Z"}
```

### partial
Incremental results from research and analysis agents.
```
event: partial
data: {"agent": "research", "query": "Notion competitors 2026", "findings": [{"url": "...", "snippet": "..."}]}
```

### swot
SWOT item emitted by the analysis agent.
```
event: swot
data: {"category": "strength", "point": "Market leader in collaborative docs", "confidence": 0.92}
```

### complete
Final report delivered.
```
event: complete
data: {"report_markdown": "# Competitive Analysis...", "competitors": ["Coda", "Confluence"], "swot": [...]}
```

### error
Non-fatal warning or fatal error.
```
event: error
data: {"level": "warning", "message": "Tavily rate limited, retrying..."}
event: error
data: {"level": "fatal", "message": "API key invalid"}
```

## Client Reconnection
Clients should implement exponential backoff: 1s → 2s → 4s → 8s (max 30s).
