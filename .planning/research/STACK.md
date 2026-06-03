# Technology Stack: Hardening Recommendations

**Project:** GrindX ERP - Technical Concerns Remediation
**Researched:** 2026-06-02
**Domain:** FastAPI + PostgreSQL + SQLAlchemy + Python security best practices

---

## 1. SECRET_KEY Validation (Entropy, Not Just Length)

### Current State
- Location: `apps/api-postgres/app/core/config.py:28-35`
- Only checks `len(v) < 32` — no entropy validation

### Recommendation: Add Entropy Validation via Pydantic Custom Validator

**Library:** `pydantic` (already installed) + `math` (stdlib)

```python
import math
from collections import Counter
from pydantic import field_validator

@field_validator("SECRET_KEY")
@classmethod
def validar_secret_key(cls, v: str) -> str:
    if len(v) < 32:
        raise ValueError("SECRET_KEY deve ter pelo menos 32 caracteres.")
    
    # Calculate Shannon entropy
    freq = Counter(v)
    length = len(v)
    entropy = -sum((count/length) * math.log2(count/length) for count in freq.values())
    
    # Require minimum 3.5 bits of entropy per character
    # A 32-char key with 3.5 entropy = 112 bits total (strong)
    if entropy < 3.5:
        raise ValueError(
            f"SECRET_KEY tem entropia muito baixa ({entropy:.2f} bits/caractere). "
            "Use uma chave aleatória: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    return v
```

**Why Shannon entropy:** A key like `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` passes length check but has ~0 entropy. Real random keys from `secrets.token_hex(32)` have ~3.9 bits/char entropy.

**Confidence:** HIGH — Shannon entropy is a well-established metric for randomness quality.

---

## 2. Rate Limiting Strategies (User-Based vs IP-Based)

### Current State
- Location: `apps/api-postgres/app/middleware/rate_limit.py`
- IP-only rate limiting with in-memory sliding window
- No user-based limiting — easy to bypass with IP rotation

### Recommendation: SlowAPI with Dual Key Strategy

**Library:** `slowapi>=0.1.9` (wraps `limits` library, built for FastAPI)

```bash
pip install slowapi>=0.1.9
```

**Architecture:**
1. **IP-based** for unauthenticated endpoints (login, register, forgot-password)
2. **User-based** for authenticated endpoints (extract user_id from JWT)

```python
from slowapi import Limiter
from slowapi.util import get_ipaddr
from fastapi import Request

# Default: IP-based
limiter = Limiter(key_func=get_ipaddr)

# User-based for authenticated routes
def get_user_id(request: Request) -> str:
    user = getattr(request.state, "user", None)
    return str(user.id) if user else get_ipaddr(request)

# Usage
@app.post("/auth/login")
@limiter.limit("5/minute")  # Strict for login
async def login(request: Request, ...): ...

@app.get("/api/data")
@limiter.limit("100/minute", key_func=get_user_id)  # Per-user
async def data(request: Request, ...): ...
```

**Why SlowAPI over custom middleware:**
- Battle-tested (adapted from flask-limiter)
- Supports Redis backend for multi-worker deployments
- Dynamic rate limits per user tier
- Proper `Retry-After` headers

**Do NOT use:** `fastapi-limiter` (requires Redis always, less flexible key functions)

**Confidence:** HIGH — SlowAPI is the de facto standard for FastAPI rate limiting.

---

## 3. CSRF Protection in JWT-Based APIs

### Current State
- JWT stored in localStorage (XSS vulnerable)
- No CSRF tokens

### Recommendation: Defense-in-Depth Strategy

**For JWT APIs, CSRF protection works differently than cookie-based auth:**

| Attack Vector | Mitigation |
|---------------|------------|
| XSS → steal JWT from localStorage | CSP headers, input sanitization |
| CSRF → forge state-changing requests | JWT in `Authorization` header (not cookies) |
| Token theft | Short-lived access tokens + refresh rotation |

**Implementation:**

