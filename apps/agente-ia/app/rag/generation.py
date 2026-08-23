"""Geração de respostas com o LLM (via DeepSeek)."""

import time

import httpx

from app.core.config import settings
from app.core.exceptions import GenerationError
from app.rag.types import ChunkResult

_MAX_RETRIES = 3
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}

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


def _post_with_retry(url: str, payload: dict, headers: dict, timeout: int):
    """Faz a chamada HTTP com retentativas em erros transitórios (429/5xx)."""
    last_status = None
    last_error: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=timeout)
            last_status = response.status_code
            if response.status_code in _RETRYABLE_STATUS and attempt < _MAX_RETRIES - 1:
                time.sleep(2**attempt)
                continue
            response.raise_for_status()
            return response
        except httpx.HTTPError as exc:
            last_error = exc
            if attempt < _MAX_RETRIES - 1:
                time.sleep(2**attempt)
                continue
            break

    if last_status == 429:
        raise GenerationError(
            "Limite de requisições atingido (429). Aguarde alguns instantes e tente novamente."
        )
    raise GenerationError(str(last_error) if last_error else "Falha ao gerar resposta.")


def generate(
    question: str,
    chunks: list[ChunkResult],
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    timeout: int | None = None,
) -> str:
    """Gera a resposta via LLM com base no contexto recuperado."""
    if not chunks:
        return FALLBACK_ANSWER

    api_key = api_key or settings.LLM_API_KEY
    base_url = base_url or settings.LLM_BASE_URL
    model = model or settings.LLM_MODEL
    timeout = timeout or settings.LLM_TIMEOUT_SECONDS

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

    response = _post_with_retry(
        f"{base_url}/chat/completions",
        payload,
        headers,
        timeout,
    )
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
