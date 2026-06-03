# Project Research Summary

**Project:** GrindX ERP — Technical Concerns Remediation
**Domain:** FastAPI + PostgreSQL + SQLAlchemy Security & Quality Hardening
**Researched:** 2026-06-02
**Confidence:** HIGH

## Executive Summary

GrindX is a FastAPI-based ERP monorepo (api-postgres, api-sqlserver, frontend-webapp) requiring security hardening and quality improvements. Research unanimously identifies **security vulnerabilities as the highest priority** — particularly SECRET_KEY entropy validation, JWT token invalidation gaps, rate limiting bypasses, and file upload validation weaknesses. The codebase uses a layered architecture (Router → Service → Repository → Model) that enables isolated fixes without cascading changes.

The recommended approach is a **phased remediation strategy**: infrastructure foundation first (pytest-cov, migration cleanup), then parallel security hardening (config, migrations, security fixes), followed by a test safety net to lock in correct behavior, and finally performance/observability improvements. All four research streams converge on this ordering — security unblocks everything else, tests prevent regressions, and performance optimizations are safe only after coverage exists.

Key risks include: (1) JWT token invalidation impossibility after security changes — tokens remain valid until expiration with no revocation mechanism; (2) Schema translate map blindness — SQLite tests don't catch PostgreSQL schema-specific failures; (3) Rate limiting bypass via IP spoofing — current implementation trusts attacker-controlled headers. Mitigations are documented for each, but require careful implementation to avoid breaking existing auth flows.

## Key Findings

### Recommended Stack

New dependencies required for hardening (see `STACK.md` for full details):

**Core technologies to add:**
- **slowapi>=0.1.9**: Rate limiting with dual IP/user keys — battle-tested, supports Redis backend for scaling
- **filetype>=1.2.0**: Magic bytes file validation — pure Python, no system dependencies, works on Windows
- **pytest-cov>=5.0.0**: Coverage tracking with fail-under threshold — standard for CI quality gates
- **cachetools>=5.3.0**: In-memory cache for dev/small deployments — stdlib-compatible, TTL support
- **fastapi-cache2[redis]>=0.2.1**: Redis cache for production — built for FastAPI, async-first

**No changes needed:** bcrypt (good), python-jose (good), pydantic-settings (good), SQLAlchemy (good), Alembic (good)

### Expected Features

**Must have (table stakes — missing = system vulnerable):**
- SECRET_KEY entropy validation — prevents weak JWT tokens (currently length-only check)
- Temporary password expiry — prevents credential stuffing (currently no expiry)
- User-based rate limiting — prevents brute force per-account (currently IP-only)
- CORS production config — prevents unauthorized cross-origin requests (currently dev defaults)
- Path traversal protection — prevents directory traversal attacks (currently `os.path.join` without validation)
- File upload magic bytes validation — prevents malicious file uploads (currently extension/content-type only)
- pytest-cov with minimum threshold — prevents coverage regression (currently no coverage tracking)

**Should have (differentiators — adds value):**
- Security headers middleware — OWASP compliance (X-Content-Type-Options, X-Frame-Options, HSTS)
- Request ID tracking — distributed tracing support
- Audit logging — compliance & forensics capability
- Centralized error codes — consistent API responses via enum
- Health check depth — container orchestration readiness (liveness/readiness split)
- Redis caching layer — reduces database load for theme/config queries

**Defer (v2+ — not essential for remediation milestone):**
- Async SQLAlchemy migration — high risk, low current benefit
- Frontend framework migration — vanilla JS works, high effort
- WebSocket/real-time — out of scope for remediation
- Microservice decomposition — over-engineering for current scale
- Full OWASP ASVS compliance — massive scope creep

### Architecture Approach

Remediation follows a **layered fix strategy** where changes are scoped to minimize propagation. The key insight: security fixes unblock everything else because they establish trust boundaries, then tests establish safety nets before performance/code-quality changes touch shared code. GrindX's architecture (Router → Service → Repository → Model) makes this tractable — fixes can be isolated to layers without cascading.

