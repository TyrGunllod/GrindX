# Domain Pitfalls

**Domain:** FastAPI + PostgreSQL + SQLAlchemy ERP Refactoring
**Researched:** 2026-06-02
**Overall confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Schema Translate Map Blindness

**What goes wrong:** Tests pass with SQLite in-memory using `schema_translate_map` but production fails because PostgreSQL schemas (`iam`, `portal`, `catalogo`, `org`) behave differently than `None` schema in SQLite.

**Why it happens:** The `_SCHEMA_TRANSLATE = {"iam": None, "portal": None, "catalogo": None, "org": None}` mapping in `conftest.py:26` silently strips schema prefixes. SQLite doesn't support schemas, so cross-schema queries, foreign keys between schemas, and schema-specific PostgreSQL features (like `SET search_path`) are never tested.

**Consequences:**
- Schema-qualified table references work in tests but fail in production
- New schemas added without updating `_SCHEMA_TRANSLATE` cause silent test failures
- PostgreSQL-specific SQL (e.g., `ALTER TABLE iam.usuarios`) passes SQLite but fails in production
- Foreign key constraints between schemas are not enforced in SQLite

**Prevention:**
1. **Always update `_SCHEMA_TRANSLATE` when adding new schemas** — add a lint check or pre-commit hook that validates schema coverage
2. **Add at least one integration test against real PostgreSQL** (can use testcontainers or a CI service container)
3. **Document all schemas in a central registry** and cross-reference with test fixtures
4. **Test schema-specific operations explicitly** — don't assume SQLite behavior matches PostgreSQL

**Detection:** Run `grep -r "schema_translate_map" apps/api-postgres/tests/` and compare against all schema names in `app/modules/*/base.py`. Any mismatch is a risk.

**Phase mapping:** Phase 2 (Technical Debt) — must fix before adding new features

---

### Pitfall 2: JWT Token Invalidation Impossibility

**What goes wrong:** After security hardening (e.g., password change, account deactivation, role downgrade), existing JWT tokens remain valid until expiration. Users retain access for up to 30 minutes (access token) or 7 days (refresh token).

**Why it happens:** JWT tokens are stateless — `verificar_jwt()` in `packages/shared/security/jwt.py` only validates signature and expiration. There's no token blacklist, no token version check, and no server-side session state. The `refresh_token()` method in `auth/service.py:66` checks if user is active, but the access token itself has no such check.

**Consequences:**
- Deactivated users can continue making requests for 30 minutes
- Compromised tokens cannot be revoked without changing SECRET_KEY (invalidates ALL tokens)
- Role changes don't take effect until token refresh
- Password changes don't invalidate existing sessions

**Prevention:**
1. **Add `token_version` field to Usuario model** — increment on password change/deactivation, include in JWT payload, validate on each request
2. **For immediate revocation:** implement a Redis-backed token blacklist with TTL matching token expiration
3. **Shorten access token lifetime** to 15 minutes or less for sensitive operations
4. **On password change:** increment token_version to invalidate all existing tokens
5. **On account deactivation:** increment token_version immediately

**Detection:** Test: change user password → old token still works = pitfall present.

**Phase mapping:** Phase 1 (Security) — must address during security hardening

---

### Pitfall 3: Rate Limiting Bypass via IP Spoofing

**What goes wrong:** The current rate limiter (`middleware/rate_limit.py`) uses `X-Forwarded-For` header for IP extraction, which is trivially spoofable. Attackers bypass rate limiting by rotating fake IPs in the header.

**Why it happens:** The `_get_client_ip()` method at line 48-53 trusts `X-Forwarded-For` without validation. In production behind a reverse proxy, this header is attacker-controlled. The rate limiter stores counters per IP, so spoofing a new IP resets the counter.

**Consequences:**
- Brute force attacks on `/v1/auth/token` are unimpeded
- Password recovery endpoint can be abused
- API can be overwhelmed despite rate limiting being "enabled"
- False sense of security

**Prevention:**
1. **Configure trusted proxies** — only accept `X-Forwarded-For` from known proxy IPs
2. **Use `request.client.host` as primary** and only trust forwarded headers from configured proxies
3. **Add user-based rate limiting** — rate limit by authenticated user ID, not just IP
4. **For auth endpoints:** add stricter limits (e.g., 5 attempts per username per 15 minutes)
5. **Consider using `X-Real-IP`** set by nginx/traefik instead of `X-Forwarded-For`

**Detection:** Send requests with rotating `X-Forwarded-For` headers → all succeed = bypass present.

**Phase mapping:** Phase 1 (Security) — critical security fix

---

### Pitfall 4: File Upload Magic Byte Bypass