1. **Keep JWT in Authorization header** (current approach is correct for APIs)
2. **Add CSP headers** via middleware to prevent XSS
3. **Implement refresh token rotation** (invalidate old refresh token on use)
4. **Add `SameSite=Strict` cookies** for any cookie-based operations

```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
```

**Why NOT traditional CSRF tokens:** JWT in `Authorization` header cannot be triggered by CSRF (browsers don't attach `Authorization` headers to form submissions). CSRF tokens are for cookie-based auth.

**Confidence:** HIGH — This is the standard approach for JWT-based SPAs.

---

## 4. File Upload Validation (Magic Bytes, Content-Type Verification)

### Current State
- Location: `apps/api-postgres/app/routers/theme_router.py:344-390`
- Font upload checks extension only
- Logo upload checks content-type but not magic bytes

### Recommendation: filetype Library for Magic Bytes Validation

**Library:** `filetype>=1.2.0` (zero dependencies, fast magic bytes detection)

```bash
pip install filetype>=1.2.0
```

**Implementation:**

```python
import filetype
from fastapi import UploadFile, HTTPException

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_FONT_TYPES = {"font/woff", "font/woff2", "font/sfnt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def validate_upload(
    file: UploadFile,
    allowed_types: set[str],
    max_size: int = MAX_FILE_SIZE,
) -> bytes:
    """Validate file upload with magic bytes + size check."""
    content = await file.read()
    
    # Size check
    if len(content) > max_size:
        raise HTTPException(413, f"Arquivo excede {max_size // (1024*1024)}MB")
    
    # Magic bytes check (first 261 bytes sufficient for filetype detection)
    kind = filetype.guess(content[:261])
    if kind is None or kind.mime not in allowed_types:
        raise HTTPException(
            400,
            f"Tipo de arquivo inválido. Permitidos: {', '.join(allowed_types)}"
        )
    
    # Reset file position for downstream processing
    await file.seek(0)
    return content
```

**Why filetype over python-magic:**
- `filetype` is pure Python, no system-level `libmagic` dependency
- Works on Windows without extra installation
- Smaller dependency footprint
- Covers all common file types (images, fonts, documents)

**Confidence:** HIGH — filetype is the recommended library for Python magic bytes detection.

---

## 5. CORS Production Configuration

### Current State
- Location: `apps/api-postgres/app/core/config.py:39`
- Default: `"http://localhost:3000"`, CI uses `["*"]`

### Recommendation: Environment-Specific CORS with Strict Defaults

```python
from pydantic import field_validator

class Settings(BaseSettings):
    CORS_ORIGINS: str = ""  # Empty = no CORS in production
    ENVIRONMENT: str = "development"  # development|staging|production
    
    @property
    def allowed_origins_list(self) -> list[str]:
        """Returns strict CORS origins based on environment."""
        if self.ENVIRONMENT == "production":
            if not self.CORS_ORIGINS:
                raise ValueError(
                    "CORS_ORIGINS obrigatório em produção. "
                    "Defina origins explícitos (ex: https://app.grindx.com)"
                )
            # Never allow wildcards in production
            origins = self._parse_origins(self.CORS_ORIGINS)
            if "*" in origins:
                raise ValueError("CORS_ORIGINS não pode ser '*' em produção")
            return origins
        
        # Development/staging: allow localhost variants
        if not self.CORS_ORIGINS:
            return [
                "http://localhost:3000",
                "http://localhost:5500",
                "http://127.0.0.1:5500",
            ]
        return self._parse_origins(self.CORS_ORIGINS)
    
    def _parse_origins(self, value: str) -> list[str]:
        clean = value.replace("[", "").replace("]", "").replace('"', "").replace("'", "")
        return [o.strip() for o in clean.split(",") if o.strip()]
```

**CORS Middleware Configuration:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Not "*"
    allow_headers=["Authorization", "Content-Type"],  # Not "*"
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=600,  # Cache preflight for 10 minutes
)
```

**Key rules:**
- **NEVER** `allow_origins=["*"]` with `allow_credentials=True` (browsers reject this)
- **NEVER** wildcard origins in production
- **Explicit methods and headers** instead of wildcards

**Confidence:** HIGH — Direct from FastAPI official documentation.

---

## 6. Password Hashing and Temporary Password Security

### Current State
- Location: `packages/shared/security/jwt.py` and `apps/api-postgres/app/auth/service.py:157`
- bcrypt with default rounds (12) — good
- `token_hex(6)` = 12 hex chars for temp password — weak
- No expiry on temp passwords

### Recommendation: Strengthen bcrypt + Secure Temp Passwords

**bcrypt Configuration (explicit rounds):**

```python
import bcrypt

