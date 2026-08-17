"""Geração de respostas com o DeepSeek (deepseek-chat)."""

import httpx

from app.core.config import settings
from app.core.exceptions import GenerationError
from app.rag.types import ChunkResult

SYSTEM_PROMPT = (
    "Você é o assistente de manual do ERP GrindX. "
    "Responda SOMENTE com base no contexto fornecido. "
    "Não use conhecimento externo. "
    "Cite a fonte (manual e seção) de cada informação no formato [manual — seção]. "
    "Se o contexto não cobrir a pergunta, responda exatamente: "
    '"Não encontrei essa informação nos manuais disponíveis."'
)

FALLBACK_ANSWER = "Não encontrei essa informação nos manuais disponíveis."


def build_context(chunks: list[ChunkResult]) -> str:
    """Monta o bloco de contexto a partir dos chunks recuperados."""
    return "\n\n".join(
        f"[{chunk.filename} — {chunk.title}]\n{chunk.content}" for chunk in chunks
    )


def generate(
    question: str,
    chunks: list[ChunkResult],
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    timeout: int | None = None,
) -> str:
    """Gera a resposta via DeepSeek com base no contexto recuperado."""
    if not chunks:
        return FALLBACK_ANSWER

    api_key = api_key or settings.DEEPSEEK_API_KEY
    base_url = base_url or settings.DEEPSEEK_BASE_URL
    model = model or settings.DEEPSEEK_MODEL
    timeout = timeout or settings.DEEPSEEK_TIMEOUT_SECONDS

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Contexto:\n{build_context(chunks)}\n\nPergunta: {question}",
            },
        ],
        "temperature": 0.2,
        "stream": False,
    }
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    try:
        response = httpx.post(
            f"{base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise GenerationError(str(exc)) from exc

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
