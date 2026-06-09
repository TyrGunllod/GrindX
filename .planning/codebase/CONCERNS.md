# Technical Concerns

**Last updated:** 2026-06-08

## Technical Debt

### High Priority

1. **No formal test coverage tracking**
   - ✓ RESOLVED: pytest-cov configured with 70% threshold in Phase 2
   - Location: `apps/api-postgres/requirements.txt`, `pytest.ini`, `.github/workflows/release.yml`

2. **Duplicate migration file names**
   - ✓ RESOLVED: Consolidated in Phase 2 (006_add_performance_indexes.py at head)
   - Location: `apps/api-postgres/alembic/versions/`

3. **SQLAlchemy model re-exports**
   - ✓ RESOLVED: Documented re-export pattern in Phase 4
   - Note: Re-exports kept for backward compatibility, new code should import from modules
   - Location: `apps/api-postgres/app/models/usuario.py`

### Medium Priority

4. **Hardcoded API URL in frontend**
   - ✓ RESOLVED: Centralized in config.js, fallbacks removed in Phase 4
   - Location: `apps/frontend-webapp/shared/config.js`

5. **No database connection pooling for SQL Server**
   - ✓ RESOLVED: connect_timeout added in Phase 3 fix
   - Note: Full pool config not implemented, but connection timeout prevents hangs
   - Location: `apps/api-sqlserver/app/database.py`

6. **Missing input sanitization in theme router**
   - ✓ RESOLVED: Path traversal protection added in Phase 4
   - Location: `apps/api-postgres/app/routers/theme_router.py`

7. **Frontend has no build/bundle step**
   - ✗ NOT RESOLVED: Out of scope (frontend architecture decision)
   - Location: `apps/frontend-webapp/`

## Security Concerns

### High Priority

1. **SECRET_KEY validation only checks length**
   - ✓ RESOLVED: Shannon entropy validation (3.5 bits/char threshold) in Phase 1
   - Location: `apps/api-postgres/app/core/config.py`

2. **Password recovery generates weak temporary passwords**
   - ✓ RESOLVED: 16 alphanumeric chars via `secrets` module, 15-min expiry in Phase 1
   - Location: `apps/api-postgres/app/auth/service.py`

3. **Rate limiting by IP only**
   - ✓ RESOLVED: SlowAPI with dual keys (IP + user_id) in Phase 1
   - Location: `apps/api-postgres/app/middleware/rate_limit.py`

### Medium Priority

4. **CORS allows all origins by default in dev**
   - ✓ RESOLVED: Strict production mode, never `*` in prod in Phase 1
   - Location: `apps/api-postgres/app/core/config.py`

5. **No CSRF protection**
   - ✗ DEFERRED TO V2: Not needed for JWT in Authorization header
   - Location: Frontend architecture

6. **File upload validation is incomplete**
   - ✓ RESOLVED: Magic bytes validation via `filetype` library in Phase 1
   - Location: `apps/api-postgres/app/routers/theme_router.py`

## Performance Concerns

1. **No caching layer**
   - ✓ RESOLVED: cachetools TTLCache (15min TTL) in Phase 3
   - Location: `apps/api-postgres/app/core/cache.py`

2. **Synchronous database operations**
   - ✗ DEFERRED TO V2: Async SQLAlchemy migration deferred
   - Location: All repository files

3. **No database indexing strategy**
   - ✓ RESOLVED: 5 B-tree indexes via Alembic migration in Phase 3
   - Location: `apps/api-postgres/alembic/versions/006_add_performance_indexes.py`

4. **Frontend loads all modules**
   - ✗ DEFERRED TO V2: Frontend lazy loading deferred
   - Location: `apps/frontend-webapp/dashboard.html`

## Fragile Areas

1. **Schema translate map for testing**
   - ✓ RESOLVED: Validation test confirms all 4 schemas mapped in Phase 2
   - Location: `apps/api-postgres/tests/unit/test_schema_validation.py`

2. **PYTHONPATH dependency**
   - ✓ RESOLVED: pyproject.toml created for shared package in Phase 4
   - Note: Can now install via `pip install -e packages/shared`
   - Location: `packages/shared/pyproject.toml`

3. **Alembic migration ordering**
   - ✓ RESOLVED: Consolidated in Phase 2, single head at 006
   - Location: `apps/api-postgres/alembic/versions/`

4. **Frontend `window.grindx` global**
   - ✓ RESOLVED: Documented in Phase 4 with clear API contract
   - Location: `apps/frontend-webapp/shared/app.js:228`

## Missing Features / Gaps

1. **No API versioning strategy**
   - ✓ RESOLVED: Versioning module created in Phase 4
   - Location: `apps/api-postgres/app/core/versioning.py`

2. **No health check depth**
   - ✓ RESOLVED: Deep health checks with schema validation in Phase 3
   - Location: `apps/api-postgres/app/routers/health_router.py`

3. **No structured error codes**
   - ✓ RESOLVED: ErrorCode registry created in Phase 4
   - Location: `packages/shared/exceptions/codes.py`

4. **No API documentation generation**
   - ✓ RESOLVED: OpenAPI export script created in Phase 4
   - Location: `scripts/export_openapi.py`

## Environment Dependencies

| Dependency | Required | Fallback |
|-----------|----------|----------|
| PostgreSQL | Production | SQLite (tests) |
| SQL Server | Production | None |
| SMTP Server | Email features | Silent failure |
| Podman | Containers | Manual setup |
| Python 3.12 | Runtime | None |
| PowerShell | Dev commands | None (Windows only) |

---

## Summary

| Category | Resolved | Not Resolved | Deferred to V2 |
|----------|----------|--------------|----------------|
| Technical Debt | 2 | 1 | 0 |
| Security | 5 | 0 | 1 |
| Performance | 2 | 0 | 2 |
| Fragile Areas | 4 | 0 | 0 |
| Missing Features | 4 | 0 | 0 |
| **Total** | **17** | **1** | **3** |

**Progress:** 17/21 items resolved (81%)
**Out of Scope:** 3 items deferred to v2
**Remaining:** 1 item not addressed (Frontend build/bundle step)
