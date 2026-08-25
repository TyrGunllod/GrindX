from app.rag.retrieval import retrieve
from app.rag.types import ChunkResult
from app.rag.vectorstore import _keyword_score, _query_terms


def _chunk(similarity: float, module: str = "estoque") -> ChunkResult:
    return ChunkResult(
        id=1,
        module=module,
        title="Entrada de Produtos",
        content="como cadastrar um produto",
        filename="estoque.md",
        similarity=similarity,
    )


def test_retrieve_finds_in_module_without_fallback():
    def embed_fn(texts):
        return [[0.1, 0.2]]

    def search_fn(embedding, module, k, query=None):
        return [_chunk(0.8)]

    result = retrieve(
        question="como cadastrar produto?",
        module="estoque",
        embed_fn=embed_fn,
        search_fn=search_fn,
        threshold=0.35,
        top_k=3,
    )
    assert result.has_answer is True
    assert result.used_fallback is False


def test_retrieve_only_searches_current_module():
    calls = []

    def embed_fn(texts):
        return [[0.1, 0.2]]

    def search_fn(embedding, module, k, query=None):
        calls.append(module)
        return [] if module == "estoque" else [_chunk(0.7)]

    result = retrieve(
        question="onde vejo o balanço?",
        module="estoque",
        embed_fn=embed_fn,
        search_fn=search_fn,
        threshold=0.35,
        top_k=3,
    )
    assert result.has_answer is False
    assert calls == ["estoque"]


def test_retrieve_returns_no_answer_when_below_threshold():
    def embed_fn(texts):
        return [[0.1, 0.2]]

    def search_fn(embedding, module, k, query=None):
        return [_chunk(0.2)]

    result = retrieve(
        question="pergunta sem resposta",
        module="estoque",
        embed_fn=embed_fn,
        search_fn=search_fn,
        threshold=0.35,
        top_k=3,
    )
    assert result.has_answer is False


def test_query_terms_removes_stopwords():
    terms = _query_terms("o que faz o botão Salvar no cadastro de usuário?")
    assert "salvar" in terms
    assert "cadastro" in terms
    assert "usuário" in terms
    assert "botão" not in terms
    assert "que" not in terms


def test_keyword_score_ranks_title_match_higher():
    terms = {"salvar", "cadastro", "usuário"}
    score_salvar = _keyword_score(
        terms, "Botão Salvar", "grava o usuário e atualiza a tabela"
    )
    score_permissoes = _keyword_score(
        terms, "Botão Salvar Permissões", "grava as permissões"
    )
    assert score_salvar > score_permissoes
