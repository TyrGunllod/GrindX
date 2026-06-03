# Feature Landscape

**Domain:** FastAPI + PostgreSQL + SQLAlchemy Security & Quality Hardening
**Researched:** 2026-06-02
**Overall confidence:** HIGH

## Table Stakes

Features users expect. Missing = system is vulnerable or unreliable.

### Security (Critical)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| SECRET_KEY entropy validation | Prevents weak JWT tokens | Low | Current: length-only check. Add `secrets.compare_digest` + minimum entropy |
| Temporary password expiry | Prevents credential stuffing | Medium | Current: `token_hex(6)` no expiry. Add `datetime.utcnow() + timedelta(hours=24)` |
| User-based rate limiting | Prevents brute force per-account | Medium | Current: IP-only. Use `slowapi` with custom `key_func` extracting user from JWT |
| CORS production config | Prevents unauthorized cross-origin requests | Low | Current: dev defaults. Add explicit origin list from env vars |
| Path traversal protection | Prevents directory traversal attacks | Low | Current: `os.path.join` without validation. Use `pathlib.Path.resolve()` + whitelist |
| File upload magic bytes validation | Prevents malicious file uploads | Medium | Current: extension/content-type only. Use `python-magic` or manual byte checking |
| Pydantic input validation | Prevents malformed data injection | Low | Already using Pydantic; ensure all endpoints have explicit schemas |
| SQL injection prevention | Prevents database compromise | Low | SQLAlchemy ORM handles this; verify no raw SQL with string formatting |

### Testing (Critical)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| pytest-cov with minimum threshold | Prevents coverage regression | Low | Add `--cov-fail-under=70` to pytest.ini |
| Coverage reporting in CI | Visibility into test quality | Low | Add `pytest-cov` to requirements, configure in GitHub Actions |
| Test isolation verification | Prevents test pollution | Medium | Verify `db_session` fixture properly cleans up between tests |
| Auth flow test coverage | Critical path must be tested | Medium | Current: basic auth tests. Add edge cases (expired tokens, invalid roles) |

### Error Handling (Critical)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Centralized error codes | Consistent API responses | Low | Current: string-based codes. Create `ErrorCode` enum in `packages/shared` |
| Structured error responses | Client-side error handling | Low | FastAPI exception handlers return `{error_code, message, details}` |
| Input validation error messages | Developer experience | Low | Pydantic returns detailed errors; ensure they're not suppressed |

## Differentiators

Features that set product apart. Not expected, but valued.

### Security (Hardening)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| CSRF protection | Prevents cross-site request forgery | High | Add `starlette-csrf` middleware; requires frontend token storage changes |
| Security headers middleware | OWASP compliance | Medium | Add `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security` |
| Request ID tracking | Distributed tracing | Low | Add UUID middleware; log `request_id` in all entries |
| Audit logging | Compliance & forensics | Medium | Log all state-changing operations with user, timestamp, action |
| Penetration detection | Blocks automated attacks | Medium | Use `fastapi-guard` for SQL injection/XSS pattern detection |
| Secret rotation mechanism | Reduces breach impact | High | Add `SECRET_KEY_VERSION` + dual-key validation during rotation |

### Testing (Quality)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Integration test fixtures | Faster test development | Medium | Create reusable fixtures for common scenarios (authenticated user, admin, etc.) |
| Mutation testing | Validates test quality | High | Add `mutmut` to verify tests actually catch bugs |
| Contract testing | API compatibility | High | Add `schemathesis` for OpenAPI-based fuzz testing |
| Performance benchmarks | Prevents performance regression | Medium | Add `pytest-benchmark` for critical paths |
| Test data factories | Reduces test boilerplate | Low | Add `factory_boy` for model creation |

### Performance (Optimization)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Redis caching layer | Reduces database load | Medium | Add `fastapi-cache2` with Redis backend for theme/config queries |
| Database indexing strategy | Query performance | Low | Add `index=True` to frequently queried columns (username, email) |
| Connection pool tuning | Resource efficiency | Low | Configure `pool_size`, `max_overflow`, `pool_pre_ping` in SQLAlchemy |
| Query optimization logging | Identifies slow queries | Low | Enable SQLAlchemy `echo=True` in dev, add query timing middleware |
| Response compression | Bandwidth reduction | Low | Add `GZip` middleware for JSON responses |

### Observability (Visibility)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Structured logging (JSON) | Log aggregation & analysis | Medium | Add `structlog` with JSON renderer; replace print statements |
| Health check depth | Container orchestration | Low | Current: basic HTTP. Add DB connectivity, migration status checks |
| Request timing middleware | Performance monitoring | Low | Add `X-Response-Time` header; log slow requests |
| Error tracking integration | Production debugging | Medium | Add Sentry or similar for exception capture |
| Metrics endpoint | Operational visibility | Medium | Add `/metrics` endpoint with request counts, latencies, error rates |

