# External Integrations

**Last updated:** 2026-06-02

## Databases

### PostgreSQL (Primary)
- **Connection**: `DATABASE_URL` env var (SQLAlchemy format)
- **Driver**: psycopg[binary]
- **Pool config**: pool_size=10, max_overflow=20, pool_recycle=1800
- **Schemas**: `iam`, `portal`, `catalogo`, `org`
- **Migrations**: Alembic in `apps/api-postgres/alembic/`
- **Schema translate**: Tests use `schema_translate_map` to map schemas to None for SQLite

### SQL Server (Read-Only)
- **Connection**: Via pymssql/pyodbc
- **Purpose**: External data queries (legacy ERP data)
- **Access**: Read-only, no write operations
- **Override**: `DB_URL_OVERRIDE` env var for testing

## Authentication & Authorization

### JWT System (Shared Package)
- **Token creation**: `packages/shared/security/jwt.py`
- **Token validation**: Shared between both APIs
- **Algorithm**: HS256
- **Token types**: access_token (30min default) + refresh_token (7 days default)
- **Payload**: `sub` (user_id), `role`, `company_id`, `exp`

### RBAC (Role-Based Access Control)
- **Roles**: `admin`, `operador`, `leitura` (defined in `packages/shared/security/permissions.py`)
- **Hierarchy**: admin >= operador >= leitura
- **Implementation**: FastAPI dependencies (`require_role`, `require_role_or_higher`)
- **Binding**: Each API binds its own `get_current_user` to the shared permission system

## Email Service

- **SMTP**: Configurable via env vars (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS)
- **TLS**: Optional SMTP_USE_TLS
- **Default**: localhost:2525 (development)
- **Usage**: Password recovery flow in `apps/api-postgres/app/services/email_service.py`

## File Storage

### Uploads
- **Directory**: `apps/api-postgres/uploads/`
- **Subdirs**: `logos/`, `fonts/`
- **Serving**: FastAPI StaticFiles mount at `/uploads`
- **Max size**: 5MB per file
- **Allowed images**: JPEG, PNG, SVG, GIF
- **Allowed fonts**: TTF, OTF, WOFF, WOFF2

## Frontend-Backend Communication

- **API Base URL**: Configurable via `shared/config.js` (`window.GRINDX_CONFIG.API_BASE_URL`)
- **Default**: `http://localhost:8002/v1`
- **Auth**: Bearer token in Authorization header
- **Auto-detection**: Falls back to `window.location.hostname:8002`

## Container Networking

- **Network**: `erp-net` (bridge driver)
- **Services**:
  - `api-postgres`: port 8002
  - `api-sqlserver`: port 8001
- **Health checks**: HTTP GET to `/health` endpoint
- **Shared volume**: `packages/shared` mounted at `/app/shared:z`

## CI/CD Pipeline

### GitHub Actions (release.yml)
- **Trigger**: Push to `main`
- **Jobs**:
  1. `test-api-postgres` - pytest with SQLite in-memory
  2. `test-api-sqlserver` - pytest with SQLite in-memory
  3. `test-root` - Integration tests (depends on 1 & 2)
  4. `lint` - ruff check + format
  5. `release` - semantic-release (depends on 3 & 4)
- **Python**: 3.12
- **Test DATABASE_URL**: `sqlite:///:memory:`

## Version Management

- **Version source**: `APP_VERSION` constant in config files
- **Sync**: `scripts/update_frontend_version.py` updates `apps/frontend-webapp/version.json`
- **Release**: python-semantic-release with angular commit parser
- **Changelog**: Auto-generated `CHANGELOG.md`
