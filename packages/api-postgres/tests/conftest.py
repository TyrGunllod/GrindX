"""
Fixtures compartilhadas para testes da api-postgres.

Fornece banco em memória (SQLite), sessão de teste, TestClient
e mocks de serviços para testes unitários e de integração.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Adiciona o diretório raiz dos packages ao sys.path para importar shared
_packages_dir = str(Path(__file__).resolve().parent.parent.parent)
if _packages_dir not in sys.path:
    sys.path.insert(0, _packages_dir)

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="function")
def db_session() -> Session:
    """Cria uma sessão com banco SQLite em memória para cada teste.

    Yields:
        Session do SQLAlchemy conectada ao SQLite in-memory.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session: Session) -> TestClient:
    """TestClient do FastAPI com banco de teste injetado.

    Substitui a dependency get_db para usar o banco em memória.

    Args:
        db_session: Sessão do banco de teste.

    Returns:
        TestClient configurado para testes.
    """

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient, db_session: Session) -> dict[str, str]:
    """Cria um usuário de teste e retorna headers com token JWT válido.

    Útil para testar rotas protegidas sem repetir o setup de auth.

    Returns:
        Dict com header Authorization: Bearer <token>.
    """
    from app.models.usuario import Usuario
    from shared.security.jwt import gerar_hash_senha

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
