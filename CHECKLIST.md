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

## Phase 2 — Seed Incidents + Verified Cross-Incident Recall ✅
- [x] 17 incidents authored in seed.py (3 clusters + standalones)
  - payments-api escalation arc (connection pool 10→50 → PgBouncer → dynamic autoscaling)
  - recommendation-service root-cause arc (memory leak REC-512 → REC-688)
  - api-gateway arc (manual cert renewal → cert-manager automated renewal)
  - same-service distractor (INC-2025-0118 payments-api, different problem) to test precision
- [x] Consolidated dataset architecture: all incidents ingested into ONE shared
      `incidents` dataset (constant INCIDENTS_DATASET in memory_service.py) so Cognee
      builds a single connected graph. Shared nodes (services, engineers, fixes) link
      incidents, making recall one graph traversal instead of one LLM call per dataset.
- [x] Eliminated per-incident-dataset fan-out: recall dropped from ~17 LLM calls
      (one per old dataset) to a flat **2 calls/recall** that does NOT scale with
      incident count.
- [x] recall_for_alert uses SearchType.GRAPH_COMPLETION (1 completion call) instead of
      the auto-routed GRAPH_COMPLETION_CONTEXT_EXTENSION (5+ calls) — cheaper + avoids
      rate limits.
- [x] 3 verification recalls run with litellm cost tracking (test_phase2.py):
  - Recall 1 "payments-api connection issues"        → 2 calls, $0.0031
  - Recall 2 "recommendation-service high memory usage" → 2 calls, $0.0039
  - Recall 3 "api-gateway certificate problem"       → 2 calls, $0.0037
  - Seed (17 incidents → graph): 35 calls, $0.0328
  - **TOTAL this run: $0.0435** (well under the $2 hard cap)
- [x] Graph-aware cross-incident reasoning confirmed: Recall 3 reconstructed the full
      manual→automated cert arc across INC-2024-0301, INC-2024-0905, INC-2025-0301.
- [x] Committed: "feat: Phase 2 -- seed 17 incidents into consolidated graph, verified cross-incident recall with cost tracking"

## Phase 3 — (pending)
- [ ] TBD
