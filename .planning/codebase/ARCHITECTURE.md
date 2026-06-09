# Architecture

**Last updated:** 2026-06-02

## System Pattern

**Monorepo with Dual-API Architecture:**

```
┌─────────────────┐     ┌─────────────────┐
│  Frontend (SPA) │────▶│   api-postgres  │ (port 8002)
│  port 5500      │     │   Read/Write    │
└─────────────────┘     └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │  api-sqlserver  │ (port 8001)
                        │   Read-Only     │
                        └─────────────────┘
```

- **api-postgres**: Primary API, handles auth, CRUD, JWT issuance
- **api-sqlserver**: Read-only queries to external SQL Server, validates JWTs from api-postgres
- **Frontend**: Vanilla JS portal, loads modules via iframes

## Layers (Per API)

```
Router → Service → Repository → Model → Database
  │         │          │          │
  └── Auth ─┘          └── Schema ┘
```

### api-postgres Layers

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Routers** | `app/routers/` | HTTP endpoints, request/response handling |
| **Auth** | `app/auth/` | JWT validation, dependency injection |
| **Services** | `app/services/` | Business logic, orchestration |
| **Repositories** | `app/repositories/` | Data access, query building |
| **Models** | `app/models/` | SQLAlchemy ORM models |
| **Schemas** | `app/schemas/` | Pydantic validation schemas |
| **Modules** | `app/modules/` | Domain modules (iam, org, portal) |
| **Middleware** | `app/middleware/` | Request processing pipeline |
| **Core** | `app/core/` | Config, exceptions, logging |

### api-sqlserver Layers

Same structure but **no auth service** - only validates tokens from api-postgres.

## Data Flow

### Authentication Flow
```
Client → POST /v1/auth/token → AuthService.autenticar()
  → UsuarioRepository.buscar_por_username()
  → verificar_senha() (bcrypt)
  → criar_jwt() (access + refresh tokens)
  → Return TokenResponse
```

### Authenticated Request Flow
```
Client → Router → get_current_user (dependency)
  → verificar_jwt() (shared package)
  → TokenPayload injected into route
  → Service → Repository → Database
```

### RBAC Flow
```
Router → require_role("admin") → get_current_user
  → verificar_jwt() → TokenPayload
  → Check role against allowed roles
  → Raise ForbiddenError if denied
```

## Module System (Frontend)

Each module is standalone with its own `index.html`, `script.js`, `style.css`:
- Loaded via iframe in the dashboard
- Communicates with parent via `window.grindx` global
- Shares `apiService.js`, `app.js`, `core.css` from `shared/`

## Skin/Theme System

```
SkinLoader → API /v1/themes/active → ThemeResponse
  → Apply CSS custom properties (--skin-*)
  → Apply fonts (Google Fonts CDN)
  → Update branding (company name, logos)
  → Cache in localStorage (5min TTL)
```

## Entry Points

| Component | Entry Point | Port |
|-----------|------------|------|
| api-postgres | `apps/api-postgres/app/main.py` | 8002 |
| api-sqlserver | `apps/api-sqlserver/app/main.py` | 8001 |
| Frontend | `apps/frontend-webapp/index.html` | 5500 |
| DB Migration | `apps/api-postgres/manage_db.py` | N/A |
| Seed Data | `apps/api-postgres/seed.py` | N/A |

## Key Abstractions

### Shared Package (`packages/shared/`)
- **security/jwt.py**: JWT creation, validation, password hashing
- **security/permissions.py**: RBAC system with role hierarchy
- **exceptions/base.py**: Domain exception hierarchy
- **schemas/auth.py**: Token payload, request/response schemas
- **schemas/base.py**: Common response schemas

### Database Session Pattern
```python
# Dependency injection via FastAPI
def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in routes
@router.get("/")
def get_items(db: Session = Depends(get_db)):
    ...
```

### Exception Handling
```
AppException (base)
├── NotFoundError (404)
├── ConflictError (409)
├── BusinessValidationError (422)
├── UnauthorizedError (401)
├── ForbiddenError (403)
└── DatabaseError (503)
```

All exceptions converted to JSON responses via `register_exception_handlers()`.
