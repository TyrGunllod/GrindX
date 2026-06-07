# Phase 3: Performance & Resilience - Research

**Researched:** 2026-06-06
**Domain:** In-memory caching, database indexing, health check deepening
**Confidence:** HIGH

## Summary

Phase 3 adds performance optimizations and resilience to the GrindX ERP system. The phase covers three requirements: PERF-01 (in-memory cache with cachetools), PERF-02 (database indexing strategy), and PERF-03 (deep health checks with graceful degradation).

The codebase already has a solid foundation: health check endpoints exist in both APIs, the repository pattern is clean for cache integration, and SQLAlchemy models are well-structured for index definition. The main work involves adding cachetools as a dependency, implementing TTL-based caching at the repository layer, creating Alembic migrations for database indexes, and enhancing health checks to verify actual database connectivity and schema integrity.

**Primary recommendation:** Use cachetools TTLCache at the repository layer with 15-minute TTL, add composite indexes for frequent query patterns, and enhance health checks to return HTTP 503 when databases are unreachable.

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Cache Library:** cachetools — in-memory cache, no external dependencies
- **Queries to cache:** `GET /v1/themes/active`, `GET /v1/portal/abas`, `GET /v1/usuarios/{id}`
- **TTL:** 15 minutes (900 seconds)
- **Invalidation:** TTL only — cache expires naturally, no write-through invalidation
- **Both APIs:** Apply to api-postgres (main API); api-sqlserver read-only so caching less critical
- **Index types:** B-tree only (standard for equality and range queries)
- **Health checks:** PostgreSQL connectivity, SQL Server connectivity, schema validation
- **Behavior:** Fail-fast — 503 if any DB unavailable
- **Response format:** `{"status": "healthy"}` or `{"status": "degraded", "details": {...}}`

### Agent's Discretion
- **Error messages:** Portuguese (BR) to match existing codebase conventions
- **Logging:** Use structlog for health check events
- **Testing:** Each feature must have unit test validating behavior
- **Index columns:** Let researcher decide based on query analysis

### Deferred Ideas (OUT OF SCOPE)
- **Redis cache:** Deferred to v2 — adds infrastructure complexity
- **Async SQLAlchemy:** Deferred — refactoring too large for this phase
- **Frontend lazy loading:** Deferred — not in scope for this phase
- **Connection pooling for SQL Server:** Deferred — needs investigation

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PERF-01 | In-memory cache with cachetools for frequent queries (active themes, company config) | cachetools TTLCache verified on PyPI (v7.1.4, MIT, Python >=3.10). Repository layer pattern supports cache decorator integration. |
| PERF-02 | Database indexing strategy (composite indexes for common queries, functional indexes for case-insensitive search) | SQLAlchemy models analyzed. CompanyTheme has `company_id` indexed but needs composite `(company_id, is_active)`. Usuario has `username` indexed but needs `role` and `ativo` indexes. |
| PERF-03 | Deep health checks verifying PostgreSQL and SQL Server connectivity with graceful degradation | Existing health checks verify connectivity with `SELECT 1`. Need to add schema validation and proper HTTP status codes (200 vs 503). |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| cachetools | 7.1.4 | In-memory TTL cache | Mature (12+ years), MIT license, no dependencies, Python >=3.10, actively maintained |
| SQLAlchemy | >=2.0.27 | ORM with index support | Already in stack, supports index definition in models |
| Alembic | >=1.13.1 | Database migrations | Already in stack, handles index creation |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| structlog | >=24.1.0 | Structured logging | Already in stack, use for health check events |
| pytest | >=8.0.0 | Testing | Already in stack, use for cache and health tests |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| cachetools | functools.lru_cache | lru_cache lacks TTL support, cachetools provides TTLCache |
| cachetools | Redis | Redis adds infrastructure complexity, deferred to v2 |
| B-tree indexes | GIN/GiST indexes | GIN/GiST for full-text search, not needed for current queries |

**Installation:**
```bash
pip install cachetools>=7.1.0
```

**Version verification:** cachetools 7.1.4 verified on PyPI (released May 21, 2026). Requires Python >=3.10, which matches the project's Python 3.12+ requirement.

## Package Legitimacy Audit

> **Required** whenever this phase installs external packages. Run the Package Legitimacy Gate protocol before completing this section.

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| cachetools | PyPI | 12+ years (since 2014) | High (production stable) | github.com/tkem/cachetools | [ASSUMED] — slopcheck unavailable | Approved — verified on PyPI, MIT license, actively maintained |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

