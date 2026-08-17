"""
Configuração do banco de dados PostgreSQL com SQLAlchemy 2.x.

O Agente reusa o PostgreSQL do GrindX (pgvector). O engine é criado de
forma lazy para não falhar na importação quando o banco está indisponível.
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
    kwargs: dict = {"echo": settings.DEBUG}
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
def get_engine():
    """Cria o engine sob demanda (lazy)."""
    return create_engine(settings.DATABASE_URL, **_get_engine_kwargs())


class Base(DeclarativeBase):
    """Classe base para modelos SQLAlchemy do Agente de IA."""


def get_db() -> Generator[Session, None, None]:
    """Dependency que fornece uma sessão do banco de dados.

    Yields:
        Session do SQLAlchemy conectada ao PostgreSQL.
    """
    session = sessionmaker(
        bind=get_engine(),
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )()
    try:
        yield session
    finally:
        session.close()
