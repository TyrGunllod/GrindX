"""
Fixtures compartilhadas para testes da api-sqlserver.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

_packages_dir = str(Path(__file__).resolve().parent.parent.parent)
if _packages_dir not in sys.path:
    sys.path.insert(0, _packages_dir)

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="function")
def db_session() -> Session:
    """Banco SQLite em memória para cada teste."""
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
    """TestClient com banco de teste injetado."""

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Headers com JWT válido para testes (sem banco, token gerado direto).

    Usa settings.SECRET_KEY para garantir que o token seja aceito
    pelo get_current_user dependency.
    """
    from datetime import timedelta

    from app.core.config import settings
    from shared.security.jwt import criar_jwt

    token = criar_jwt(
        payload={"sub": "1", "role": "admin"},
        secret_key=settings.SECRET_KEY,
        expira_em=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}
