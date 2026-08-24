from app.rag.ingestion import chunk_csv, chunk_markdown


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


def test_chunk_markdown_keeps_subheadings_in_parent():
    text = (
        "## Cadastro de Usuário\n"
        "Clique em Novo Usuário.\n"
        "### Dados Pessoais\n"
        "Preencha nome e e-mail.\n"
        "### Endereço\n"
        "Preencha rua e cidade.\n"
    )
    chunks = chunk_markdown(text)
    assert len(chunks) == 1
    assert chunks[0].title == "Cadastro de Usuário"
    assert "Dados Pessoais" in chunks[0].content
    assert "Endereço" in chunks[0].content


def test_chunk_csv_converts_rows():
    text = "nome,email,perfil\nMaria,maria@x.com,operador\nJoao,joao@x.com,leitura\n"
    chunks = chunk_csv(text)
    assert len(chunks) == 2
    assert chunks[0].title == "Linha 2"
    assert "nome: Maria" in chunks[0].content
    assert "email: maria@x.com" in chunks[0].content
    assert "perfil: operador" in chunks[0].content


def test_chunk_csv_skips_empty_rows():
    text = "a,b\n1,2\n\n3,4\n"
    chunks = chunk_csv(text)
    assert len(chunks) == 2