BCRYPT_ROUNDS = 12  # Default is good, ~250ms per hash on modern hardware

def gerar_hash_senha(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(senha_bytes, salt).decode("utf-8")
```

**Why 12 rounds:** Each round doubles the work factor. 12 rounds = ~250ms, which is the sweet spot between security and UX. 13 rounds = ~500ms (too slow for login). 11 rounds = ~125ms (faster but less secure).

**Temporary Password Generation:**

```python
import secrets
import string
from datetime import datetime, timedelta, timezone

def generate_temp_password(length: int = 16) -> str:
    """Generate a cryptographically secure temporary password.
    
    Format: XXXX-XXXX-XXXX-XXXX (human-readable, 16 chars)
    Entropy: ~77 bits (log2(36^16) where 36 = alphanumeric chars)
    """
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    # Format as groups of 4 for readability
    return '-'.join(password[i:i+4] for i in range(0, length, 4))

def get_temp_password_expiry() -> datetime:
    """Temp passwords expire in 15 minutes."""
    return datetime.now(timezone.utc) + timedelta(minutes=15)
```

**Database changes needed:**
- Add `temp_password_hash` column to `usuarios` table
- Add `temp_password_expires_at` column (nullable datetime)
- On `forgot_password`: store hash + expiry
- On `apply_temp_password`: check expiry before accepting

**Confidence:** HIGH — bcrypt is the standard, `secrets` module is cryptographically secure.

---

## 7. pytest-cov Configuration for FastAPI Projects

### Current State
- Location: `pytest.ini`, `requirements.txt`
- No pytest-cov installed, no coverage tracking

### Recommendation: pytest-cov with Fail-Under Threshold

**Add to requirements.txt:**

```
pytest-cov>=5.0.0
```

**Update pytest.ini:**

```ini
[pytest]
testpaths = apps packages tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers --cov=apps --cov=packages --cov-report=term-missing --cov-fail-under=70
markers =
    unit: Testes unitários
    integration: Testes de integração
    slow: Testes lentos
```

**Coverage configuration (.coveragerc or pyproject.toml):**

```toml
# pyproject.toml
[tool.coverage.run]
source = ["apps", "packages"]
omit = [
    "*/tests/*",
    "*/alembic/*",
    "*/__pycache__/*",
    "*/migrations/*",
]

[tool.coverage.report]
fail_under = 70
show_missing = true
skip_empty = true
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

**Why 70% initial threshold:** Start achievable, increase as coverage improves. Jumping to 90% immediately will fail CI and block progress.

**CI Integration (GitHub Actions):**

```yaml
- name: Run tests with coverage
  run: |
    set PYTHONPATH=${{ github.workspace }}/packages
    python -m pytest --cov --cov-report=xml --cov-fail-under=70

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
```

**Confidence:** HIGH — pytest-cov is the standard, well-documented.

---

## 8. Alembic Migration Best Practices (Avoiding Duplicates)

### Current State
- Location: `apps/api-postgres/alembic/versions/`
- Duplicate prefixes: `001_create_tables.py` and `001_initial_schema.py`
- `0001_criar_tabela_projetos.py` also has prefix conflict

### Recommendation: Consolidate + Use Timestamp-Based Naming

**Step 1: Consolidate existing migrations**

```bash
# Mark all current migrations as applied (if DB is already at head)
cd apps/api-postgres
alembic stamp heads

# Create a clean baseline migration
alembic revision --autogenerate -m "baseline_consolidated"
```

**Step 2: Configure Alembic for timestamp-based naming**

```python
# alembic/env.py
from datetime import datetime

def run_migrations_online():
    # ... existing config ...
    pass

# In alembic.ini or env.py, configure file template:
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
```

**alembic.ini configuration:**

```ini
[alembic]
# Use timestamp-based file naming to avoid conflicts
file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
# Truncate long revision IDs for readability
truncate_slug_length = 40
```

**Migration naming convention:**
```
2026_06_02_1430_abc123def456_add_user_indexes.py
│         │     │   │           │
│         │     │   │           └─ Descriptive slug
│         │     │   └─ Short revision ID
│         │     └─ Hour + minute (HHMM)
│         └─ Day
└─ Year_Month
```

**Best practices:**
1. **Always use `--autogenerate`** — let Alembic detect changes
2. **Review generated migrations** before committing
3. **One logical change per migration** — don't bundle unrelated changes
4. **Never edit applied migrations** — create a new migration to fix issues
5. **Use `alembic stamp heads`** when consolidating old migrations

**Confidence:** HIGH — Alembic official documentation recommends timestamp-based naming.

---

## 9. SQLAlchemy Indexing Strategies

### Current State
- Location: `apps/api-postgres/app/modules/` models
- No explicit index definitions
- Only primary keys and foreign keys auto-indexed

### Recommendation: Strategic Index Placement

**Index Types in SQLAlchemy:**

```python
from sqlalchemy import Column, Integer, String, Index, func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)  # Auto-indexed (unique)
    email = Column(String(100), unique=True)     # Auto-indexed (unique)
    role = Column(String(20))                    # Needs index (filtered often)
    empresa_id = Column(Integer)                 # Needs index (foreign key)
    ativo = Column(Boolean)                      # Needs index (filtered in queries)
    criado_em = Column(DateTime)                 # Needs index (sorted/filtered)
    
    # Composite index for common query patterns
    __table_args__ = (
        Index("idx_usuario_role_empresa", "role", "empresa_id"),
        Index("idx_usuario_ativo_criado", "ativo", "criado_em"),
    )
```

**When to Add Indexes:**

| Pattern | Example | Index Type |
|---------|---------|------------|
| `WHERE` clause columns | `WHERE ativo = true` | Single column |
| `JOIN` columns | `JOIN empresas ON ...` | Foreign key |
| `ORDER BY` columns | `ORDER BY criado_em DESC` | Single column |
| Composite filters | `WHERE role = 'admin' AND empresa_id = 1` | Composite |
| `LIKE 'prefix%'` | `WHERE username LIKE 'joao%'` | B-tree (default) |

**Functional Indexes (PostgreSQL):**

```python
# Case-insensitive search
Index("idx_usuario_email_lower", func.lower(Usuario.email))
```

**Index Naming Convention:**
```
idx_{table}_{column(s)}
idx_usuario_role_empresa
idx_pedido_status_criado_em
```

**PostgreSQL-Specific: Use `CONCURRENTLY` for large tables**

```python
# In migration
op.execute("CREATE INDEX CONCURRENTLY idx_usuario_email ON usuarios (email)")
# CONCURRENTLY avoids locking the table during index creation
```

**Confidence:** HIGH — Standard PostgreSQL indexing best practices.

---

## 10. Caching Patterns for FastAPI

### Current State
- No caching layer
- Theme API called on every page load
- Database queries repeated for same data

### Recommendation: Two-Tier Caching Strategy

**Tier 1: In-Memory Cache (for development/small deployments)**

**Library:** `cachetools>=5.3.0` (stdlib-compatible, TTL support)

```bash
pip install cachetools>=5.3.0
```

```python
from cachetools import TTLCache
from functools import wraps

# Global cache instance
_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutes TTL

def cached(ttl: int = 300, key_prefix: str = ""):
    """Simple in-memory cache decorator."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
            if cache_key in _cache:
                return _cache[cache_key]
            result = await func(*args, **kwargs)
            _cache[cache_key] = result
            return result
        return wrapper
    return decorator

# Usage
@cached(ttl=600, key_prefix="theme")
async def get_theme(theme_name: str):
    # Database query here
    pass
```

**Tier 2: Redis Cache (for production/multi-worker)**

**Library:** `fastapi-cache2[redis]>=0.2.1` (built for FastAPI, Redis backend)

```bash
pip install "fastapi-cache2[redis]>=0.2.1"
```

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis cache
    redis = aioredis.from_url(
        "redis://localhost:6379",
        encoding="utf8",
        decode_responses=False  # Required for fastapi-cache
    )
    FastAPICache.init(RedisBackend(redis), prefix="grindx-cache")
    yield
    await redis.close()

app = FastAPI(lifespan=lifespan)

# Usage
@app.get("/v1/themes/{theme_name}")
@cache(expire=600)  # Cache for 10 minutes
async def get_theme(theme_name: str):
    # Database query here
    pass
```

**Why fastapi-cache2:**
- Built specifically for FastAPI
- Supports Redis, Memcached, DynamoDB backends
- HTTP cache headers (`X-FastAPI-Cache: HIT/MISS`)
- Custom key builders for fine-grained control
- Async-first design

**What to Cache:**

| Data | TTL | Strategy |
|------|-----|----------|
| Theme configs | 10 min | Cache-aside |
| User permissions | 5 min | Cache-aside with invalidation |
| Static lookups | 1 hour | Write-through |
| API responses | Varies | HTTP cache headers |

**What NOT to Cache:**
- User-specific data (unless per-user key)
- Frequently changing data
- Large payloads (>1MB)

**Confidence:** HIGH — fastapi-cache2 is the standard for FastAPI caching.

---

## Summary: Required Dependencies

### New Dependencies to Add

```txt
# apps/api-postgres/requirements.txt

# === Security ===
slowapi>=0.1.9              # Rate limiting with user/IP keys
filetype>=1.2.0             # Magic bytes file validation

# === Testing ===
pytest-cov>=5.0.0           # Coverage tracking

# === Caching ===
cachetools>=5.3.0           # In-memory cache (dev/small)
fastapi-cache2[redis]>=0.2.1  # Redis cache (production)
```

### No Changes Needed

| Library | Current Version | Status |
|---------|-----------------|--------|
| bcrypt | >=4.1.2 | ✅ Good (default rounds=12) |
| python-jose[cryptography] | >=3.3.0 | ✅ Good (HS256 is fine for internal JWT) |
| pydantic-settings | >=2.2.1 | ✅ Good (supports custom validators) |
| SQLAlchemy | >=2.0.27 | ✅ Good (supports all index types) |
| Alembic | >=1.13.1 | ✅ Good (supports timestamp naming) |

---

## Alternatives Considered and Rejected

| Area | Rejected | Why |
|------|----------|-----|
| Rate limiting | `fastapi-limiter` | Requires Redis always, less flexible |
| File validation | `python-magic` | Requires system `libmagic`, Windows issues |
| Caching | `redis-py` directly | More boilerplate, no FastAPI integration |
| JWT | `PyJWT` | `python-jose` already installed, works fine |
| Password hashing | `argon2-cffi` | Overkill for this use case, bcrypt is sufficient |
| CSRF | Traditional CSRF tokens | Not needed for JWT in Authorization header |

---

## Sources

| Source | Confidence | URL |
|--------|------------|-----|
| FastAPI CORS docs | HIGH | https://fastapi.tiangolo.com/tutorial/cors/ |
| SQLAlchemy Index docs | HIGH | https://docs.sqlalchemy.org/en/20/core/constraints.html |
| Alembic docs | HIGH | https://alembic.sqlalchemy.org/en/latest/ |
| SlowAPI docs | HIGH | https://slowapi.readthedocs.io/ |
| filetype docs | HIGH | https://github.com/h2non/filetype.py |
| fastapi-cache2 docs | HIGH | https://github.com/long2ice/fastapi-cache |
| pytest-cov docs | HIGH | https://pytest-cov.readthedocs.io/ |
| passlib bcrypt docs | HIGH | https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html |
| Pydantic settings docs | HIGH | https://docs.pydantic.dev/latest/concepts/pydantic_settings/ |
