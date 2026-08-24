"""Geração de embeddings com sentence-transformers (modelo local)."""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def _encode(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return [vector.tolist() for vector in vectors]


def embed(texts: list[str]) -> list[list[float]]:
    """Gera embeddings de documentos/passagens (prefixo 'passage:')."""
    return _encode([f"passage: {text}" for text in texts])


def embed_query(texts: list[str]) -> list[list[float]]:
    """Gera embeddings de consultas (prefixo 'query:')."""
    return _encode([f"query: {text}" for text in texts])
