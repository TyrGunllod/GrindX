"""Tipos de dados compartilhados do pipeline RAG."""

from dataclasses import dataclass


@dataclass
class ChunkResult:
    """Trecho recuperado do banco vetorial com sua similaridade."""

    id: int
    module: str
    title: str
    content: str
    filename: str
    similarity: float
