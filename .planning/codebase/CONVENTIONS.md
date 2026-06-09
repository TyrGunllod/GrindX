# Code Conventions

**Last updated:** 2026-06-02

## Python Code Style

### Formatting & Linting
- **Tool**: Ruff (select E, F, I; ignore E501)
- **Config**: `apps/api-postgres/ruff.toml`
- **Line length**: No hard limit (E501 ignored)
- **Import sorting**: isort-compatible (I rules)
- **Run**: `ruff format . && ruff check --fix .`

### Docstrings
- **Language**: Portuguese (BR)
- **Format**: Google-style with Args/Returns/Raises sections
- **Example**:
```python
def autenticar(self, username: str, password: str) -> TokenResponse:
    """Autentica um usuário e retorna tokens JWT.

    Args:
        username: Nome de usuário.
        password: Senha em texto plano.

    Returns:
        TokenResponse com access_token e refresh_token.

    Raises:
        CredenciaisInvalidasError: Se username/senha estiverem incorretos.
    """
```

### Type Hints
- **Required**: All function signatures must have type hints
- **Return types**: Always annotated
- **Optional**: Use `X | None` syntax (Python 3.10+)
- **Collections**: Use `list[str]`, `dict[str, Any]` (not `List`, `Dict`)

### Error Handling
- **Custom exceptions**: Use hierarchy from `shared/exceptions/base.py`
- **Never**: Bare `except:` or `except Exception: pass`
- **Logging**: Always log before raising
- **HTTP mapping**: Exceptions auto-mapped to HTTP status codes

### Naming
| Type | Convention | Example |
|------|-----------|---------|
| Classes | PascalCase | `UsuarioRepository` |
| Functions/methods | snake_case | `buscar_por_username()` |
| Variables | snake_case | `usuario_id` |
| Constants | UPPER_SNAKE | `APP_VERSION` |
| Private | underscore prefix | `_bearer_scheme` |
| Boolean | prefix `is_`/`has_` | `is_active` |

## JavaScript Code Style

### General
- **No frameworks**: Vanilla JS only
- **Module pattern**: IIFE for encapsulation
- **Globals**: Single `window.grindx` namespace
- **Classes**: ES6 class syntax

### Naming
| Type | Convention | Example |
|------|-----------|---------|
| Classes | PascalCase | `StorageManager` |
| Methods | camelCase | `getToken()` |
| Variables | camelCase | `accessToken` |
| Constants | UPPER_SNAKE | `SKIN_DEFAULTS` |
| CSS classes | kebab-case | `btn-primary` |
| CSS vars | `--skin-*` | `--skin-primary` |

### DOM Patterns
- Use `document.createElement()` over innerHTML when possible
- Event delegation for dynamic content
- `data-*` attributes for JS hooks

## Architecture Patterns

### Backend: Repository Pattern
```
Router → Service → Repository → Model
```
- **Router**: HTTP handling only, delegates to service
- **Service**: Business logic, orchestration
- **Repository**: Data access abstraction
- **Model**: SQLAlchemy ORM definition

### Backend: Dependency Injection
```python
# FastAPI Depends for DI
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)
```

### Backend: Schema Validation
- Pydantic schemas for request/response validation
- Separate schemas per domain (usuario, theme, etc.)
- `model_dump()` for serialization

### Frontend: Module Isolation
- Each module is standalone (own HTML/CSS/JS)
- Loaded via iframe in dashboard
- Shares `window.grindx` API

### Frontend: Skin System
- CSS custom properties for all visual properties
- Runtime loading via `SkinLoader` class
- localStorage cache with 5min TTL
- Fallback chain: API → JSON file → defaults

## Database Conventions

### Migrations
- **Naming**: `NNN_description.py` (e.g., `001_initial_schema.py`)
- **Tool**: Alembic with `manage_db.py` CLI
- **Schemas**: `iam`, `portal`, `catalogo`, `org`
- **Testing**: SQLite in-memory with `schema_translate_map`

### Models
- **Base per schema**: `IamBase`, `OrgBase`, `PortalBase`
- **Re-exports**: `app/models/` re-exports from modules
- **Relationships**: Explicit `relationship()` definitions

## Testing Conventions

### Structure
```
tests/
├── conftest.py        # Shared fixtures
├── unit/              # Fast, isolated tests
└── integration/       # API-level tests with TestClient
```

### Fixtures
- `db_session`: SQLite in-memory, function-scoped
- `client`: FastAPI TestClient with DB override
- `auth_headers`: Pre-authenticated headers

### Markers
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow tests

## Commit Conventions

### Format
```
type(scope): description

Detailed description in Portuguese (BR).
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance
- `ci`: CI/CD changes
- `perf`: Performance

### Language
- **Title prefix**: English (`feat(auth):`)
- **Description**: Portuguese (BR)
