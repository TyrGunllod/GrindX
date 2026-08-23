import httpx

from app.rag import generation
from app.rag.types import ChunkResult


def _chunk() -> ChunkResult:
    return ChunkResult(
        id=1,
        module="estoque",
        title="Entrada de Produtos",
        content="Para cadastrar, vá em Produtos > Novo.",
        filename="estoque.md",
        similarity=0.8,
    )


def test_generate_returns_fallback_when_no_chunks():
    assert generation.generate("pergunta", []) == generation.FALLBACK_ANSWER


def test_build_context_formats_sources():
    context = generation.build_context([_chunk()])
    assert "[estoque.md — Entrada de Produtos]" in context
    assert "Produtos > Novo" in context


def test_generate_calls_llm_api(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "Resposta de teste"}}]}

    def fake_post(url, json=None, headers=None, timeout=None):
        return FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)

    answer = generation.generate(
        "como cadastrar?",
        [_chunk()],
        api_key="key",
        base_url="https://opencode.ai/zen/v1",
        model="big-pickle",
        timeout=10,
    )
    assert answer == "Resposta de teste"
