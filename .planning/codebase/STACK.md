# Technology Stack

**Last updated:** 2026-06-02

## Languages & Runtime

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend APIs | Python | 3.12+ |
| Frontend | Vanilla JS (ES6+) | Browser-native |
| Shell/Scripts | PowerShell | 7+ |
| Containerization | Podman (not Docker) | Latest |

## Backend Frameworks & Libraries

### api-postgres (Primary API - Port 8002)

| Dependency | Purpose | Version |
|-----------|---------|---------|
| FastAPI | Web framework | >=0.110.0 |
| uvicorn[standard] | ASGI server | >=0.27.0 |
| SQLAlchemy | ORM | >=2.0.27 |
| psycopg[binary] | PostgreSQL driver | >=3.1.18 |
| Alembic | Database migrations | >=1.13.1 |
| pydantic[email] | Data validation | >=2.6.1 |
| pydantic-settings | Config management | >=2.2.1 |
| python-dotenv | Env file loading | >=1.0.1 |
| python-jose[cryptography] | JWT handling | >=3.3.0 |
| bcrypt | Password hashing | >=4.1.2 |
| structlog | Structured logging | >=24.1.0 |
| python-multipart | File uploads | >=0.0.9 |
| ruff | Linting/formatting | >=0.3.0 |
| pytest | Testing | >=8.0.0 |
| pytest-asyncio | Async test support | >=0.23.5 |
| httpx | Test HTTP client | >=0.27.0 |

### api-sqlserver (Read-Only API - Port 8001)

| Dependency | Purpose | Version |
|-----------|---------|---------|
| FastAPI | Web framework | >=0.110.0 |
| uvicorn[standard] | ASGI server | >=0.27.0 |
| SQLAlchemy | ORM | >=2.0.27 |
| pymssql | SQL Server driver | >=2.2.11 |
| pyodbc | SQL Server driver (alt) | >=5.1.0 |
| pydantic-settings | Config management | >=2.2.1 |
| python-jose[cryptography] | JWT validation | >=3.3.0 |
| structlog | Structured logging | >=24.1.0 |
| ruff | Linting/formatting | >=0.3.0 |

## Frontend Stack

| Component | Technology |
|-----------|-----------|
| UI Framework | Vanilla JS (no React/Vue/Angular) |
| CSS Approach | CSS Custom Properties (`var(--skin-*)`) |
| Design System | Glassmorphism, CSS tokens |
| Module Loading | iframe-based isolation |
| Theming | Runtime skin loader with localStorage cache |
| i18n | Custom I18nManager (pt-BR, en-US, es-ES) |
| Icons | Font Awesome (via skin config) |
| Fonts | Google Fonts (configurable per skin) |

## Database

| Database | Usage | Access |
|----------|-------|--------|
| PostgreSQL | Primary data store (api-postgres) | Read/Write |
| SQL Server | External data queries (api-sqlserver) | Read-Only |
| SQLite | Testing (in-memory) | Test-only |

## Configuration

- **Config management**: pydantic-settings with `.env` files
- **Secret validation**: SECRET_KEY minimum 32 characters enforced
- **CORS**: Configurable via `CORS_ORIGINS` env var
- **Rate limiting**: Configurable requests/window per API
- **Semantic versioning**: `APP_VERSION` in `apps/api-postgres/app/core/config.py:14` and `apps/api-sqlserver/app/core/config.py`

## Build & CI

| Tool | Purpose |
|------|---------|
| Makefile | Task automation (Windows/PowerShell) |
| GitHub Actions | CI/CD (release.yml) |
| python-semantic-release | Automated versioning |
| Ruff | Lint + format |
| podman-compose | Container orchestration |
