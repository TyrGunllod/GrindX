"""Geração de embeddings com fastembed (ONNX Runtime — leve, sem torch).

Usa ONNX, reduzindo drasticamente o uso de memória (ideal para o plano
free do Render com 512MB).
"""

from functools import lru_cache

from fastembed import TextEmbedding

from app.core.config import settings


@lru_cache
def _get_model() -> TextEmbedding:
    return TextEmbedding(model_name=settings.EMBEDDING_MODEL)


def _encode(texts: list[str]) -> list[list[float]]:
    return [vector.tolist() for vector in _get_model().embed(texts)]


def embed(texts: list[str]) -> list[list[float]]:
    """Gera embeddings de documentos/passagens."""
    return _encode(texts)


def embed_query(texts: list[str]) -> list[list[float]]:
    """Gera embeddings de consultas (mesmo modelo; MiniLM não usa prefixo)."""
    return _encode(texts)