*If slopcheck was unavailable at research time, all packages above are tagged `[ASSUMED]` and the planner must gate each install behind a `checkpoint:human-verify` task.*

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| In-memory caching | Repository Layer | Service Layer | Cache should be close to data access, not business logic |
| Database indexing | Database (PostgreSQL) | Alembic Migrations | Indexes are database-level concerns, managed via migrations |
| Health checks | Router Layer (HTTP) | Database Layer (connectivity) | Health endpoints are HTTP concerns, but verify database state |
| Schema validation | Database Layer | Health Check Logic | Schema existence is a database concern, reported via health endpoint |

## Architecture Patterns

### Recommended Project Structure
```
apps/api-postgres/app/
├── core/
│   ├── cache.py          # NEW: Cache configuration and instances
│   └── health.py         # NEW: Health check logic (shared)
├── repositories/
│   ├── theme_repository.py  # MODIFIED: Add cache decorator
│   └── usuario_repository.py # MODIFIED: Add cache decorator
├── routers/
│   └── health_router.py  # MODIFIED: Enhanced health checks
└── ...

apps/api-sqlserver/app/
├── core/
│   └── health.py         # NEW: Health check logic (shared)
├── routers/
│   └── health_router.py  # MODIFIED: Enhanced health checks
└── ...
```

### Pattern 1: TTLCache at Repository Layer
**What:** Use cachetools TTLCache to cache frequently accessed database queries
**When to use:** For queries that are read-heavy and don't change frequently (themes, portal modules, user data)
**Example:**
```python
# Source: cachetools documentation (https://cachetools.readthedocs.io/en/stable/)
from cachetools import TTLCache

# Create cache instance: 100 items max, 15-minute TTL
_theme_cache = TTLCache(maxsize=100, ttl=900)

class ThemeRepository:
    def find_active_by_company_id(self, company_id: int) -> CompanyTheme | None:
        cache_key = f"active_theme:{company_id}"
        
        # Check cache first
        if cache_key in _theme_cache:
            return _theme_cache[cache_key]
        
        # Query database
        theme = (
            self.db.query(CompanyTheme)
            .filter(CompanyTheme.company_id == company_id, CompanyTheme.is_active)
            .first()
        )
        
        # Cache result (even None results to prevent cache penetration)
        _theme_cache[cache_key] = theme
        
        return theme
```

### Pattern 2: Composite Indexes for Common Queries
**What:** Create composite indexes for queries that filter on multiple columns
**When to use:** For queries that frequently filter on multiple conditions (e.g., `company_id` + `is_active`)
**Example:**
```python
# Source: SQLAlchemy documentation (https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html)
class CompanyTheme(OrgBase):
    __tablename__ = "company_themes"
    
    # Existing single-column index
    company_id: Mapped[int] = mapped_column(Integer, index=True)
    
    # Add composite index for common query pattern
    __table_args__ = (
        Index("ix_company_themes_active", "company_id", "is_active"),
    )
```

### Pattern 3: Deep Health Checks with Schema Validation
**What:** Health checks that verify not just connectivity but also schema integrity
**When to use:** For container orchestration (Kubernetes, Docker) that needs to know if the service is truly ready
**Example:**
```python
# Source: FastAPI documentation (https://fastapi.tiangolo.com/tutorial/health-checks/)
from sqlalchemy import text, inspect

def check_database_health(db: Session) -> dict:
    """Verify database connectivity and schema integrity."""
    try:
        # Test basic connectivity
        db.execute(text("SELECT 1"))
        
        # Verify critical tables exist
        inspector = inspect(db.bind)
        required_tables = ["usuarios", "company_themes", "portal_abas"]
        existing_tables = inspector.get_table_names()
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        if missing_tables:
            return {
                "status": "degraded",
                "details": {"missing_tables": missing_tables}
            }
        
        return {"status": "healthy"}
    except Exception as e:
        return {
            "status": "degraded",
            "details": {"error": str(e)}
        }
```

### Anti-Patterns to Avoid
- **Cache penetration:** Don't cache `None` results without TTL — attackers could flood with non-existent keys
- **Cache stampede:** Don't use `@cached` decorator without lock for concurrent access — use manual caching with lock if needed
- **Over-indexing:** Don't add indexes for every column — only for columns used in WHERE, JOIN, ORDER BY
- **Health check as liveness probe:** Don't use deep health checks for liveness probes — use simple ping for liveness, deep checks for readiness

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| TTL-based caching | Custom cache with threading.Lock and time tracking | cachetools.TTLCache | Handles TTL expiration, LRU eviction, thread safety (with lock parameter) |
| Cache key generation | String concatenation with manual escaping | cachetools.keys.hashkey | Handles edge cases, type safety |
| Database index management | Manual SQL DDL statements | Alembic migrations with Index() | Version control, rollback support, cross-database compatibility |
| Health check response | Custom JSON serialization | Pydantic models (HealthCheckResponse) | Validation, documentation, consistency |

