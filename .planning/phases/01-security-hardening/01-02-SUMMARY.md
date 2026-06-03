---
phase: 01-security-hardening
plan: 02
subsystem: api
tags: [rate-limiting, slowapi, limits, middleware, security]

# Dependency graph
requires:
  - phase: none
    provides: n/a
provides:
  - Dual key rate limiting (user_id + IP) for both APIs
  - SlowAPI/limits library integration
  - 5 integration tests for rate limiting behavior
affects: [api-postgres, api-sqlserver, security]

# Tech tracking
tech-stack:
  added: [slowapi, limits]
  patterns: [dual-key-rate-limiting, middleware-with-lazy-config]

key-files:
  created:
    - apps/api-postgres/tests/test_rate_limit.py
  modified:
    - apps/api-postgres/app/middleware/rate_limit.py
    - apps/api-postgres/requirements.txt
    - apps/api-sqlserver/app/middleware/rate_limit.py
    - apps/api-sqlserver/requirements.txt

key-decisions:
  - "Used limits library (SlowAPI internals) instead of SlowAPI's decorator pattern — preserves existing middleware class interface"
  - "JWT decoded directly in middleware for user_id extraction — avoids dependency on request.state.user which is set after middleware"
  - "Singleton MemoryStorage shared across middleware instances — consistent rate limiting state"

patterns-established:
  - "Dual key rate limiting: user_id for authenticated, IP for unauthenticated endpoints"
  - "Lazy-loaded SECRET_KEY in middleware to avoid circular imports"

requirements-completed: [SEC-03]

# Metrics
duration: 7min
completed: 2026-06-02
---

# Phase 01 Plan 02: Rate Limiting Summary

**SlowAPI dual-key rate limiter: user_id-based for authenticated endpoints, IP-based for unauthenticated, applied to both APIs**

## Performance

- **Duration:** 7 min
- **Started:** 2026-06-02T22:52:27Z
- **Completed:** 2026-06-02T22:59:04Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Replaced custom sliding-window rate limiter with SlowAPI/limits library in both APIs
- Implemented dual key strategy: authenticated users keyed by user_id, unauthenticated by IP
- Two users from same IP get independent rate limits (per-account brute-force defense)
- 5 integration tests verify IP limiting, user limiting, independent limits, excluded paths, and headers

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace custom rate limiter with SlowAPI (api-postgres)** - `2428349` (feat)
2. **Task 2: Apply SlowAPI rate limiting to api-sqlserver** - `3e5bc8b` (feat)

## Files Created/Modified
- `apps/api-postgres/app/middleware/rate_limit.py` - Rewritten with limits library, dual key strategy (user_id + IP)
- `apps/api-postgres/requirements.txt` - Added slowapi>=0.1.9
- `apps/api-postgres/tests/test_rate_limit.py` - 5 integration tests for rate limiting behavior
- `apps/api-sqlserver/app/middleware/rate_limit.py` - Same dual key implementation as api-postgres
- `apps/api-sqlserver/requirements.txt` - Added slowapi>=0.1.9

## Decisions Made
- Used `limits` library (SlowAPI internals) directly instead of SlowAPI's decorator pattern — preserves the existing `RateLimitMiddleware` class interface that `main.py` already uses
- JWT decoded directly in middleware via `jose.jwt.decode` for user_id extraction — `request.state.user` is not available at middleware level (set by FastAPI dependencies after middleware)
- Singleton `MemoryStorage` instance at module level — consistent state across all middleware instances
- Lazy-loaded `SECRET_KEY` to avoid circular import between middleware and config

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Recreated broken api-sqlserver venv**
- **Found during:** Pre-task setup
- **Issue:** api-sqlserver `.venv` pointed to non-existent `C:\Program Files\Python3.12\python.exe`
- **Fix:** Recreated venv using available Python 3.13, reinstalled all dependencies
- **Files modified:** `apps/api-sqlserver/.venv/` (recreated)
- **Verification:** `python -c "from app.main import app"` succeeds
- **Committed in:** N/A (environment fix, not code change)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Environment fix required before Task 2 verification. No code changes needed.

## Issues Encountered
None — plan executed smoothly.

## Known Stubs
None — all functionality is fully wired.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| T-02-02 (accepted) | rate_limit.py | IP-based limiting uses X-Forwarded-For which is attacker-controlled — accepted per threat model; user_id-based is the real defense for authenticated endpoints |

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Rate limiting complete for both APIs (SEC-03 satisfied)
- Ready for next security hardening plan (file upload validation, CORS)

## Self-Check: PASSED

- All 5 created/modified files exist
- Both commit hashes (2428349, 3e5bc8b) found in git log
- 18 tests pass (5 rate limit + 6 auth security + 7 config security)
- No regressions detected

---
*Phase: 01-security-hardening*
*Completed: 2026-06-02*
