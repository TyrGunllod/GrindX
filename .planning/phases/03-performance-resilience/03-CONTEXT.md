# Phase 3: Performance & Resilience - Context

**Gathered:** 2026-06-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Add performance optimizations and resilience to the GrindX ERP system. The application must respond quickly under load and report accurate health status for container orchestration. Both api-postgres and api-sqlserver are in scope.

**Requirements:** PERF-01, PERF-02, PERF-03
**Success Criteria:**
1. Cached queries return from cache on second request within TTL
2. Common queries use indexes (EXPLAIN shows index scan)
3. Health endpoint returns 200 when DB reachable, 503 when unreachable

</domain>

<decisions>
## Implementation Decisions

### Cache Strategy (PERF-01)
- **Library:** cachetools — in-memory cache, no external dependencies
- **Queries to cache:**
  - `GET /v1/themes/active` — active themes per company
  - `GET /v1/portal/abas` — portal modules
  - `GET /v1/usuarios/{id}` — user data
- **TTL:** 15 minutes (balance between performance and freshness)
- **Invalidation:** TTL only — cache expires naturally, no write-through invalidation
- **Both APIs:** Apply to api-postgres (main API); api-sqlserver read-only so caching less critical

### Index Strategy (PERF-02)
- **Index types:** B-tree only (standard for equality and range queries)
- **Columns to index:** Let researcher decide based on query analysis
- **Migration:** New Alembic migration for index creation
- **Verification:** EXPLAIN queries should show index scan after migration

### Health Check Depth (PERF-03)
- **Checks:**
  - PostgreSQL connectivity
  - SQL Server connectivity
  - Schema validation (verify main tables exist)
- **Behavior:** Fail-fast — 503 if any DB unavailable
- **Response format:** `{"status": "healthy"}` or `{"status": "degraded", "details": {...}}`
- **Both APIs:** Apply to api-postgres AND api-sqlserver

### Agent's Discretion
- **Error messages:** Portuguese (BR) to match existing codebase conventions
- **Logging:** Use structlog for health check events
- **Testing:** Each feature must have unit test validating behavior

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Project goals, constraints, and key decisions
- `.planning/REQUIREMENTS.md` — v1 requirements with PERF-01 through PERF-03
- `.planning/ROADMAP.md` — Phase structure and success criteria

### Codebase Maps
- `.planning/codebase/STACK.md` — Current technology stack and dependencies
- `.planning/codebase/ARCHITECTURE.md` — System architecture and data flow
- `.planning/codebase/CONCERNS.md` — Original concerns (source of truth for what to fix)
- `.planning/codebase/CONVENTIONS.md` — Code style and naming conventions

### Research
- `.planning/research/SUMMARY.md` — Research synthesis with stack recommendations
- `.planning/research/STACK.md` — Detailed library recommendations (cachetools, etc.)

### Key Source Files
- `apps/api-postgres/app/routers/theme_router.py` — Theme endpoints to cache
- `apps/api-postgres/app/routers/health_router.py` — Current health check
- `apps/api-postgres/app/repositories/` — Repository layer for cache integration
- `apps/api-postgres/app/modules/` — SQLAlchemy models for index definitions
- `apps/api-sqlserver/app/routers/health_router.py` — SQL Server health check

</canonical_refs>

<specifics>
## Specific Ideas

- **cachetools usage:** `from cachetools import TTLCache; cache = TTLCache(maxsize=100, ttl=900)` (900 seconds = 15 min)
- **Cache decorator pattern:** `@cached(cache)` on repository methods
- **Health check endpoint:** `GET /health` returns `{"status": "healthy", "database": {"postgres": "ok", "sqlserver": "ok"}}`
- **Index naming:** `ix_{table}_{column}` convention

</specifics>

<deferred>
## Deferred Ideas

- **Redis cache:** Deferred to v2 — adds infrastructure complexity
- **Async SQLAlchemy:** Deferred — refactoring too large for this phase
- **Frontend lazy loading:** Deferred — not in scope for this phase
- **Connection pooling for SQL Server:** Deferred — needs investigation

</deferred>

---

*Phase: 03-performance-resilience*
*Context gathered: 2026-06-06*