**What goes wrong:** Font upload validation (`theme_router.py:350-357`) only checks file extension. Logo upload checks `content_type` but not magic bytes. Attackers upload malicious files (e.g., PHP shells, HTML with XSS) disguised as fonts/logos.

**Why it happens:** Extension checking is trivially bypassable (rename `malware.php` to `malware.ttf`). Content-Type headers are client-controlled and unreliable. Magic bytes (file signatures) are the only reliable content verification.

**Consequences:**
- Malicious file execution if uploads directory is web-accessible
- XSS via uploaded HTML/SVG files served with wrong Content-Type
- Server-side code execution if file is processed by vulnerable parser
- Path traversal if filename is used in file operations without sanitization

**Prevention:**
1. **Validate magic bytes** — check file signatures (e.g., TTF starts with `\x00\x01\x00\x00`, OTF with `OTTO`)
2. **Generate random filenames** — already done with UUID (line 373), good
3. **Store uploads outside webroot** or configure web server to not execute uploaded files
4. **Set `Content-Disposition: attachment`** for served uploads to prevent inline execution
5. **Scan uploads with ClamAV or similar** for known malware signatures
6. **Validate file structure** — try parsing the font file with a library like `fonttools`

**Detection:** Upload a file with `.ttf` extension but PNG magic bytes → accepted = pitfall present.

**Phase mapping:** Phase 1 (Security) — must fix during security hardening

---

### Pitfall 5: Alembic Migration Ordering Chaos

**What goes wrong:** Multiple migration files with `001` prefix (`001_create_tables.py`, `001_initial_schema.py`, `0001_criar_tabela_projetos.py`) cause Alembic to apply migrations in unpredictable order or fail with "multiple heads" error.

**Why it happens:** Alembic determines migration order from `down_revision` chains in each migration file, not from filenames. When multiple files claim to be the first migration (no `down_revision`), Alembic creates multiple heads. The `001` prefix is misleading — it's not used for ordering.

**Consequences:**
- `alembic upgrade head` fails with "multiple heads" error
- CI/CD pipeline breaks on fresh database creation
- Different developers get different database states depending on which migration runs first
- Data loss if migrations are applied in wrong order

**Prevention:**
1. **Run `alembic heads` to detect multiple heads** — should always return exactly one
2. **Merge heads with `alembic merge`** — create a merge migration to consolidate branches
3. **Use sequential numeric prefixes** — `001_`, `002_`, `003_` for human readability, but rely on `down_revision` for actual ordering
4. **Add CI check:** `alembic check` should pass (no pending migrations, no multiple heads)
5. **Never edit existing migration files** — always create new migrations for changes

**Detection:** Run `alembic heads` → multiple lines = problem exists.

**Phase mapping:** Phase 2 (Technical Debt) — must fix before adding new migrations

---

## Moderate Pitfalls

### Pitfall 6: CORS Wildcard in Production

**What goes wrong:** `CORS_ORIGINS` config (`config.py:39`) defaults to `"http://localhost:3000"` but CI uses `["*"]`. If production environment accidentally uses wildcard, any website can make authenticated requests.

**Why it happens:** The `allowed_origins_list` property (line 72-82) parses the string value. If someone sets `CORS_ORIGINS=["*"]` in production `.env`, all origins are allowed. The `allow_credentials=True` setting combined with `allow_origins=["*"]` is particularly dangerous — it allows any site to send cookies.

**Consequences:**
- Any website can make API requests on behalf of authenticated users
- CSRF attacks become trivial
- Data exfiltration from authenticated sessions

**Prevention:**
1. **Validate CORS_ORIGINS at startup** — reject `["*"]` when `allow_credentials=True`
2. **Use `allow_origin_regex`** for pattern matching instead of wildcards
3. **Add environment-specific validation** — production must have explicit origins
4. **Log CORS configuration at startup** for audit trail
5. **Never combine `allow_credentials=True` with `allow_origins=["*"]`** — FastAPI/Starlette should reject this, but validate explicitly

**Detection:** Check production `.env` for `CORS_ORIGINS=*` or `CORS_ORIGINS=["*"]`.

**Phase mapping:** Phase 1 (Security) — fix during CORS hardening

---

### Pitfall 7: Connection Pool Exhaustion Under Load

**What goes wrong:** `database.py` configures `pool_size=10, max_overflow=20` (total 30 connections). Under concurrent load, all connections are consumed and new requests timeout with `QueuePool limit reached`.

**Why it happens:** Each request holds a connection for the entire request duration. Slow queries, missing indexes, or long-running transactions hold connections longer. The `pool_recycle=1800` (30 min) only prevents stale connections, not exhaustion.

