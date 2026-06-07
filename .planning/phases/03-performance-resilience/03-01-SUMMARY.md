---
phase: 03-performance-resilience
plan: 01
subsystem: database
tags: [cache, cachetools, ttlcache, performance, threading]

# Dependency graph
requires:
  - phase: 02-infrastructure-quality
    provides: "pytest-cov configured, migration consolidation done"
provides:
  - "In-memory cache layer with cachetools TTLCache (theme, portal, user)"
  - "Cached repository methods for frequent queries"
  - "Cache invalidation on write operations"
  - "Thread-safe cache access with locks"
affects: [03-performance-resilience]

# Tech tracking
tech-stack:
  added: [cachetools>=7.1.0]
  patterns: [TTLCache at repository layer, get_or_set helper, cache invalidation on writes]

key-files:
  created:
    - apps/api-postgres/app/core/cache.py
    - apps/api-postgres/tests/unit/test_cache.py
  modified:
    - apps/api-postgres/requirements.txt
    - apps/api-postgres/app/repositories/theme_repository.py
    - apps/api-postgres/app/repositories/usuario_repository.py
    - apps/api-postgres/app/routers/portal_router.py
    - apps/api-postgres/tests/conftest.py

key-decisions:
  - "Cache at repository layer (close to data access, not business logic)"
  - "TTL-only invalidation — eventual consistency with 15-min staleness accepted"
  - "Cache None results to prevent cache penetration attacks"
  - "autouse fixture _clear_cache in conftest.py for test isolation"

patterns-established:
  - "get_or_set(cache, lock, key, fetch_fn): Thread-safe cache-or-fetch pattern"
  - "invalidate(cache, lock, key): Targeted cache invalidation on writes"
  - "clear_all(): Global cache reset for testing"

requirements-completed: [PERF-01]

# Metrics
duration: 12min
completed: 2026-06-06
---

# Phase 3 Plan 1: In-Memory Cache Summary

**cachetools TTLCache at repository layer for theme, portal, and user queries with 15-min TTL and thread-safe access**

## Performance

- **Duration:** 12 min
- **Started:** 2026-06-06T21:57:41Z
- **Completed:** 2026-06-06T22:10:00Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- In-memory cache layer with 3 TTLCache instances (theme, portal, user) at 15-min TTL
- ThemeRepository.find_active_by_company_id serves from cache on second call
- UsuarioRepository.buscar_por_id and buscar_por_username serve from cache on second call
- Portal /menu endpoint caches active Aba query (base query only, tree built per-request)
- Cache invalidation on all write operations (activate_theme, update/delete user, create/update/delete aba)
- Thread-safe access with per-cache threading.Lock
- 15 unit tests covering cache hit/miss/TTL/invalidation/repository integration

## Task Commits

Each task was committed atomically:

1. **Task 1: Install cachetools and create cache module** - `7d0f636` (feat)
2. **Task 2: Add caching to repositories and portal router** - `340190e` (feat)

## Files Created/Modified
- `apps/api-postgres/app/core/cache.py` - Cache module: 3 TTLCache instances, get_or_set/invalidate/clear_all helpers
- `apps/api-postgres/tests/unit/test_cache.py` - 15 unit tests for cache behavior and repository integration
- `apps/api-postgres/requirements.txt` - Added cachetools>=7.1.0
- `apps/api-postgres/app/repositories/theme_repository.py` - find_active_by_company_id uses cache, activate_theme invalidates
- `apps/api-postgres/app/repositories/usuario_repository.py` - buscar_por_id/username use cache, update/delete invalidate
- `apps/api-postgres/app/routers/portal_router.py` - /menu caches active Abas, write endpoints invalidate
- `apps/api-postgres/tests/conftest.py` - autouse _clear_cache fixture for test isolation

## Decisions Made
- **Cache at repository layer:** Close to data access, not business logic — follows architectural responsibility map from research
- **TTL-only invalidation:** Accept 15-min staleness for simplicity — write-through invalidation deferred to v2 per CONTEXT.md decision
- **Cache None results:** Prevents cache penetration — attackers can't flood with non-existent keys
- **autouse _clear_cache fixture:** Prevents cache leakage between tests — discovered during regression testing

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed cache leakage between tests**
- **Found during:** Task 2 (regression testing)
- **Issue:** Existing repository tests failed because cached values from one test leaked to the next (test_find_active_returns_none_if_no_theme got a cached result from test_find_active_by_company_id)
- **Fix:** Added autouse `_clear_cache` fixture in conftest.py that calls `clear_all()` before and after each test
- **Files modified:** apps/api-postgres/tests/conftest.py
- **Verification:** All 22 existing repository tests pass, all 15 new cache tests pass
- **Committed in:** 340190e (Task 2 commit)

**2. [Rule 3 - Blocking] Formatted cache.py with ruff**
- **Found during:** Task 1 (lint verification)
- **Issue:** cache.py had formatting inconsistencies detected by `ruff format --check`
- **Fix:** Ran `ruff format app/core/cache.py`
- **Files modified:** apps/api-postgres/app/core/cache.py
- **Verification:** `ruff format --check` passes on all files
- **Committed in:** 7d0f636 (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Cache isolation fix essential for test correctness. No scope creep.

## Issues Encountered
None — plan executed smoothly after cache isolation fix.

## User Setup Required
None - no external service configuration required. cachetools is in-memory, no Redis or external cache needed.

## Known Stubs
None — all cache methods are fully wired to repository queries and portal endpoints.

## Threat Flags
No new threat surface beyond what's documented in the plan's threat_model (T-03-01 through T-03-SC).

## Next Phase Readiness
- PERF-01 complete — in-memory cache layer operational
- Ready for PERF-02 (database indexing) and PERF-03 (deep health checks)
- Cache layer can be extended with additional cache instances as needed

---
*Phase: 03-performance-resilience*
*Completed: 2026-06-06*

## Self-Check: PASSED

- [x] apps/api-postgres/app/core/cache.py exists
- [x] apps/api-postgres/tests/unit/test_cache.py exists
- [x] .planning/phases/03-performance-resilience/03-01-SUMMARY.md exists
- [x] Commit 7d0f636 exists (Task 1)
- [x] Commit 340190e exists (Task 2)
