# Architecture Research: Technical Remediation Patterns

**Project:** GrindX ERP - Technical Concerns Remediation
**Researched:** 2026-06-02
**Confidence:** HIGH (based on codebase analysis + established remediation patterns)

## Executive Summary

Remediation projects require a specific ordering to avoid rework. The key insight: **security fixes unblock everything else** because they establish trust boundaries, then **tests establish safety nets** before performance/code-quality changes touch shared code. GrindX's layered architecture (Router → Service → Repository → Model) makes this tractable — fixes can be scoped to layers without cascading.

## Component Boundaries (What Needs to Change)

### Layer 1: Configuration & Infrastructure (No code changes to business logic)

| Component | Current State | Remediation Target | Boundary |
|-----------|---------------|-------------------|----------|
| `app/core/config.py` | SECRET_KEY length-only validation | Entropy validation + env guards | Isolated — changes don't propagate |
| `alembic/versions/` | Duplicate `001_*` prefixes | Clean sequential numbering | Isolated — migration-only |
| `requirements.txt` | No pytest-cov | Add coverage tooling | Isolated — dev dependency |
| `packages/shared/` | PYTHONPATH dependency | pip-installable package | Moderate — affects all imports |

### Layer 2: Security Middleware (Touches request pipeline)

| Component | Current State | Remediation Target | Boundary |
|-----------|---------------|-------------------|----------|
| `app/middleware/rate_limit.py` | IP-only limiting | User-based + IP hybrid | Moderate — auth dependency |
| `app/core/config.py` CORS | Permissive defaults | Strict origin validation | Isolated — config-only |
| `app/routers/theme_router.py` | No path traversal protection | Sanitized file access | Isolated — single router |
| Frontend `localStorage` | JWT storage (XSS risk) | HttpOnly cookie migration | HIGH — cross-cutting |

### Layer 3: Business Logic (Services + Repositories)

| Component | Current State | Remediation Target | Boundary |
|-----------|---------------|-------------------|----------|
| `app/auth/service.py` | Weak temp passwords | Strong generation + expiry | Isolated — auth service |
| Error codes | String-based, scattered | Centralized registry | Moderate — all exception sites |
| Health checks | Basic HTTP check | Deep dependency checks | Isolated — new endpoints |

### Layer 4: Data Access (Performance)

| Component | Current State | Remediation Target | Boundary |
|-----------|---------------|-------------------|----------|
| Models | No explicit indexes | Strategic index definitions | Low risk — additive only |
| Repositories | No caching | Cache-aside pattern | Moderate — repository layer |
| SQL Server connection | No pooling config | Connection pool tuning | Isolated — database.py |

## Data Flow: How Changes Propagate

```
┌─────────────────────────────────────────────────────────────┐
│                    CHANGE PROPAGATION MAP                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Config changes ──────► No downstream code changes          │
│  (config.py)            (just env vars)                     │
│                                                             │
│  Migration fixes ─────► No code changes                     │
│  (alembic/)             (just DB schema alignment)          │
│                                                             │
│  Security middleware ──► Request pipeline only               │
│  (rate_limit.py)        (routers unaffected)                │
│                                                             │
│  Error registry ───────► All exception raise sites           │
│  (new file)             (moderate refactor)                 │
│                                                             │
│  Index additions ──────► Zero code changes                  │
│  (models/)              (pure DB optimization)              │
│                                                             │
│  Cache layer ──────────► Repository interface unchanged     │
│  (new layer)            (implementation swap)               │
│                                                             │
│  Test infrastructure ──► All test files                     │
│  (conftest, fixtures)   (additive, non-breaking)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Fix Ordering: Dependency Graph

```
                    ┌──────────────────┐
                    │  Phase 0: Infra  │
                    │  (pytest-cov,    │
                    │   shared pkg)    │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  Phase 1A:  │  │  Phase 1B:  │  │  Phase 1C:  │
    │  Config     │  │  Migrations │  │  Security   │
    │  Hardening  │  │  Cleanup    │  │  Fixes      │
    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
           │                │                │
           └────────────────┼────────────────┘
                            ▼
                  ┌─────────────────┐
                  │    Phase 2:     │
                  │    Test Safety  │
                  │    Net          │
                  └────────┬────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Phase 3A:  │ │  Phase 3B:  │ │  Phase 3C:  │
    │  Error      │ │  Health     │ │  Caching    │
    │  Registry   │ │  Checks     │ │  Layer      │
    └─────────────┘ └─────────────┘ └─────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    Phase 4:     │
                  │    Indexes +    │
                  │    Performance  │
                  └─────────────────┘
