"""
Configuração do banco de dados SQL Server com SQLAlchemy 2.x.

Conexão READ-ONLY configurada via settings (suporta pymssql e pyodbc).
Toda persistência está no PostgreSQL.

Engine é criado lazy (na primeira chamada) para evitar timeout na
importação dos módulos quando o SQL Server está indisponível.
"""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


@lru_cache
def _get_engine_kwargs() -> dict:
    """Retorna kwargs do engine, calculados uma vez."""
    is_sqlite = settings.DATABASE_URL.startswith("sqlite")
    kwargs = {"echo": settings.DEBUG}
    if not is_sqlite:
        kwargs.update(
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5},
        )
    else:
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


@lru_cache
def _get_engine():
    """Cria o engine sob demanda (lazy)."""
    return create_engine(settings.DATABASE_URL, **_get_engine_kwargs())


class Base(DeclarativeBase):
    """Classe base para modelos SQLAlchemy do SQL Server (read-only)."""
    pass


def get_engine():
    """Retorna o engine (lazy, criado na primeira chamada)."""
    return _get_engine()


def get_db() -> Generator[Session, None, None]:
    """Dependency que fornece uma sessão do banco de dados SQL Server.

    Yields:
        Session do SQLAlchemy conectada ao SQL Server (read-only).
    """
    engine = get_engine()
    db = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )()
    try:
        yield db
    finally:
        db.close()
