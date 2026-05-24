# CompeteScope API Contract

## Base URL
`http://localhost:8000/api`

## Endpoints

### Health Check
```
GET /api/health
Response 200: { "status": "healthy", "version": "0.1.0" }
```

### Start Analysis
```
POST /api/analyze/start
Body: { "product_name": "Notion" }
Response 200: { "job_id": "uuid", "status": "queued" }
```

### Job Status
```
GET /api/analyze/{job_id}/status
Response 200: { "job_id": "uuid", "status": "running", "current_agent": "Research" }
```

### SSE Stream
```
GET /api/analyze/{job_id}/stream
Content-Type: text/event-stream

Events:
  - event: progress    data: {"agent": "planner", "step": "generating plan"}
  - event: partial     data: {"agent": "research", "findings": [...]}
  - event: complete    data: {"report": "...", "swot": [...]}
  - event: error       data: {"message": "..."}
```

## Error Format
```json
{ "detail": "Error message" }
```
HTTP status codes: 400 (bad input), 404 (job not found), 500 (internal).
