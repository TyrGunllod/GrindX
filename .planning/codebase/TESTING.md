# Testing

**Last updated:** 2026-06-02

## Test Framework

| Component | Framework | Version |
|-----------|----------|---------|
| Test runner | pytest | >=8.0.0 |
| Async support | pytest-asyncio | >=0.23.5 |
| HTTP client | httpx | >=0.27.0 |
| API testing | FastAPI TestClient | Built-in |

## Test Structure

```
tests/                              # Root-level integration tests
├── conftest.py                     # Global fixtures
├── unit/
└── integration/

apps/api-postgres/tests/
├── conftest.py                     # API-specific fixtures
├── unit/
│   ├── test_auth.py
│   ├── test_auth_service.py
│   ├── test_import_module.py
│   ├── test_import_router.py
│   ├── test_models_theme.py
│   ├── test_models_theme_history.py
│   ├── test_repository_usuario.py
│   ├── test_theme_repository.py
│   └── test_theme_service.py
└── integration/
    ├── test_autenticacao_integrada.py
    └── test_theme_router.py

apps/api-sqlserver/tests/
├── conftest.py
├── unit/
│   └── test_service_cliente.py
└── integration/
    ├── test_repository_cliente.py
    └── test_router_cliente.py

packages/shared/tests/
└── test_permissions.py
```

## pytest Configuration

From `pytest.ini`:
```ini
[pytest]
testpaths = apps packages tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Testes unitários
    integration: Testes de integração
    slow: Testes lentos
```

## Test Database Strategy

### SQLite In-Memory
- All tests use SQLite in-memory (no real PostgreSQL/SQL Server)
- **Critical**: `schema_translate_map` maps PostgreSQL schemas to None:
```python
_SCHEMA_TRANSLATE = {"iam": None, "portal": None, "catalogo": None, "org": None}
```

### Fixture Pattern
```python
@pytest.fixture(scope="function")
def db_session() -> Session:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create all tables
    with engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE).connect() as conn:
        _all_metadata.create_all(conn)
    
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables
```

### TestClient with DB Override
```python
@pytest.fixture
def client(db_session: Session) -> TestClient:
    def _override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

## Running Tests

### Via Makefile
```powershell
make test-postgres     # pytest apps/api-postgres/tests/ -v
make test-sqlserver    # pytest apps/api-sqlserver/tests/ -v
make test-shared       # pytest packages/shared/tests/ -v
make test-root         # pytest tests/ -v
make test-all          # All above
```

### Manual (requires PYTHONPATH)
```powershell
# api-postgres
cd apps/api-postgres
set PYTHONPATH=..\..\packages
.\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short

# Root tests
set PYTHONPATH=apps\\api-postgres;apps\\api-sqlserver;packages
.\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short
```

### CI (GitHub Actions)
- Uses `sqlite:///:memory:` for DATABASE_URL
- PYTHONPATH set to `${{ github.workspace }}/packages`
- Runs `pytest tests/ -v --tb=short --strict-markers`

## Mocking Strategy

### Auth Mocking
```python
@pytest.fixture
def auth_headers(client: TestClient, db_session: Session) -> dict[str, str]:
    # Create user in test DB
    usuario = Usuario(
        username="testuser",
        email="test@example.com",
        senha_hash=gerar_hash_senha("senha123"),
        role="admin",
    )
    db_session.add(usuario)
    db_session.commit()
    
    # Get real token via login endpoint
    response = client.post("/v1/auth/token", json={"username": "testuser", "password": "senha123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Service Mocking
- Services are injected via FastAPI dependencies
- Override `get_db` for database mocking
- Use `unittest.mock.patch` for external service mocking

## Test Patterns

### Unit Tests
- Test individual functions/methods in isolation
- Mock external dependencies
- Fast execution

### Integration Tests
- Test full API endpoints via TestClient
- Real database (SQLite in-memory)
- Real auth flow (create user → login → use token)

## Coverage

- **No formal coverage tool configured** (no pytest-cov in requirements)
- Coverage checked informally via CI test pass/fail
- All new features should include tests

## Test Naming Convention

```
test_{what_is_being_tested}
test_{action}_{scenario}_{expected_result}
```

Examples:
- `test_autenticar_credenciais_validas`
- `test_autenticar_credenciais_invalidas`
- `test_theme_service_create_theme`
