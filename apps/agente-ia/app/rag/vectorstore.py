"""Persistência e busca vetorial com pgvector (PostgreSQL)."""

import re
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text, delete, func, select, text
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.config import settings
from app.database import Base, get_engine
from app.rag.types import ChunkResult

_STOPWORDS = {
    "a",
    "e",
    "i",
    "o",
    "u",
    "é",
    "os",
    "as",
    "um",
    "uma",
    "uns",
    "umas",
    "de",
    "do",
    "da",
    "dos",
    "das",
    "no",
    "na",
    "nos",
    "nas",
    "em",
    "ao",
    "aos",
    "que",
    "como",
    "para",
    "por",
    "com",
    "sem",
    "mas",
    "mais",
    "menos",
    "se",
    "me",
    "qual",
    "quais",
    "faz",
    "fazer",
    "fazem",
    "serve",
    "servir",
    "botão",
    "botao",
    "ícone",
    "icone",
    "ícones",
    "icones",
    "tela",
    "janela",
    "janelas",
    "telas",
    "sistema",
    "grindx",
    "posso",
    "quero",
    "saber",
    "preciso",
    "onde",
    "quando",
    "isto",
    "isso",
    "aquilo",
    "este",
    "esta",
    "estes",
    "estas",
    "esse",
    "essa",
    "esses",
    "essas",
    "vai",
    "pode",
    "poderia",
    "podem",
    "abrir",
    "fechar",
}


def _query_terms(query: str) -> set[str]:
    """Extrai termos significativos da consulta (sem stopwords)."""
    words = set(re.findall(r"[a-zà-ú]+", query.lower()))
    return words - _STOPWORDS


def _keyword_score(terms: set[str], title: str, content: str) -> float:
    """Fração de termos da consulta presentes no título/conteúdo do chunk."""
    if not terms:
        return 0.0
    haystack = f"{title} {content}".lower()
    matched = sum(1 for term in terms if term in haystack)
    return matched / len(terms)


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


def search(
    embedding: list[float],
    module: str | None,
    k: int,
    query: str | None = None,
    candidate_k: int = 20,
) -> list[ChunkResult]:
    """Busca os k chunks mais relevantes do módulo.

    Usa busca vetorial (cosseno) com reforço por palavras-chave quando `query`
    é informado, para que perguntas como "o que faz o botão X?" encontrem o
    chunk cujo título/conteúdo contém o termo.
    """
    stmt = select(
        Chunk,
        (1 - Chunk.embedding.cosine_distance(embedding)).label("similarity"),
    )
    if module:
        stmt = stmt.where(Chunk.module == module)
    stmt = stmt.order_by(Chunk.embedding.cosine_distance(embedding)).limit(candidate_k)

    with Session(get_engine()) as session:
        rows = session.execute(stmt).all()

    results = [
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

    if query and results:
        terms = _query_terms(query)
        if terms:
            results.sort(
                key=lambda r: (
                    r.similarity + 0.8 * _keyword_score(terms, r.title, r.content)
                ),
                reverse=True,
            )

    return results[:k]


def search_keyword(query: str, module: str | None, k: int) -> list[ChunkResult]:
    """Busca lexical por termos no título/conteúdo, sem carregar embeddings.

    Usado quando `EMBEDDINGS_ENABLED=false` (planos com pouca memória,
    ex.: Render free 512MB).
    """
    stmt = select(Chunk)
    if module:
        stmt = stmt.where(Chunk.module == module)
    with Session(get_engine()) as session:
        rows = session.scalars(stmt).all()

    terms = _query_terms(query)
    if not terms:
        return []

    scored = []
    for chunk in rows:
        score = _keyword_score(terms, chunk.title, chunk.content)
        if score > 0:
            scored.append(
                ChunkResult(
                    id=chunk.id,
                    module=chunk.module,
                    title=chunk.title,
                    content=chunk.content,
                    filename=chunk.filename,
                    similarity=score,
                )
            )
    scored.sort(key=lambda r: r.similarity, reverse=True)
    return scored[:k]


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


def delete_manual(module: str, filename: str) -> int:
    """Remove todos os chunks de um manual (módulo + arquivo)."""
    with Session(get_engine()) as session:
        result = session.execute(
            delete(Chunk).where(Chunk.module == module, Chunk.filename == filename)
        )
        session.commit()
    return result.rowcount or 0
