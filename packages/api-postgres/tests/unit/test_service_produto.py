"""Testes unitários do ProdutoService com mock do repositório."""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.schemas.produto import ProdutoCreate, ProdutoUpdate
from app.services.produto_service import ProdutoService
from shared.exceptions.base import PrecoInvalidoError, ProdutoNaoEncontradoError


@pytest.fixture
def mock_repo():
    """Mock do ProdutoRepository."""
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    """ProdutoService com repositório mockado."""
    return ProdutoService(mock_repo)


class TestBuscarProduto:
    """Testes para buscar_produto."""

    def test_produto_encontrado(self, service, mock_repo):
        mock_produto = MagicMock()
        mock_produto.id = 1
        mock_produto.nome = "Caneta"
        mock_repo.buscar_por_id.return_value = mock_produto

        resultado = service.buscar_produto(1)

        assert resultado.id == 1
        mock_repo.buscar_por_id.assert_called_once_with(1)

    def test_produto_inexistente_lanca_erro(self, service, mock_repo):
        mock_repo.buscar_por_id.return_value = None

        with pytest.raises(ProdutoNaoEncontradoError):
            service.buscar_produto(999)


class TestCriarProduto:
    """Testes para criar_produto."""

    def test_criar_produto_valido(self, service, mock_repo):
        dados = ProdutoCreate(nome="Caneta", preco=Decimal("5.00"))
        mock_produto = MagicMock()
        mock_produto.id = 1
        mock_repo.criar.return_value = mock_produto

        resultado = service.criar_produto(dados)

        assert resultado.id == 1
        mock_repo.criar.assert_called_once_with(dados)

    def test_criar_produto_preco_zero_lanca_erro(self, service):
        # O schema já valida preco > 0, mas o service tem validação adicional
        dados = MagicMock()
        dados.preco = Decimal("0")

        with pytest.raises(PrecoInvalidoError):
            service.criar_produto(dados)

    def test_criar_produto_preco_negativo_lanca_erro(self, service):
        dados = MagicMock()
        dados.preco = Decimal("-10.00")

        with pytest.raises(PrecoInvalidoError):
            service.criar_produto(dados)


class TestAtualizarProduto:
    """Testes para atualizar_produto."""

    def test_atualizar_produto_valido(self, service, mock_repo):
        mock_produto = MagicMock()
        mock_produto.id = 1
        mock_repo.buscar_por_id.return_value = mock_produto
        mock_repo.atualizar.return_value = mock_produto

        dados = ProdutoUpdate(nome="Novo Nome")
        resultado = service.atualizar_produto(1, dados)

        assert resultado is not None
        mock_repo.atualizar.assert_called_once()

    def test_atualizar_produto_inexistente_lanca_erro(self, service, mock_repo):
        mock_repo.buscar_por_id.return_value = None
        dados = ProdutoUpdate(nome="Novo Nome")

        with pytest.raises(ProdutoNaoEncontradoError):
            service.atualizar_produto(999, dados)

    def test_atualizar_preco_invalido_lanca_erro(self, service, mock_repo):
        mock_produto = MagicMock()
        mock_repo.buscar_por_id.return_value = mock_produto
        # Usa MagicMock para bypassar a validação do schema Pydantic
        # e testar a validação de negócio no service
        dados = MagicMock()
        dados.preco = Decimal("-5.00")

        with pytest.raises(PrecoInvalidoError):
            service.atualizar_produto(1, dados)


class TestDesativarProduto:
    """Testes para desativar_produto."""

    def test_desativar_produto_existente(self, service, mock_repo):
        mock_produto = MagicMock()
        mock_repo.buscar_por_id.return_value = mock_produto
        mock_repo.desativar.return_value = mock_produto

        resultado = service.desativar_produto(1)

        assert resultado is not None
        mock_repo.desativar.assert_called_once_with(mock_produto)

    def test_desativar_produto_inexistente_lanca_erro(self, service, mock_repo):
        mock_repo.buscar_por_id.return_value = None

        with pytest.raises(ProdutoNaoEncontradoError):
            service.desativar_produto(999)