### Code Quality (Maintainability)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Type checking (mypy) | Catches type errors early | Medium | Add `mypy` to pre-commit; configure strict mode for new code |
| Docstring enforcement | API documentation | Low | Add `pydocstyle` to linting; require docstrings on public functions |
| Import sorting (isort) | Consistent imports | Low | Already using Ruff with `I` rule; verify configuration |
| Dead code detection | Reduces technical debt | Low | Add `vulture` to find unused code |
| API versioning strategy | Backward compatibility | Medium | Add `/v2/` prefix with deprecation headers |

### DevOps (Operations)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Database migration CI check | Prevents migration conflicts | Low | Add `alembic upgrade --sql` check in CI |
| Container health checks | Kubernetes readiness | Low | Add `HEALTHCHECK` instruction to Containerfile |
| Environment validation | Prevents misconfigurations | Low | Validate required env vars at startup with clear error messages |
| Graceful shutdown | Zero-downtime deployments | Medium | Add signal handlers for connection draining |
| OpenAPI spec export | Client SDK generation | Low | Add `/openapi.json` endpoint; generate client with `openapi-python-client` |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Async SQLAlchemy migration | High risk, low current benefit | Keep sync mode; optimize with connection pooling |
| Frontend framework migration | Vanilla JS works; high effort | Keep iframe modules; add lazy loading if needed |
| WebSocket/real-time | Out of scope for remediation | Defer to future milestone |
| Custom auth framework | Reinventing the wheel | Keep existing JWT + RBAC; harden what exists |
| Microservice decomposition | Over-engineering for current scale | Keep monorepo; improve module boundaries |
| Redis dependency for rate limiting | Adds infrastructure complexity | Use in-memory rate limiting (slowapi default) unless scaling needs dictate otherwise |
| Full OWASP ASVS compliance | Massive scope creep | Focus on top 10 vulnerabilities relevant to FastAPI |
| Custom ORM abstractions | SQLAlchemy is sufficient | Use SQLAlchemy directly; avoid repository pattern over-engineering |
| API gateway (Kong, etc.) | Premature optimization | Use FastAPI middleware for security; add gateway when scaling requires |
| Distributed tracing (Jaeger, etc.) | Overkill for monolith | Use request ID + structured logging; add tracing when microservices exist |

## Feature Dependencies

```
pytest-cov → Coverage reporting in CI
Centralized error codes → Structured error responses
Structured logging → Request ID tracking
Connection pool tuning → Health check depth
Pydantic input validation → File upload magic bytes validation
CORS production config → Security headers middleware
```

## MVP Recommendation

Prioritize (Phase 1 - Security Critical):
1. SECRET_KEY entropy validation
2. Temporary password expiry
3. Path traversal protection
4. User-based rate limiting
5. pytest-cov with minimum threshold

Defer to Phase 2 (Testing & Quality):
- Coverage reporting in CI
- Integration test fixtures
- Type checking (mypy)

Defer to Phase 3 (Performance & Observability):
- Redis caching layer
- Structured logging
- Health check depth

Defer to Phase 4 (Hardening):
- CSRF protection
- Security headers middleware
- Audit logging

## Sources

### Security
- FastAPI CORS middleware: https://github.com/fastapi/fastapi/blob/master/docs/en/docs/tutorial/cors.md
- FastAPI CSRF protection: https://github.com/fastapi/fastapi/blob/master/docs/en/docs/advanced/strict-content-type.md
- FastAPI Guard security middleware: https://github.com/rennf93/fastapi-guard
- SlowAPI rate limiting: https://github.com/laurents/slowapi
- SQLAlchemy security: https://docs.sqlalchemy.org/en/20/core/pooling.html

### Testing
- pytest-cov configuration: https://github.com/pytest-dev/pytest-cov
- pytest fixtures: https://docs.pytest.org/en/stable/how-to/fixtures.html
- pytest monkeypatch: https://docs.pytest.org/en/stable/how-to/monkeypatch.html

### Observability
- Structlog configuration: https://www.structlog.org/en/stable/standard-library.html
- FastAPI middleware: https://github.com/fastapi/fastapi/blob/master/docs/en/docs/tutorial/middleware.md

### Database
- Alembic migrations: https://alembic.sqlalchemy.org/en/latest/
- SQLAlchemy connection pooling: https://docs.sqlalchemy.org/en/20/core/pooling.html

---
*Last updated: 2026-06-02*