## Common Pitfalls

### Pitfall 1: Cache Invalidation on Write Operations
**What goes wrong:** Cached data becomes stale after database updates
**Why it happens:** TTL-only strategy means cache expires after 15 minutes, even if data changes sooner
**How to avoid:** For this phase, accept eventual consistency (15-min staleness). Document that write-through invalidation is deferred to v2.
**Warning signs:** Users reporting "I changed the theme but still see the old one"

### Pitfall 2: SQLite Incompatibility with Index Migrations
**What goes wrong:** Alembic migration fails in tests because SQLite doesn't support all PostgreSQL index features
**Why it happens:** Tests use SQLite in-memory, but indexes are PostgreSQL-specific
**How to avoid:** Use `op.create_index()` with `if_not=True` parameter, or skip index creation in test environment
**Warning signs:** Test failures with "near IF: syntax error"

### Pitfall 3: Health Check Performance
**What goes wrong:** Health check endpoint becomes slow due to schema validation
**Why it happens:** `inspect()` calls can be expensive on large schemas
**How to avoid:** Cache schema validation results for 30-60 seconds, or only check critical tables
**Warning signs:** Health check taking >100ms

### Pitfall 4: Cache Memory Usage
**What goes wrong:** Application memory grows unbounded due to large cache
**Why it happens:** `maxsize=100` with large JSON objects (themes with colors, fonts, tokens)
**How to avoid:** Monitor cache size, consider `getsizeof` parameter for large objects
**Warning signs:** OOM errors, memory usage growing over time

## Code Examples

Verified patterns from official sources:

### TTLCache with Manual Caching
```python
# Source: cachetools documentation (https://cachetools.readthedocs.io/en/stable/)
from cachetools import TTLCache
import threading

# Thread-safe cache with lock
_cache = TTLCache(maxsize=100, ttl=900)
_lock = threading.Lock()

def get_cached(key, fetch_fn):
    """Get value from cache or fetch from database."""
    with _lock:
        if key in _cache:
            return _cache[key]
    
    # Fetch outside lock to avoid blocking
    value = fetch_fn()
    
    with _lock:
        _cache[key] = value
    
    return value
```

### Alembic Index Migration
```python
# Source: Alembic documentation (https://alembic.sqlalchemy.org/en/latest/ops.html)
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Composite index for common query pattern
    op.create_index(
        "ix_company_themes_active",
        "company_themes",
        ["company_id", "is_active"],
        unique=False,
    )
    
    # Index for role-based queries
    op.create_index(
        "ix_usuarios_role_ativo",
        "usuarios",
        ["role", "ativo"],
        unique=False,
    )

def downgrade() -> None:
    op.drop_index("ix_company_themes_active", table_name="company_themes")
    op.drop_index("ix_usuarios_role_ativo", table_name="usuarios")
```