**Major components requiring changes:**
1. **Configuration & Infrastructure** (`config.py`, `alembic/`, `requirements.txt`) — isolated changes, zero propagation
2. **Security Middleware** (`rate_limit.py`, CORS, file uploads) — touches request pipeline only
3. **Business Logic** (`auth/service.py`, error codes, health checks) — moderate propagation
4. **Data Access** (models, repositories, connection pools) — additive-only changes (indexes)

### Critical Pitfalls

1. **Schema Translate Map Blindness** — Tests pass with SQLite but production fails because PostgreSQL schemas (`iam`, `portal`, `catalogo`, `org`) behave differently. Mitigation: update `_SCHEMA_TRANSLATE` when adding schemas, add at least one integration test against real PostgreSQL.

2. **JWT Token Invalidation Impossibility** — After security hardening (password change, deactivation), existing tokens remain valid for 30min/7days. Mitigation: add `token_version` field to Usuario model, increment on sensitive operations, validate on each request.

3. **Rate Limiting Bypass via IP Spoofing** — Current rate limiter trusts `X-Forwarded-For` header (attacker-controlled). Mitigation: configure trusted proxies, use `request.client.host` as primary, add user-based rate limiting.

4. **File Upload Magic Byte Bypass** — Font/logo upload validation only checks extension/content-type, not actual file signatures. Mitigation: validate magic bytes (TTF starts with `\x00\x01\x00\x00`), use `filetype` library.

5. **Alembic Migration Ordering Chaos** — Multiple `001_*` prefixes cause unpredictable ordering or "multiple heads" errors. Mitigation: run `alembic heads` to detect, merge with `alembic merge`, use timestamp-based naming.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 0: Infrastructure Foundation
**Rationale:** Everything else depends on being able to measure test coverage and have clean migrations. This is the foundation that unblocks all subsequent phases.
**Delivers:** pytest-cov integration, shared package installability, clean migration chain
**Addresses:** pytest-cov with minimum threshold (table stakes)
**Avoids:** Alembic migration ordering chaos (Pitfall 5)
**Effort:** ~3.5 hours

### Phase 1A: Configuration Hardening (parallel)
**Rationale:** Config changes are isolated, zero propagation risk, can be done in parallel with other Phase 1 work.
**Delivers:** SECRET_KEY entropy validation, strict CORS parsing, environment-specific config
**Addresses:** SECRET_KEY entropy validation, CORS production config (table stakes)
**Avoids:** Secret key weak validation (Pitfall 9), CORS wildcard in production (Pitfall 6)
**Effort:** ~4 hours

### Phase 1B: Migration Cleanup (parallel)
**Rationale:** Migrations are isolated from code — fixing them has zero runtime impact but unblocks future schema changes.
**Delivers:** Consolidated migration chain, timestamp-based naming convention
**Avoids:** Alembic migration ordering chaos (Pitfall 5)
**Effort:** ~5 hours
**⚠️ Critical:** Must verify which migration is actually applied in production before deleting.

### Phase 1C: Security Fixes (parallel)
**Rationale:** Security vulnerabilities have immediate exploit potential. These fixes establish trust boundaries.
**Delivers:** Strong temp passwords with expiry, user-based rate limiting, path traversal protection, magic bytes validation
**Addresses:** Temporary password expiry, user-based rate limiting, path traversal protection, file upload magic bytes validation (all table stakes)
**Avoids:** JWT token invalidation impossibility (Pitfall 2), rate limiting bypass (Pitfall 3), file upload bypass (Pitfall 4)
**Effort:** ~9 hours

### Phase 2: Test Safety Net
**Rationale:** Security fixes change behavior — tests lock in the new correct behavior. Must come after security fixes to avoid testing old (vulnerable) behavior.
**Delivers:** Coverage baseline, security fix regression tests, critical path smoke tests, CI coverage gate
**Addresses:** Coverage reporting in CI (should-have)
**Avoids:** Test coverage false confidence (Pitfall 8)
**Effort:** ~9.5 hours

### Phase 3A: Error Registry (parallel)
**Rationale:** After tests exist, error code standardization can proceed safely with regression detection.
**Delivers:** Centralized error code enum, structured error responses, deprecation path for old codes
**Addresses:** Centralized error codes, structured error responses (table stakes)
**Effort:** ~8 hours