**Consequences:**
- API becomes unresponsive under moderate load
- Health checks fail, triggering container restarts
- Cascading failures across dependent services
- SQL Server API (`api-sqlserver`) has no pool configuration at all

**Prevention:**
1. **Monitor connection pool metrics** — log pool size, checked out, overflow
2. **Set appropriate pool sizes** — `pool_size = 2 * CPU cores`, `max_overflow = 10`
3. **Use connection timeouts** — `pool_timeout=30` is good, but consider lower for health checks
4. **Optimize slow queries** — add indexes, use `selectinload` for relationships
5. **Configure SQL Server pool** — currently missing in `api-sqlserver/app/database.py`
6. **Add circuit breaker** — fail fast when pool is exhausted instead of queuing

**Detection:** Load test with 50+ concurrent users → timeout errors = pool exhaustion.

**Phase mapping:** Phase 3 (Performance) — address during performance optimization

---

### Pitfall 8: Test Coverage False Confidence

**What goes wrong:** High test coverage percentage (e.g., 90%) gives false confidence. Tests pass but production fails because tests use SQLite, mock services, and don't test error paths.

**Why it happens:**
- SQLite doesn't enforce PostgreSQL constraints (CHECK, EXCLUDE, partial indexes)
- Mocked services return ideal responses, hiding integration issues
- Tests only cover happy paths (create → success, not create → database timeout)
- `schema_translate_map` hides schema-related bugs
- No tests for concurrent access, race conditions, or connection failures

**Consequences:**
- Production crashes on PostgreSQL-specific SQL
- Integration failures between services not caught
- Edge cases (duplicate emails, concurrent updates) untested
- Security vulnerabilities in error handling paths

**Prevention:**
1. **Test error paths explicitly** — what happens when DB is down? When duplicate key?
2. **Add property-based testing** with Hypothesis for input validation
3. **Test with real PostgreSQL in CI** — use testcontainers or service containers
4. **Test concurrent access** — use threading in tests for race condition detection
5. **Coverage ≠ quality** — measure branch coverage, not just line coverage
6. **Add mutation testing** — use `mutmut` to verify tests catch real bugs

**Detection:** Run `mutmut run` → many surviving mutations = weak tests.

**Phase mapping:** Phase 2 (Technical Debt) — improve test quality during coverage setup

---

### Pitfall 9: Secret Key Weak Validation