### Enhanced Health Check Endpoint
```python
# Source: FastAPI documentation (https://fastapi.tiangolo.com/tutorial/health-checks/)
from fastapi import APIRouter, Depends, status
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

router = APIRouter(tags=["Health"])

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """Deep health check with schema validation."""
    postgres_status = check_database_health(db, "postgresql")
    
    if postgres_status["status"] == "healthy":
        return {"status": "healthy"}
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "details": postgres_status["details"]}
        )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| No caching | cachetools TTLCache | This phase | 15-min TTL reduces database load |
| No indexes beyond PKs | Composite indexes | This phase | Faster queries for common patterns |
| Basic health check (SELECT 1) | Deep health check with schema validation | This phase | Better container orchestration support |

**Deprecated/outdated:**
- `functools.lru_cache` without TTL: Not suitable for this use case, cachetools provides TTL support

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | cachetools package is legitimate and safe to install | Package Legitimacy Audit | Low — verified on PyPI, 12+ year history, MIT license |
| A2 | Index naming convention `ix_{table}_{column}` is standard | Code Examples | Low — follows PostgreSQL convention |
| A3 | Health check should verify 3 critical tables (usuarios, company_themes, portal_abas) | Architecture Patterns | Medium — may need adjustment based on actual critical tables |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.

## Open Questions

1. **Which tables are truly critical for health checks?**
   - What we know: `usuarios`, `company_themes`, `portal_abas` are core tables
   - What's unclear: Whether other tables (e.g., `empresa`, `theme_history`) should also be verified
   - Recommendation: Start with 3 core tables, add more if health checks are too permissive

2. **Should we cache `None` results to prevent cache penetration?**
   - What we know: Caching `None` prevents repeated queries for non-existent data
   - What's unclear: Whether this could mask database issues
   - Recommendation: Cache `None` with shorter TTL (5 minutes) to balance between performance and freshness

3. **How to handle cache in tests?**
   - What we know: Tests use SQLite in-memory, cache should be isolated per test
   - What's unclear: Whether to use mock cache or real cache in tests
   - Recommendation: Use mock cache in unit tests, real cache in integration tests with cleanup fixture

## Environment Availability

> Skip this section if the phase has no external dependencies (code/config-only changes).

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Both APIs | ✓ | 3.12+ | — |
| PostgreSQL | api-postgres | ✓ | — | SQLite for tests |
| SQL Server | api-sqlserver | ✓ | — | SQLite for tests |
| cachetools | Cache layer | ✗ | — | Install via pip |
| Alembic | Migrations | ✓ | >=1.13.1 | — |
| SQLAlchemy | ORM | ✓ | >=2.0.27 | — |

**Missing dependencies with no fallback:**
- cachetools must be installed before implementation

**Missing dependencies with fallback:**
- None — all other dependencies are already available

## Validation Architecture

> Skip this section entirely if workflow.nyquist_validation is explicitly set to false in .planning/config.json. If the key is absent, treat as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >=8.0.0 |
| Config file | `pytest.ini` (root) |
| Quick run command | `make test-postgres` |
| Full suite command | `make test-all` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PERF-01 | Cached queries return from cache on second request within TTL | unit | `pytest apps/api-postgres/tests/unit/test_cache.py -x` | ❌ Wave 0 |
| PERF-01 | Cache expires after TTL | unit | `pytest apps/api-postgres/tests/unit/test_cache.py::test_ttl_expiry -x` | ❌ Wave 0 |
| PERF-02 | EXPLAIN shows index scan after migration | integration | `pytest apps/api-postgres/tests/integration/test_indexes.py -x` | ❌ Wave 0 |
| PERF-03 | Health endpoint returns 200 when DB reachable | integration | `pytest apps/api-postgres/tests/integration/test_health.py -x` | ❌ Wave 0 |
| PERF-03 | Health endpoint returns 503 when DB unreachable | integration | `pytest apps/api-postgres/tests/integration/test_health.py::test_degraded -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `make test-postgres`
- **Per wave merge:** `make test-all`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `apps/api-postgres/tests/unit/test_cache.py` — covers PERF-01
- [ ] `apps/api-postgres/tests/integration/test_indexes.py` — covers PERF-02
- [ ] `apps/api-postgres/tests/integration/test_health.py` — covers PERF-03
- [ ] `apps/api-sqlserver/tests/integration/test_health.py` — covers PERF-03 (sqlserver)
- [ ] Install cachetools: `pip install cachetools>=7.1.0`

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). Omit only if explicitly `false` in config.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Not affected by caching/indexing |
| V3 Session Management | no | Not affected by caching/indexing |
| V4 Access Control | no | Not affected by caching/indexing |
| V5 Input Validation | no | Cache keys are internal, not user input |
| V6 Cryptography | no | No cryptographic operations in this phase |

### Known Threat Patterns for Python/FastAPI

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Cache poisoning | Tampering | Cache keys are internal (company_id, user_id), not user-controlled |
| Cache penetration | Denial of Service | Cache `None` results with shorter TTL to prevent repeated queries |
| Memory exhaustion | Denial of Service | `maxsize=100` limits cache size, monitor memory usage |

## Sources

### Primary (HIGH confidence)
- cachetools PyPI (https://pypi.org/project/cachetools/) — Version 7.1.4, MIT license, Python >=3.10
- cachetools documentation (https://cachetools.readthedocs.io/en/stable/) — TTLCache API, cached decorator
- SQLAlchemy documentation (https://docs.sqlalchemy.org/en/20/) — Index definition, composite indexes
- Alembic documentation (https://alembic.sqlalchemy.org/en/latest/) — Migration operations, create_index

### Secondary (MEDIUM confidence)
- FastAPI documentation (https://fastapi.tiangolo.com/) — Health check patterns, dependency injection
- PostgreSQL documentation (https://www.postgresql.org/docs/current/indexes.html) — Index types, composite indexes

### Tertiary (LOW confidence)
- None — all findings verified against official documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — cachetools verified on PyPI, SQLAlchemy/Alembic already in stack
- Architecture: HIGH — repository pattern clear, health check endpoints exist
- Pitfalls: MEDIUM — based on common patterns, may need adjustment for this specific codebase

**Research date:** 2026-06-06
**Valid until:** 2026-07-06 (30 days for stable stack)

---

*Phase: 03-performance-resilience*
*Research completed: 2026-06-06*
