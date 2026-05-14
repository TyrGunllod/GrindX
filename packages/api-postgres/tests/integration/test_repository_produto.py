"""Testes de integração do repositório de Produto com banco SQLite."""

from decimal import Decimal

from app.models.produto import Produto
from app.repositories.produto_repository import ProdutoRepository
from app.schemas.produto import ProdutoCreate, ProdutoUpdate


class TestProdutoRepository:

    def test_criar_produto(self, db_session):
        repo = ProdutoRepository(db_session)
        dados = ProdutoCreate(nome="Caneta", preco=Decimal("2.50"))
        produto = repo.criar(dados)
        assert produto.id is not None
        assert produto.nome == "Caneta"

    def test_buscar_por_id_existente(self, db_session):
        repo = ProdutoRepository(db_session)
        criado = repo.criar(ProdutoCreate(nome="Lápis", preco=Decimal("1.00")))
        resultado = repo.buscar_por_id(criado.id)
        assert resultado is not None
        assert resultado.nome == "Lápis"

    def test_buscar_por_id_inexistente(self, db_session):
        repo = ProdutoRepository(db_session)
        assert repo.buscar_por_id(9999) is None

    def test_listar_ativos(self, db_session):
        repo = ProdutoRepository(db_session)
        repo.criar(ProdutoCreate(nome="Ativo", preco=Decimal("5.00")))
        inativo = repo.criar(ProdutoCreate(nome="Inativo", preco=Decimal("3.00")))
        repo.desativar(inativo)
        ativos, total = repo.listar_ativos()
        assert total == 1

    def test_atualizar_produto(self, db_session):
        repo = ProdutoRepository(db_session)
        produto = repo.criar(ProdutoCreate(nome="Original", preco=Decimal("10.00")))
        atualizado = repo.atualizar(produto, ProdutoUpdate(nome="Novo"))
        assert atualizado.nome == "Novo"

    def test_desativar_produto(self, db_session):
        repo = ProdutoRepository(db_session)
        produto = repo.criar(ProdutoCreate(nome="Teste", preco=Decimal("5.00")))
        desativado = repo.desativar(produto)
        assert desativado.ativo is False