### Phase 3B: Health Checks (parallel)
**Rationale:** Health checks need test coverage to verify behavior. After Phase 2, this is safe.
**Delivers:** Deep DB connectivity check, liveness/readiness split, dependency health monitoring
**Addresses:** Health check depth (should-have)
**Effort:** ~5 hours

### Phase 3C: Caching Layer (parallel)
**Rationale:** Cache invalidation bugs are caught by regression tests. After Phase 2, this is safe.
**Delivers:** Cache interface abstraction, in-memory implementation, cache-aside in repositories, optional Redis adapter
**Addresses:** Redis caching layer (should-have)
**Effort:** ~11 hours

### Phase 4: Performance Indexes
**Rationale:** Indexes are pure optimization — zero risk, but need test coverage to verify query plans. Safest to do last.
**Delivers:** Strategic index definitions, Alembic migration for indexes, query plan verification
**Addresses:** Database indexing strategy (should-have)
**Effort:** ~6 hours

### Phase Ordering Rationale

- **Security first:** All 4 research streams agree — security fixes unblock everything else because they establish trust boundaries
- **Tests after security:** Tests lock in correct (secure) behavior, not old (vulnerable) behavior
- **Performance last:** Indexes and caching are safe optimizations, but need test coverage to catch regressions
- **Parallel phases:** Phases 1A/1B/1C and 3A/3B/3C can run in parallel — no dependencies between them
- **Isolation principle:** Each phase is independently deployable — one concern per PR

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1C:** JWT token invalidation mechanism (token_version vs Redis blacklist) needs design decision
- **Phase 3C:** Cache invalidation strategy for multi-tenant data needs careful design

Phases with standard patterns (skip research-phase):
- **Phase 0:** Well-documented pytest-cov and Alembic patterns
- **Phase 1A:** Standard Pydantic validators and CORS configuration
- **Phase 2:** Standard pytest fixtures and CI integration
- **Phase 4:** Standard SQLAlchemy index definitions

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All recommendations from official documentation, battle-tested libraries |
| Features | HIGH | Clear table stakes vs differentiators, aligned with OWASP top 10 |
| Architecture | HIGH | Layered fix strategy verified against codebase structure, minimal propagation risk |
| Pitfalls | HIGH | All pitfalls verified against actual codebase files with line numbers |

**Overall confidence:** HIGH

### Gaps to Address

- **JWT invalidation design:** Need to decide between token_version (simpler) vs Redis blacklist (immediate revocation) — recommend token_version for Phase 1C, Redis blacklist deferred
- **Production migration state:** Must verify which Alembic migration is actually applied in production before Phase 1B consolidation
- **Schema coverage:** Need to audit all schema names in `app/modules/*/base.py` against `_SCHEMA_TRANSLATE` in conftest.py
- **SQL Server connection pool:** `api-sqlserver/app/database.py` has no pool configuration — needs attention during Phase 3

## Sources

### Primary (HIGH confidence)
- FastAPI CORS docs — https://fastapi.tiangolo.com/tutorial/cors/
- SQLAlchemy Index docs — https://docs.sqlalchemy.org/en/20/core/constraints.html
- Alembic docs — https://alembic.sqlalchemy.org/en/latest/
- SlowAPI docs — https://slowapi.readthedocs.io/
- filetype docs — https://github.com/h2non/filetype.py
- fastapi-cache2 docs — https://github.com/long2ice/fastapi-cache
- pytest-cov docs — https://pytest-cov.readthedocs.io/
- Pydantic settings docs — https://docs.pydantic.dev/latest/concepts/pydantic_settings/

### Secondary (MEDIUM confidence)
- Codebase analysis — all pitfalls verified against actual source files
- OWASP guidelines — rate limiting, CSRF, path traversal prevention
- Twelve-Factor App — configuration, health checks

### Tertiary (LOW confidence)
- None — all findings verified with multiple sources

---
*Research completed: 2026-06-02*
*Ready for roadmap: yes*
