# Project Structure

**Last updated:** 2026-06-02

## Root Directory

```
GrindX/
├── apps/                          # Application code
│   ├── api-postgres/              # Primary API (FastAPI + PostgreSQL)
│   ├── api-sqlserver/             # Read-only API (FastAPI + SQL Server)
│   └── frontend-webapp/           # Vanilla JS portal
├── packages/                      # Shared Python packages
│   └── shared/                    # Common code (security, schemas, exceptions)
├── tests/                         # Root-level integration tests
├── scripts/                       # Utility scripts
├── infra/                         # Infrastructure config (nginx)
├── docs/                          # Documentation
├── import/                        # Module import directory
├── .github/workflows/             # CI/CD pipelines
├── .opencode/                     # OpenCode skills config
├── Makefile                       # Task automation
├── pyproject.toml                 # Semantic release config
├── pytest.ini                     # Pytest configuration
└── podman-compose.yml             # Container orchestration
```

## api-postgres Structure

```
apps/api-postgres/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── database.py                # SQLAlchemy engine/session
│   ├── auth/                      # Authentication module
│   │   ├── __init__.py
│   │   ├── dependencies.py        # FastAPI dependencies (get_current_user, require_role)
│   │   ├── router.py              # Auth endpoints (login, register, refresh)
│   │   └── service.py             # Auth business logic
│   ├── core/                      # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py              # Settings (pydantic-settings)
│   │   ├── exceptions.py          # Exception handlers
│   │   └── logging.py             # Structured logging setup
│   ├── middleware/                 # Request middleware
│   │   ├── __init__.py
│   │   ├── rate_limit.py          # IP-based rate limiting
│   │   ├── request_id.py          # Request ID injection
│   │   └── security_headers.py    # Security headers
│   ├── models/                    # SQLAlchemy models (re-exports from modules)
│   │   ├── __init__.py
│   │   ├── empresa.py
│   │   ├── portal.py
│   │   ├── theme.py
│   │   ├── theme_history.py
│   │   └── usuario.py             # Re-exports from iam module
│   ├── modules/                   # Domain modules
│   │   ├── __init__.py
│   │   ├── iam/                   # Identity & Access Management
│   │   │   ├── base.py            # IamBase (SQLAlchemy declarative base)
│   │   │   └── models/
│   │   │       └── usuario.py     # Usuario, UsuarioModulo models
│   │   ├── org/                   # Organization
│   │   │   ├── base.py            # OrgBase
│   │   │   └── models/
│   │   │       ├── empresa.py
│   │   │       ├── theme.py
│   │   │       └── theme_history.py
│   │   └── portal/                # Portal
│   │       ├── base.py            # PortalBase
│   │       └── models/
│   │           └── portal.py
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   ├── theme_repository.py
│   │   └── usuario_repository.py
│   ├── routers/                   # API endpoints
│   │   ├── __init__.py
│   │   ├── health_router.py       # GET /health
│   │   ├── import_router.py       # Module import endpoints
│   │   ├── portal_router.py       # Portal endpoints
│   │   ├── theme_router.py        # Theme CRUD endpoints
│   │   └── usuario_router.py      # User management endpoints
│   ├── schemas/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── theme.py
│   │   ├── theme_history.py
│   │   └── usuario.py
│   └── services/                  # Business logic
│       ├── __init__.py
│       ├── email_service.py
│       ├── theme_service.py
│       └── usuario_service.py
├── alembic/                       # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial_schema.py
│       ├── 002_add_usuario_modulos.py
│       ├── 003_add_empresa_and_theme.py
│       ├── 004_add_theme_history.py
│       └── 005_add_aba_parent_id.py
├── tests/
│   ├── conftest.py                # Fixtures (db_session, client, auth_headers)
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
├── scripts/                       # API-specific scripts
├── static/                        # Static assets
├── uploads/                       # User uploads (logos, fonts)
├── .env                           # Environment variables
├── .env.example                   # Env template
├── alembic.ini                    # Alembic config
├── Containerfile                  # Container build
├── manage_db.py                   # DB management CLI
├── requirements.txt               # Python dependencies
├── ruff.toml                      # Linter config
└── seed.py                        # Seed data script
```

