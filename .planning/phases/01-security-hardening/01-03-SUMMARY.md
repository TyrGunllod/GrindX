---
phase: 01-security-hardening
plan: 03
subsystem: auth
tags: [secrets, filetype, magic-bytes, temp-password, upload-security]

# Dependency graph
requires: []
provides:
  - Temp password generation with secrets module (16 alphanumeric chars)
  - 15-minute expiry for temporary passwords stored in database
  - Magic bytes validation on file upload endpoints
  - Protection against disguised malicious file uploads
affects: [auth, upload, iam]

# Tech tracking
tech-stack:
  added: [filetype]
  patterns: [magic-bytes-validation, temp-password-with-expiry]

key-files:
  created:
    - apps/api-postgres/alembic/versions/2026_06_02_add_temp_password_fields.py
    - apps/api-postgres/tests/test_auth_security.py
    - apps/api-postgres/tests/test_upload_security.py
  modified:
    - apps/api-postgres/app/auth/service.py
    - apps/api-postgres/app/modules/iam/models/usuario.py
    - apps/api-postgres/app/routers/theme_router.py
    - packages/shared/exceptions/base.py

key-decisions:
  - "CredenciaisInvalidasError now accepts optional custom message for better security feedback"
  - "Auth service checks both regular and temp password hashes on login"
  - "SVG files excluded from magic bytes validation (filetype unreliable for SVG)"

patterns-established:
  - "Temp password flow: generate → hash → store with expiry → verify → clear on use"
  - "Upload validation: content_type check + magic bytes check (except SVG)"

requirements-completed: [SEC-02, SEC-04]

# Metrics
duration: 12min
completed: 2026-06-02
---

# Phase 1 Plan 3: Auth & Upload Security Summary

**Cryptographic temp passwords with 15-min expiry and filetype magic bytes validation on uploads**

## Performance

- **Duration:** 12 min
- **Started:** 2026-06-02T22:49:04Z
- **Completed:** 2026-06-02T23:01:00Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- Temporary passwords generated via `secrets` module (16 alphanumeric chars) with 15-minute expiry stored in DB
- Login with expired temp password rejected with clear error message
- File uploads validate magic bytes via `filetype` library (logos + fonts)
- `.txt` renamed to `.png` returns HTTP 400 with descriptive error

## Task Commits

Each task was committed atomically:

1. **Task 1: Temp password security with expiry (SEC-02)** - `2dbe471` (feat)
2. **Task 2: File upload magic bytes validation (SEC-04)** - `2c3b3e9` (feat)

## Files Created/Modified
- `apps/api-postgres/app/modules/iam/models/usuario.py` - Added `temp_password_hash` and `expires_at` columns
- `apps/api-postgres/app/auth/service.py` - Secure temp password generation, expiry check, dual-hash login
- `apps/api-postgres/alembic/versions/2026_06_02_add_temp_password_fields.py` - Migration for new columns
- `apps/api-postgres/app/routers/theme_router.py` - Magic bytes validation via `_validate_file_magic` helper
- `apps/api-postgres/tests/test_auth_security.py` - 6 tests for temp password security
- `apps/api-postgres/tests/test_upload_security.py` - 4 tests for upload magic bytes validation
- `packages/shared/exceptions/base.py` - CredenciaisInvalidasError accepts optional message

## Decisions Made
- **CredenciaisInvalidasError optional message:** Changed from no-arg to optional message parameter to support descriptive error messages for expired temp passwords vs generic "invalid credentials"
- **Dual-hash login:** Auth service checks both regular `senha_hash` and `temp_password_hash` on login, so users can authenticate directly with temp password without separate apply step
- **SVG excluded from magic bytes:** SVG files use content_type validation only because `filetype` library cannot reliably detect SVG magic bytes

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] CredenciaisInvalidasError custom message support**
- **Found during:** Task 1 (Temp password expiry tests)
- **Issue:** `CredenciaisInvalidasError.__init__()` accepted no arguments, preventing descriptive error messages for expired temp passwords
- **Fix:** Changed to accept optional `message` parameter with default "Usuário ou senha incorretos."
- **Files modified:** `packages/shared/exceptions/base.py`
- **Verification:** Tests pass with custom "expirada" message assertions
- **Committed in:** 2dbe471 (Task 1 commit)

**2. [Rule 1 - Bug] SQLite timezone-naive datetime handling**
- **Found during:** Task 1 (Temp password expiry tests)
- **Issue:** SQLite returns timezone-naive datetimes, causing `TypeError: can't subtract offset-naive and offset-aware datetimes`
- **Fix:** Added `.replace(tzinfo=timezone.utc)` handling for naive datetimes in auth service
- **Files modified:** `apps/api-postgres/app/auth/service.py`
- **Verification:** All 6 auth security tests pass
- **Committed in:** 2dbe471 (Task 1 commit)

**3. [Rule 1 - Bug] Login with temp password not working**
- **Found during:** Task 1 (Temp password acceptance test)
- **Issue:** `autenticar` method only checked `senha_hash`, not `temp_password_hash` — users couldn't login with temp password
- **Fix:** Added dual-hash check: if regular password fails, check temp password hash. On success, update main password and clear temp fields.
- **Files modified:** `apps/api-postgres/app/auth/service.py`
- **Verification:** `test_valid_temp_password_accepted` passes
- **Committed in:** 2dbe471 (Task 1 commit)

---

**Total deviations:** 3 auto-fixed (1 missing critical, 2 bugs)
**Impact on plan:** All auto-fixes necessary for correctness. No scope creep.

## Issues Encountered
- Alembic has multiple heads (001, 0001, 005_add_aba_parent_id) — based new migration on 005_add_aba_parent_id as latest in main chain
- `filetype` package was in requirements.txt but not installed in venv — installed via pip

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- SEC-02 and SEC-04 requirements complete
- Auth service now secure against credential stuffing via temp passwords
- Upload endpoints protected against disguised malicious files

---
*Phase: 01-security-hardening*
*Completed: 2026-06-02*

## Self-Check: PASSED

All files verified:
- `apps/api-postgres/app/modules/iam/models/usuario.py` - FOUND
- `apps/api-postgres/app/auth/service.py` - FOUND
- `apps/api-postgres/alembic/versions/2026_06_02_add_temp_password_fields.py` - FOUND
- `apps/api-postgres/tests/test_auth_security.py` - FOUND
- `apps/api-postgres/tests/test_upload_security.py` - FOUND
- `apps/api-postgres/app/routers/theme_router.py` - FOUND
- `packages/shared/exceptions/base.py` - FOUND
- `.planning/phases/01-security-hardening/01-03-SUMMARY.md` - FOUND

All commits verified:
- `2dbe471` feat(auth): temp password security with expiry (SEC-02)
- `2c3b3e9` feat(upload): magic bytes validation for file uploads (SEC-04)
