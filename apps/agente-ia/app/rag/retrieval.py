"""Camada de recuperação RAG: busca restrita ao módulo atual."""

from dataclasses import dataclass, field

from app.core.config import settings
from app.rag.types import ChunkResult


@dataclass
class RetrievalResult:
    """Resultado da recuperação."""

    chunks: list[ChunkResult] = field(default_factory=list)
    used_fallback: bool = False

    @property
    def has_answer(self) -> bool:
        return bool(self.chunks)


def retrieve(
    question: str,
    module: str,
    embed_fn,
    search_fn,
    threshold: float | None = None,
    top_k: int | None = None,
) -> RetrievalResult:
    """Recupera chunks apenas do módulo atual (sem busca global)."""
    threshold = threshold if threshold is not None else settings.SIMILARITY_THRESHOLD
    top_k = top_k if top_k is not None else settings.TOP_K

    embedding = embed_fn([question])[0]

    results = search_fn(embedding, module=module, k=top_k, query=question)
    if results and results[0].similarity >= threshold:
        return RetrievalResult(chunks=results, used_fallback=False)

    return RetrievalResult(chunks=[], used_fallback=False)