## api-sqlserver Structure

```
apps/api-sqlserver/
├── app/
│   ├── main.py                    # FastAPI entry point (read-only)
│   ├── database.py                # SQLAlchemy engine
│   ├── auth/
│   │   └── dependencies.py        # JWT validation (no issuance)
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   ├── middleware/
│   │   ├── rate_limit.py
│   │   ├── request_id.py
│   │   └── security_headers.py
│   ├── models/
│   │   └── cliente.py
│   ├── repositories/
│   │   └── cliente_repository.py
│   ├── routers/
│   │   ├── cliente_router.py
│   │   └── health_router.py
│   ├── schemas/
│   │   └── cliente.py
│   └── services/
│       └── cliente_service.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── .env
├── Containerfile
└── requirements.txt
```

## Frontend Structure

```
apps/frontend-webapp/
├── index.html                     # Login page
├── dashboard.html                 # Main dashboard (loads modules via iframe)
├── dashboard.js                   # Dashboard logic
├── dashboard.css                  # Dashboard styles
├── script.js                      # Login logic
├── style.css                      # Login styles
├── version.json                   # Version info (synced from backend)
├── shared/                        # Shared frontend code
│   ├── app.js                     # Core framework (StorageManager, SessionManager, I18nManager, UIFactory, ThemeManager)
│   ├── apiService.js              # HTTP client wrapper
│   ├── baseController.js          # Base controller class
│   ├── config.js                  # API base URL config
│   ├── constants.js               # Constants
│   ├── core.css                   # Base CSS (glassmorphism, tokens)
│   ├── skinLoader.js              # Runtime theme loader
│   ├── validation.js              # Form validation
│   ├── components/                # Reusable UI components
│   └── fonts/                     # Local font files
├── modules/                       # Standalone modules
│   ├── admin-skins/               # Skin management module
│   │   ├── index.html
│   │   ├── script.js
│   │   └── style.css
│   ├── home/                      # Home module
│   │   └── index.html
│   ├── importer/                  # Data importer module
│   │   ├── index.html
│   │   ├── script.js
│   │   └── style.css
│   ├── structure/                 # Structure module
│   │   ├── index.html
│   │   ├── script.js
│   │   └── style.css
│   └── users/                     # User management module
│       ├── index.html
│       ├── script.js
│       ├── style.css
│       ├── preview.html
│       └── users-preview.css
├── skins/                         # Skin JSON files
│   ├── _template.json
│   ├── grindx-default.json
│   └── royal-purple.json
└── assets/                        # Static assets
```

## Shared Package Structure

```
packages/shared/
├── __init__.py
├── RBAC_GUIDE.py                  # RBAC documentation
├── exceptions/
│   ├── __init__.py
│   └── base.py                    # Domain exception hierarchy
├── schemas/
│   ├── __init__.py
│   ├── auth.py                    # Token schemas (TokenPayload, TokenRequest, etc.)
│   └── base.py                    # Common schemas
├── security/
│   ├── __init__.py
│   ├── jwt.py                     # JWT utilities (criar_jwt, verificar_jwt, etc.)
│   └── permissions.py             # RBAC (Role, require_role, require_role_or_higher)
└── tests/
    └── test_permissions.py
```

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Python files | snake_case | `usuario_repository.py` |
| Python classes | PascalCase | `UsuarioRepository` |
| Python functions | snake_case | `buscar_por_username()` |
| Router prefixes | `/v1/` | `/v1/auth/token` |
| CSS variables | `--skin-*` | `--skin-primary` |
| JS globals | `window.grindx` | `grindx.session` |
| Module dirs | kebab-case | `admin-skins/` |
| Test files | `test_*.py` | `test_auth_service.py` |
| Migration files | `NNN_description.py` | `001_initial_schema.py` |
