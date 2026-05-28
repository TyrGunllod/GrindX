"""
Configuração do banco de dados SQL Server com SQLAlchemy 2.x.

Conexão READ-ONLY configurada via settings (suporta pymssql e pyodbc).
Toda persistência está no PostgreSQL.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# Parâmetros de pool são incompatíveis com SQLite (usado em testes)
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

_engine_kwargs = {"echo": settings.DEBUG}
if not _is_sqlite:
    _engine_kwargs.update(
        pool_size=5,
        max_overflow=10,
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


class Base(DeclarativeBase):
    """Classe base para modelos SQLAlchemy do SQL Server (read-only)."""

    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency que fornece uma sessão do banco de dados SQL Server.

    Yields:
        Session do SQLAlchemy conectada ao SQL Server (read-only).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
