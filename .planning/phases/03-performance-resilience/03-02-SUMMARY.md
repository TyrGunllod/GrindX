---
phase: 03-performance-resilience
plan: 02
subsystem: database
tags: [alembic, postgresql, indexes, sqlalchemy, performance]

# Dependency graph
requires:
  - phase: 01-security-hardening
    provides: "IAM and org schema tables with user/theme models"
provides:
  - "Alembic migration with 5 B-tree indexes for common query patterns"
  - "Composite index on company_themes(company_id, is_active)"
  - "Indexes on usuarios(role), usuarios(ativo), usuarios(empresa_id)"
  - "Index on portal_modulos(aba_id)"
  - "Integration tests verifying index definitions on SQLAlchemy models"
affects: [04-deployment-observability, query-performance, database-layer]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Index definitions in __table_args__ with inherited schema preservation"]

key-files:
  created:
    - "apps/api-postgres/alembic/versions/006_add_performance_indexes.py"
    - "apps/api-postgres/tests/integration/test_indexes.py"
  modified:
    - "apps/api-postgres/app/modules/org/models/theme.py"
    - "apps/api-postgres/app/modules/iam/models/usuario.py"
    - "apps/api-postgres/app/modules/portal/models/portal.py"

key-decisions:
  - "Preserved inherited schema settings in __table_args__ tuples (Rule 1 fix)"
  - "Index definitions added to both migration and model for test verification"

patterns-established:
  - "__table_args__ tuple pattern: (Index(...), Index(...), {'schema': 'name'}) preserves inherited schema"

requirements-completed: [PERF-02]

# Metrics
duration: 17min
completed: 2026-06-06
---

# Phase 3 Plan 02: Performance Indexes Summary

**5 B-tree indexes for common query patterns via Alembic migration with model-level Index definitions for test verification**

## Performance

- **Duration:** 17 min
- **Started:** 2026-06-06T21:57:10Z
- **Completed:** 2026-06-06T22:14:23Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Alembic migration creating 5 composite/single-column B-tree indexes for common query patterns
- Index definitions added to SQLAlchemy models (CompanyTheme, Usuario, Modulo) for test-time verification
- Integration tests verifying all index definitions pass with SQLite in-memory

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Alembic migration for performance indexes** - `4e89ca8` (feat)
2. **Task 2: Add integration tests for index existence** - `70fb47d` (test)

## Files Created/Modified
- `apps/api-postgres/alembic/versions/006_add_performance_indexes.py` - Alembic migration with 5 indexes (company_themes composite, usuarios role/ativo/empresa_id, portal_modulos aba_id)
- `apps/api-postgres/tests/integration/test_indexes.py` - 4 integration tests verifying index definitions on models
- `apps/api-postgres/app/modules/org/models/theme.py` - Added Index import and __table_args__ with composite index + schema
- `apps/api-postgres/app/modules/iam/models/usuario.py` - Added Index import and __table_args__ with 3 indexes + schema
- `apps/api-postgres/app/modules/portal/models/portal.py` - Added Index import and __table_args__ with 1 index + schema

## Decisions Made
- Added Index definitions to SQLAlchemy models alongside the migration so tests can verify them without running migrations against a real PostgreSQL database
- Preserved inherited schema settings (`{"schema": "iam"}`, etc.) in `__table_args__` tuples to avoid breaking FK resolution

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Overridden schema in __table_args__ breaks FK resolution**
- **Found during:** Task 2 (Integration tests)
- **Issue:** Adding `__table_args__ = (Index(...),)` to Usuario/CompanyTheme/Modulo models overrode the inherited `{"schema": "iam/org/portal"}` from their base classes, causing SQLAlchemy FK resolution to fail with `NoReferencedTableError`
- **Fix:** Changed `__table_args__` to include the schema dict as the last tuple element: `(Index(...), {"schema": "iam"})`
- **Files modified:** `app/modules/org/models/theme.py`, `app/modules/iam/models/usuario.py`, `app/modules/portal/models/portal.py`
- **Verification:** All 4 integration tests pass, existing test suite unaffected
- **Committed in:** 70fb47d (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Fix was necessary for tests to run. No scope creep — all changes are within the plan's stated deliverables.

## Issues Encountered
None beyond the auto-fixed deviation above.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all indexes are fully defined and verified.

## Next Phase Readiness
- Indexes ready for deployment via `alembic upgrade head`
- Model-level Index definitions enable test verification without real PostgreSQL
- Ready for PERF-01 (caching) and PERF-03 (health checks) plans

---
*Phase: 03-performance-resilience*
*Completed: 2026-06-06*

## Self-Check: PASSED

- [x] `apps/api-postgres/alembic/versions/006_add_performance_indexes.py` exists
- [x] `apps/api-postgres/tests/integration/test_indexes.py` exists
- [x] `.planning/phases/03-performance-resilience/03-02-SUMMARY.md` exists
- [x] Commit `4e89ca8` found in git log
- [x] Commit `70fb47d` found in git log
