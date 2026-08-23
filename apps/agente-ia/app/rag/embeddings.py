"""Geração de embeddings com sentence-transformers (modelo local)."""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def embed(texts: list[str]) -> list[list[float]]:
    """Gera embeddings normalizados para uma lista de textos."""
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return [vector.tolist() for vector in vectors]
