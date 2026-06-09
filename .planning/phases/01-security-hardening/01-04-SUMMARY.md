---
phase: 01-security-hardening
plan: 04
subsystem: auth
tags: [security, fail-closed, temp-password, expiry]

requires:
  - phase: 01-security-hardening
    provides: "Auth service with temp password support"
provides:
  - "Fail-closed temp password expiry check in autenticar()"
  - "Fail-closed temp password expiry check in apply_temp_password()"
  - "Tests validating fail-closed behavior when expires_at is None"
affects: [01-security-hardening]

tech-stack:
  added: []
  patterns: [fail-closed-security]

key-files:
  created: []
  modified:
    - apps/api-postgres/app/auth/service.py
    - apps/api-postgres/tests/test_auth_security.py

key-decisions:
  - "Fail-closed pattern: reject temp password when expires_at is None instead of accepting it"
  - "Both autenticar() and apply_temp_password() use identical fail-closed logic"

patterns-established:
  - "Fail-closed security: when a security field is missing (None), reject rather than accept"

requirements-completed: [SEC-02]

duration: 4min
completed: 2026-06-06
---

# Phase 1 Plan 4: Fail-Closed Temp Password Expiry Summary

**Fixed fail-open temp password expiry: rejects login when expires_at is None instead of accepting indefinitely**

## Performance

- **Duration:** 4 min
- **Started:** 2026-06-06T23:37:19Z
- **Completed:** 2026-06-06T23:41:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Fixed security vulnerability where temp passwords without expiry were accepted indefinitely
- Both `autenticar()` and `apply_temp_password()` now use fail-closed logic
- Two new tests validate the fail-closed behavior for both methods

## Task Commits

Each task was committed atomically:

1. **Task 1: Add fail-closed test for expires_at=None** - `04746c1` (test)
2. **Task 2: Fix fail-open expiry check** - `7dec64d` (fix)

## Files Created/Modified
- `apps/api-postgres/app/auth/service.py` - Fail-closed expiry check in both autenticar() and apply_temp_password()
- `apps/api-postgres/tests/test_auth_security.py` - Two new tests for expires_at=None case

## Decisions Made
- Fail-closed pattern: when `expires_at` is None, reject temp password with "expirada" message and clear temp fields
- Both methods use identical logic: check None first, then check past expiry

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- UAT gap 8 (temp password expiry) is now closed
- Fail-closed behavior prevents indefinite temp password usage when expires_at is missing

---
*Phase: 01-security-hardening*
*Completed: 2026-06-06*

## Self-Check: PASSED

- [x] Commit `04746c1` exists (test: add failing tests)
- [x] Commit `7dec64d` exists (fix: fail-closed expiry check)
- [x] SUMMARY.md created at `.planning/phases/01-security-hardening/01-04-SUMMARY.md`
