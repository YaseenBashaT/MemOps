# MemOps Build Checklist

## Phase 0 — Cognee Verified ✅
- [x] Cognee v1.2.2 installed
- [x] Real API confirmed: remember(), recall(), improve(), forget()
- [x] Groq LLM configured (custom provider, llama-3.3-70b-versatile)
- [x] fastembed configured for local embeddings (BAAI/bge-small-en-v1.5)
- [x] Live ingest → recall cycle verified (graph-aware, GRAPH_COMPLETION_CONTEXT_EXTENSION)

## Phase 1 — Memory Service Layer + FastAPI Skeleton ✅
- [x] Project folder structure created (backend/, services/, routes/, models/)
- [x] memory_service.py: single Cognee gateway with 4 clean async functions
  - [x] ingest_incident(incident: dict) -> None
  - [x] recall_for_alert(alert_text: str) -> dict
  - [x] reinforce_fix(dataset_name: str) -> None
  - [x] forget_incident(dataset_name: str) -> None
- [x] No other file imports cognee directly
- [x] schemas.py: Pydantic models for Incident, JiraTicket, RecallRequest, HealthResponse
- [x] main.py: FastAPI with CORS (localhost:5173), lifespan init, health route
- [x] GET /api/health returns {"status": "ok"}
- [x] test_phase1.py: ingests 2 incidents, recalls, shows graph-aware output
- [x] test_phase1.py verified: both incidents ingested, graph-aware recall confirmed
- [x] Committed: "feat: Phase 1 -- memory service layer and FastAPI skeleton"

## Phase 2 — (pending)
- [ ] TBD