```

## Recommended Fix Order (Detailed)

### Phase 0: Infrastructure Foundation
**Why first:** Everything else depends on being able to measure test coverage.

| Fix | Dependency | Risk | Effort |
|-----|------------|------|--------|
| Add pytest-cov to requirements | None | None | 30min |
| Fix shared package installability | None | Low | 2h |
| Fix duplicate migration prefixes | None | Low | 1h |

**Rationale:** You can't verify "each fix has tests" without coverage tracking. The shared package fix unblocks cleaner imports everywhere.

### Phase 1A: Configuration Hardening (Parallel)
**Why now:** Config changes are isolated, zero propagation risk.

| Fix | Dependency | Risk | Effort |
|-----|------------|------|--------|
| SECRET_KEY entropy validation | None | None | 1h |
| CORS strict origin parsing | None | None | 1h |
| Frontend API URL centralization | None | Low | 2h |

**Pattern:**
```python
# config.py — entropy-aware SECRET_KEY validation
import math
from collections import Counter

@field_validator("SECRET_KEY")
@classmethod
def validar_secret_key(cls, v: str) -> str:
    if len(v) < 32:
        raise ValueError("SECRET_KEY deve ter pelo menos 32 caracteres")

    # Shannon entropy check
    freq = Counter(v)
    length = len(v)
    entropy = -sum((count/length) * math.log2(count/length) for count in freq.values())

    if entropy < 3.5:  # Minimum bits per character
        raise ValueError(
            "SECRET_KEY tem entropia insuficiente. "
            "Use: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    return v
```

### Phase 1B: Migration Cleanup (Parallel)
**Why now:** Migrations are isolated from code — fixing them has zero runtime impact.

| Fix | Dependency | Risk | Effort |
|-----|------------|------|--------|
| Audit duplicate `001_*` files | None | Medium | 2h |
| Consolidate into single chain | Audit complete | Medium | 2h |
| Verify against production schema | Consolidation | Low | 1h |

**Critical:** Must verify which migration is actually applied in production before deleting.

### Phase 1C: Security Fixes (Parallel)
**Why now:** Security vulnerabilities have immediate exploit potential.

| Fix | Dependency | Risk | Effort |
|-----|------------|------|--------|
| Strong temp password generation | None | Low | 1h |
| Temp password expiry + forced change | Above | Low | 2h |
| User-based rate limiting | Auth dependency | Medium | 3h |
| Path traversal protection | None | Low | 1h |
| Upload validation (magic bytes) | None | Low | 2h |

**Pattern — User-based rate limiting:**
```python
# rate_limit.py — hybrid IP + user limiting
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Extract user from JWT if available (don't block unauthenticated)
        user_id = self._extract_user_id(request)
        client_ip = self._get_client_ip(request)

        # Dual key: IP for unauthenticated, user_id for authenticated
        limit_key = user_id or client_ip

        # ... existing sliding window logic with limit_key ...
```

### Phase 2: Test Safety Net
**Why after security:** Security fixes change behavior — tests lock in the new correct behavior.

| Fix | Dependency | Risk | Effort |
|-----|------------|------|--------|
| Coverage baseline measurement | Phase 0 | None | 30min |
| Security fix regression tests | Phase 1C | Low | 4h |
| Critical path smoke tests | Phase 0 | Low | 4h |
| Coverage ratchet (CI gate) | Baseline | Low | 1h |

**Pattern — Adding tests without breaking existing code:**
```python
# conftest.py — additive test infrastructure
# DON'T change existing fixtures
# ADD new fixtures alongside

@pytest.fixture
def authenticated_client(client, test_user):
    """New fixture — doesn't affect existing tests."""
    token = criar_jwt(test_user.id, test_user.perfil)
    client.headers["Authorization"] = f"Bearer {token}"
    return client

# Existing fixtures remain untouched
```

### Phase 3A: Error Registry (Parallel)
**Why after tests:** Tests catch regressions from error code changes.

| Fix | Dependency | Risk | Effort |
|-----|------------|------|--------|
| Define error code enum | Phase 2 | Low | 2h |
| Map existing string codes | Enum defined | Medium | 3h |
| Update exception hierarchy | Mapping complete | Medium | 2h |
| Deprecation warnings for old codes | All above | Low | 1h |

**Pattern:**
```python
# packages/shared/exceptions/codes.py
from enum import Enum

class ErrorCode(str, Enum):
    # Auth
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    # Business
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # System
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
```

### Phase 3B: Health Checks (Parallel)
**Why after tests:** Health check behavior needs test coverage.

| Fix | Dependency | Risk | Effort |
|-----|------------|------|--------|
| Deep DB connectivity check | Phase 2 | Low | 1h |
| Dependency health (SMTP, etc.) | DB check | Low | 2h |
| Readiness vs liveness split | Dependencies | Low | 2h |

**Pattern:**
```python
# health_router.py — deep health with dependency checks
@router.get("/health/live")
async def liveness():
    """Kubernetes liveness — is the process alive?"""
    return {"status": "alive"}

@router.get("/health/ready")
async def readiness(db: Session = Depends(get_db)):
    """Kubernetes readiness — can we serve traffic?"""
    checks = {}

    # Database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "failed"
        raise HTTPException(503, detail=checks)

    # Add SMTP, Redis, etc. checks here

    return {"status": "ready", "checks": checks}
```

### Phase 3C: Caching Layer (Parallel)
**Why after tests:** Cache invalidation bugs are caught by regression tests.

| Fix | Dependency | Risk | Effort |
|-----|------------|------|--------|
| Cache interface abstraction | Phase 2 | Low | 2h |
| In-memory implementation | Interface | Low | 2h |
| Cache-aside in repositories | Implementation | Medium | 4h |
| Redis adapter (optional) | Interface | Low | 3h |

**Pattern — Repository with cache-aside:**
```python
# repositories/base.py — cache-aside mixin
class CachedRepository:
    def __init__(self, db: Session, cache: CacheBackend):
        self.db = db
        self.cache = cache

    async def get_by_id(self, model, id: int):
        cache_key = f"{model.__tablename__}:{id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        result = self.db.query(model).filter(model.id == id).first()
        if result:
            await self.cache.set(cache_key, result, ttl=300)
        return result

    async def invalidate(self, model, id: int):
        cache_key = f"{model.__tablename__}:{id}"
        await self.cache.delete(cache_key)
```

### Phase 4: Performance Indexes
**Why last:** Indexes are pure optimization — zero risk, but need test coverage to verify query plans.

| Fix | Dependency | Risk | Effort |
|-----|------------|------|--------|
| Audit slow queries | Phase 3C | None | 2h |
| Define index strategy | Audit | None | 1h |
| Add Alembic migration for indexes | Strategy | Low | 2h |
| Verify with EXPLAIN ANALYZE | Migration | None | 1h |

**Pattern — Index definitions in models:**
```python
# models/usuario.py — explicit indexes
class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        Index("ix_usuarios_username", "username", unique=True),
        Index("ix_usuarios_email", "email"),
        Index("ix_usuarios_ativo_perfil", "ativo", "perfil"),  # Composite
    )
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Big Bang Remediation
**What:** Trying to fix everything at once in one massive PR
**Why bad:** Impossible to review, merge conflicts, can't isolate regressions
**Instead:** One concern per PR, each independently deployable

### Anti-Pattern 2: Test-After (Not Test-With)
**What:** Fixing code first, adding tests "later"
**Why bad:** "Later" never comes, regressions slip through
**Instead:** Write test that fails → fix code → test passes → commit both

### Anti-Pattern 3: Premature Optimization
**What:** Adding Redis/caching before measuring actual bottlenecks
**Why bad:** Adds complexity without evidence of benefit
**Instead:** Add indexes first (free), measure, then cache if needed

### Anti-Pattern 4: Security Through Obscurity
**What:** Relying on non-obvious URLs or hidden endpoints for security
**Why bad:** Attackers don't guess — they scan
**Instead:** Explicit auth on every endpoint, rate limiting, input validation

### Anti-Pattern 5: Migration Surgery
**What:** Deleting migration files without verifying production state
**Why bad:** Alembic loses track of what's applied
**Instead:** `alembic current` on production, then reconcile

## Scalability: Remediation vs New Development

| Concern | Remediation Approach | New Feature Approach |
|---------|---------------------|---------------------|
| Security | Fix existing code + add tests | Threat model first, then implement |
| Testing | Add coverage to existing paths | TDD from day one |
| Performance | Measure → optimize hot paths | Design for scale upfront |
| Error handling | Standardize existing codes | Use registry from start |

## Key Architectural Decisions for Remediation

1. **Keep sync SQLAlchemy** — Async migration is out of scope, sync is proven
2. **In-memory cache first, Redis later** — Avoids infrastructure dependency
3. **Error codes as enum** — Type safety + IDE support + deprecation path
4. **Health checks: liveness/readiness split** — Kubernetes-native pattern
5. **Rate limiting: hybrid IP+user** — Covers both authenticated and unauthenticated
6. **Migrations: consolidate, don't rewrite** — Preserve production compatibility

## Sources

- Codebase analysis: `.planning/codebase/CONCERNS.md`, `ARCHITECTURE.md`
- FastAPI documentation: Dependency injection patterns, middleware
- SQLAlchemy documentation: Index definitions, connection pooling
- OWASP: Rate limiting, CSRF, path traversal prevention
- Twelve-Factor App: Configuration, health checks
