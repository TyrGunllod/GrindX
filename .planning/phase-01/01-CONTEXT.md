# Phase 1: Security Hardening - Context

**Gathered:** 2026-06-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Patch all security vulnerabilities in the GrindX ERP system. The application must resist common attack vectors including weak JWT secrets, brute-force attacks, malicious file uploads, and unauthorized cross-origin requests. Both api-postgres and api-sqlserver are in scope.

**Requirements:** SEC-01, SEC-02, SEC-03, SEC-04, SEC-05
**Success Criteria:**
1. SECRET_KEY rejects keys with Shannon entropy below 3.5 bits/character
2. Temp passwords expire after 15 min, generated via `secrets` module
3. Rate limiter blocks by user_id, not just IP
4. File uploads reject mismatched magic bytes
5. CORS production mode rejects unlisted origins

</domain>

<decisions>
## Implementation Decisions

### SECRET_KEY Entropy Validation (SEC-01)
- **Validator location:** Pydantic `field_validator` on Settings class — validates at initialization, fails fast
- **Entropy method:** Shannon entropy using `math.log2` — no extra dependencies
- **Threshold:** 3.5 bits/character minimum (research-backed recommendation)
- **Existing .env handling:** Auto-generate strong key in dev mode if current key is weak; fail in production
- **Implementation:** Add `@field_validator("SECRET_KEY")` that calculates Shannon entropy, raises `ValueError` if below threshold

### Temporary Password Security (SEC-02)
- **Storage:** `expires_at` field on Usuario model — persistent, works with multiple instances
- **Expiry duration:** 15 minutes from generation
- **Format:** 16 alphanumeric characters using `secrets` module (not `token_hex`)
- **Login flow:** Check expiry on login attempt — reject expired temp passwords with clear error message
- **Forced change:** After successful login with temp password, force password change (existing behavior)

### Rate Limiting Architecture (SEC-03)
- **Library:** SlowAPI — supports dual keys (IP + user_id), easy FastAPI integration
- **Storage:** In-memory — simple, no external dependencies, sufficient for current scale
- **Key strategy:** IP-based for unauthenticated endpoints, user_id-based for authenticated endpoints
- **Threshold:** Configurable via env vars (RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)
- **Both APIs:** Apply to api-postgres AND api-sqlserver (shared middleware pattern)

### File Upload Validation (SEC-04)
- **Scope:** Logos and fonts only — existing endpoints in theme_router
- **Library:** `filetype` — pure Python, no system dependencies, works on Windows
- **Existing uploads:** No migration — validate only new uploads
- **Validation:** Check magic bytes match declared file type; reject mismatches with HTTP 400
- **Both APIs:** Apply to api-postgres (main upload handler); api-sqlserver has no uploads

### CORS Configuration (SEC-05)
- **Mode:** Strict production — never `*` in prod, explicit origin list required
- **Config source:** `CORS_ORIGINS` env var — comma-separated list
- **Environment awareness:** Dev mode allows `*` for convenience; production requires explicit list
- **Validation:** Parse and validate origins at startup; reject invalid URLs
- **Both APIs:** Apply to api-postgres AND api-sqlserver

### Agent's Discretion
- **Error messages:** Portuguese (BR) to match existing codebase conventions
- **Logging:** Use structlog for all security events (failed validations, rate limit hits)
- **Testing:** Each fix must have unit test validating the new behavior
- **Backward compatibility:** Existing .env files with weak keys auto-fixed in dev, fail in prod

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Project goals, constraints, and key decisions
- `.planning/REQUIREMENTS.md` — v1 requirements with SEC-01 through SEC-05
- `.planning/ROADMAP.md` — Phase structure and success criteria

### Codebase Maps
- `.planning/codebase/STACK.md` — Current technology stack and dependencies
- `.planning/codebase/ARCHITECTURE.md` — System architecture and data flow
- `.planning/codebase/CONCERNS.md` — Original concerns (source of truth for what to fix)
- `.planning/codebase/CONVENTIONS.md` — Code style and naming conventions

### Research
- `.planning/research/SUMMARY.md` — Research synthesis with stack recommendations
- `.planning/research/STACK.md` — Detailed library recommendations (SlowAPI, filetype, etc.)
- `.planning/research/PITFALLS.md` — Critical pitfalls to avoid during implementation

### Key Source Files
- `apps/api-postgres/app/core/config.py` — Settings class with SECRET_KEY validation
- `apps/api-postgres/app/auth/service.py` — AuthService with temp password generation
- `apps/api-postgres/app/middleware/rate_limit.py` — Current rate limiting implementation
- `apps/api-postgres/app/routers/theme_router.py` — File upload endpoints (logos, fonts)
- `apps/api-sqlserver/app/core/config.py` — SQL Server API config (similar structure)
- `apps/api-sqlserver/app/middleware/rate_limit.py` — SQL Server rate limiting

</canonical_refs>

<specifics>
## Specific Ideas

- **Shannon entropy formula:** `sum(-p * math.log2(p) for p in char_frequencies)` where `p` is character frequency
- **SlowAPI integration:** `from slowapi import Limiter, _rate_limit_exceeded_handler` with `key_func=get_remote_address`
- **filetype usage:** `filetype.guess(file_bytes)` returns `None` if unknown; check `kind.mime` against allowed types
- **CORS parsing:** `settings.CORS_ORIGINS.split(",")` with `.strip()` for each origin

</specifics>

<deferred>
## Deferred Ideas

- **JWT token invalidation:** Token version field or Redis blacklist — deferred to v2 (SEC-06)
- **Path traversal protection:** Full path validation beyond `os.path.join` — deferred to v2 (SEC-07)
- **Security headers:** CSP, HSTS, X-Frame-Options — deferred to v2 (SEC-08)
- **CSRF protection:** Not needed for JWT in Authorization header — defense is CSP + short-lived tokens

</deferred>

---

*Phase: 01-security-hardening*
*Context gathered: 2026-06-02*
