"""Exceções customizadas da API do Agente de IA."""


class AgenteError(Exception):
    """Erro base do agente de IA."""


class EmbeddingError(AgenteError):
    """Falha ao gerar embeddings."""


class GenerationError(AgenteError):
    """Falha ao gerar resposta via DeepSeek."""


class VectorStoreError(AgenteError):
    """Falha no acesso ao banco vetorial."""