**What goes wrong:** `SECRET_KEY` validation (`config.py:28-35`) only checks `len(v) < 32`. A key like `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` (32 a's) passes validation but has near-zero entropy.

**Why it happens:** Length check is necessary but insufficient. Entropy measures randomness quality, not just quantity. A predictable key allows JWT forgery — attackers can sign arbitrary tokens.

**Consequences:**
- JWT tokens can be forged if key is predictable
- All authentication is compromised
- Attacker can impersonate any user, including admin

**Prevention:**
1. **Check entropy** — use `secrets.token_hex(32)` to generate, validate minimum entropy score
2. **Reject common patterns** — all same character, sequential characters, dictionary words
3. **Validate at startup** — fail fast if key is weak
4. **Rotate keys periodically** — implement key rotation mechanism
5. **Use environment-specific keys** — never share dev key with production

**Detection:** Set `SECRET_KEY=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` → app starts = weak validation.

**Phase mapping:** Phase 1 (Security) — fix during SECRET_KEY hardening

---

### Pitfall 10: Temporary Password Security Holes

**What goes wrong:** `forgot_password()` in `auth/service.py:152-159` generates `token_hex(6)` (12 hex chars) with no expiry and no forced password change. The temp password is returned in the function response but never stored or validated.

**Why it happens:** The method generates a temp password and returns it, but `apply_temp_password()` (line 161-167) is a separate call that's never enforced. There's no mechanism to:
- Expire the temp password after X minutes
- Force password change on next login
- Prevent temp password reuse
- Rate limit password recovery attempts

**Consequences:**
- Brute force on 12 hex chars (16^12 = 281 trillion) is feasible with GPU
- No expiry means temp password is valid indefinitely
- No forced change means user keeps temp password as permanent
- Recovery endpoint can be spammed

**Prevention:**
1. **Use `secrets.token_urlsafe(32)`** — 32 bytes of entropy, URL-safe
2. **Store temp password hash with expiry** — add `temp_password_hash` and `temp_password_expires` fields to Usuario
3. **Force password change on login** — add `must_change_password` flag
4. **Rate limit recovery endpoint** — 3 attempts per email per hour
5. **Send temp password via email only** — don't return in API response
6. **Invalidate temp password after use** — single use only

**Phase mapping:** Phase 1 (Security) — fix during password recovery hardening

---

## Minor Pitfalls

### Pitfall 11: SQLAlchemy Session Leaks in Dependencies

**What goes wrong:** If a FastAPI dependency yields a session and the endpoint raises an exception before consuming the generator, the session may not be closed properly.

**Why it happens:** The `get_db()` dependency (`database.py:40-53`) uses try/finally correctly, but if the generator is not fully consumed (e.g., middleware raises before reaching the endpoint), cleanup may not run.

**Consequences:**
- Connection pool slowly drains
- Database connections held open longer than necessary
- Eventually causes pool exhaustion

**Prevention:**
1. **Use `contextmanager` pattern** — already done correctly in `get_db()`
2. **Add middleware to catch unhandled exceptions** and ensure cleanup
3. **Monitor open connections** — log connection count periodically
4. **Use `expire_on_commit=False`** — already set in `SessionLocal` (good)

**Phase mapping:** Phase 3 (Performance) — address during connection pool tuning

---

### Pitfall 12: Frontend Global State Race Condition

**What goes wrong:** `window.grindx` global (`app.js:228`) is accessed by all modules. If scripts load out of order (iframe timing), modules may access undefined properties or stale state.

**Why it happens:** iframes load asynchronously. Module A might try to use `window.grindx.theme` before Module B has loaded it. No synchronization mechanism exists.

**Consequences:**
- Intermittent UI glitches
- Theme not applied to some modules
- API service not initialized when module loads

**Prevention:**
1. **Use `DOMContentLoaded` or `load` events** — ensure parent is ready before modules
2. **Implement a simple event bus** — modules emit "ready" events, parent coordinates
3. **Use `postMessage` for iframe communication** — more robust than shared globals
4. **Add fallback defaults** — modules should work with sane defaults if global is missing

**Phase mapping:** Phase 4 (Fragile Areas) — address during frontend stabilization

---

### Pitfall 13: Path Traversal in Theme Router

**What goes wrong:** `theme_router.py` uses `os.path.join` for file operations without validating that the resulting path stays within the expected directory. The `filename` parameter from user input could contain `../` sequences.

**Why it happens:** `os.path.join` doesn't prevent traversal. `os.path.join("/uploads", "../../../etc/passwd")` resolves to `/etc/passwd`. While UUID filenames mitigate this for new uploads, serving existing files might be vulnerable.

**Consequences:**
- Arbitrary file read on server
- Configuration files exposed (`.env` with secrets)
- Source code disclosure

**Prevention:**
1. **Resolve and validate paths** — use `Path.resolve()` and check it starts with expected directory
2. **Use `werkzeug.utils.secure_filename`** — strips dangerous characters
3. **Never use user input directly in file paths** — use database IDs instead
4. **Configure web server** — serve uploads from a separate domain/vhost

**Detection:** Request `GET /uploads/fonts/../../../etc/passwd` → file content returned = vulnerability.

**Phase mapping:** Phase 1 (Security) — fix during file upload hardening

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Security Hardening | Breaking existing auth flow | Run full test suite after each security change; add integration tests first |
| SECRET_KEY Validation | App fails to start in dev with weak key | Provide dev-only key generation script; document in README |
| Rate Limiting | Legitimate users blocked | Use graduated limits (warn → slow → block); add rate limit headers |
| CORS Hardening | Frontend can't reach API | Test with actual frontend before deploying; use `allow_origin_regex` |
| File Upload Security | Existing uploads break | Validate existing files; add migration for any format changes |
| Migration Cleanup | Data loss during merge | Backup before migration changes; test `alembic downgrade` path |
| Test Coverage | Tests become slow | Use `pytest-xdist` for parallel execution; mock external services |
| Connection Pool | Pool exhaustion under load | Load test before and after changes; monitor pool metrics |
| Cache Layer | Stale data served | Implement cache invalidation on write; use short TTLs initially |
| JWT Invalidation | Users logged out unexpectedly | Roll out token_version change gradually; allow grace period |

## Sources

- **Context7**: FastAPI CORS middleware documentation, SQLAlchemy session/FAQ documentation, Alembic merge documentation
- **Official Docs**: FastAPI security tutorial, SQLAlchemy connection pool errors, Alembic branches/merge guide
- **Codebase**: `apps/api-postgres/app/middleware/rate_limit.py`, `apps/api-postgres/app/auth/service.py`, `apps/api-postgres/app/database.py`, `apps/api-postgres/app/core/config.py`, `apps/api-postgres/app/routers/theme_router.py`, `apps/api-postgres/tests/conftest.py`, `packages/shared/security/jwt.py`
- **Confidence**: HIGH — all pitfalls verified against actual codebase and official documentation

---

*Last updated: 2026-06-02*
