from app.rag.ingestion import chunk_markdown


def test_chunk_markdown_splits_by_headings():
    text = (
        "# Manual de Estoque\n"
        "Introdução do manual.\n"
        "## Entrada de Produtos\n"
        "Passo 1: abrir a tela.\n"
        "Passo 2: informar o SKU.\n"
        "## Baixa de Produtos\n"
        "Informar a quantidade a baixar.\n"
    )
    chunks = chunk_markdown(text)
    assert [c.title for c in chunks] == [
        "Manual de Estoque",
        "Entrada de Produtos",
        "Baixa de Produtos",
    ]
    assert "informar o SKU" in chunks[1].content


def test_chunk_markdown_skips_empty_sections():
    text = "## Vazio\n\n## Com conteúdo\nTexto aqui.\n"
    chunks = chunk_markdown(text)
    assert [c.title for c in chunks] == ["Com conteúdo"]
