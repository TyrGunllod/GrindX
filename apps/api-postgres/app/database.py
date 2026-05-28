"""
Configuração do banco de dados PostgreSQL com SQLAlchemy 2.x.

Fornece engine, session factory e a dependency get_db para injeção
nas rotas do FastAPI.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Parâmetros de pool são incompatíveis com SQLite (usado em testes)
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

_engine_kwargs = {"echo": settings.DEBUG}
if not _is_sqlite:
    _engine_kwargs.update(
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
    )
else:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency que fornece uma sessão do banco de dados.

    Garante que a sessão é fechada ao final da requisição,
    mesmo em caso de exceção.

    Yields:
        Session do SQLAlchemy conectada ao PostgreSQL.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
