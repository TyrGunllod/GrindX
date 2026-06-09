"""
Fixtures compartilhadas para testes da api-postgres.

Fornece banco em memória (SQLite), sessão de teste, TestClient
e mocks de serviços para testes unitários e de integração.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Adiciona o diretório raiz dos packages ao sys.path para importar shared
_packages_dir = str(Path(__file__).resolve().parent.parent.parent)
if _packages_dir not in sys.path:
    sys.path.insert(0, _packages_dir)

from app.database import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.modules.iam.base import IamBase  # noqa: E402


@pytest.fixture(autouse=True)
def _clear_cache():
    """Limpa caches entre testes para evitar vazamento de estado."""
    from app.core.cache import clear_all

    clear_all()
    yield
    clear_all()


_SCHEMA_TRANSLATE = {"iam": None, "portal": None, "catalogo": None, "org": None}

# All bases share the same MetaData object
_all_metadata = IamBase.metadata


@pytest.fixture(scope="function")
def db_session() -> Session:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    with engine.execution_options(
        schema_translate_map=_SCHEMA_TRANSLATE
    ).connect() as conn:
        _all_metadata.create_all(conn)

    TestingSession = sessionmaker(
        bind=engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE),
        autocommit=False,
        autoflush=False,
    )
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        with engine.execution_options(
            schema_translate_map=_SCHEMA_TRANSLATE
        ).connect() as conn:
            _all_metadata.drop_all(conn)


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_service(db_session: Session):
    from app.auth.service import AuthService

    return AuthService(db_session)


@pytest.fixture
def auth_headers(client: TestClient, db_session: Session) -> dict[str, str]:
    from shared.security.jwt import gerar_hash_senha

    from app.models.usuario import Usuario

    usuario = Usuario(
        username="testuser",
        email="test@example.com",
        nome_completo="Usuário de Teste",
        senha_hash=gerar_hash_senha("senha123"),
        role="admin",
    )
    db_session.add(usuario)
    db_session.commit()

    response = client.post(
        "/v1/auth/token",
        json={"username": "testuser", "password": "senha123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
