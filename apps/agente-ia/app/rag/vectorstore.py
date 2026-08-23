"""Persistência e busca vetorial com pgvector (PostgreSQL)."""

from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text, delete, func, select, text
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.config import settings
from app.database import Base, get_engine
from app.rag.types import ChunkResult


class Chunk(Base):
    """Chunk de manual indexado com embedding."""

    __tablename__ = settings.AGENT_TABLE
    __table_args__ = {"schema": settings.AGENT_SCHEMA}

    id: Mapped[int] = mapped_column(primary_key=True)
    module: Mapped[str] = mapped_column(String(120), index=True)
    title: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    filename: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    embedding = mapped_column(Vector(settings.EMBEDDING_DIM))


def init_db() -> None:
    """Cria schema, extensão pgvector e tabela (idempotente)."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{settings.AGENT_SCHEMA}"'))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)


def add_chunks(records: list[dict]) -> int:
    """Insere chunks. Cada dict: module, title, content, filename, embedding."""
    with Session(get_engine()) as session:
        session.add_all([Chunk(**record) for record in records])
        session.commit()
    return len(records)


def search(embedding: list[float], module: str | None, k: int) -> list[ChunkResult]:
    """Busca os k chunks mais similares, filtrando por módulo quando informado."""
    stmt = select(
        Chunk,
        (1 - Chunk.embedding.cosine_distance(embedding)).label("similarity"),
    )
    if module:
        stmt = stmt.where(Chunk.module == module)
    stmt = stmt.order_by(Chunk.embedding.cosine_distance(embedding)).limit(k)

    with Session(get_engine()) as session:
        rows = session.execute(stmt).all()

    return [
        ChunkResult(
            id=chunk.id,
            module=chunk.module,
            title=chunk.title,
            content=chunk.content,
            filename=chunk.filename,
            similarity=float(similarity),
        )
        for chunk, similarity in rows
    ]


def list_modules() -> list[str]:
    """Lista os módulos que possuem manuais indexados."""
    stmt = select(Chunk.module).distinct().order_by(Chunk.module)
    with Session(get_engine()) as session:
        return list(session.scalars(stmt))


def list_manuals() -> list[dict]:
    """Agrupa os manuais indexados por módulo e arquivo, com contagem de chunks."""
    stmt = (
        select(Chunk.module, Chunk.filename, func.count())
        .group_by(Chunk.module, Chunk.filename)
        .order_by(Chunk.module, Chunk.filename)
    )
    with Session(get_engine()) as session:
        rows = session.execute(stmt).all()
    return [
        {"module": module, "filename": filename, "chunks": count}
        for module, filename, count in rows
    ]


def clear_module(module: str) -> int:
    """Remove todos os chunks de um módulo e retorna a quantidade removida."""
    with Session(get_engine()) as session:
        result = session.execute(delete(Chunk).where(Chunk.module == module))
        session.commit()
    return result.rowcount or 0
