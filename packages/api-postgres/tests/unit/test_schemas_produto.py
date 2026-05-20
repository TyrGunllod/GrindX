"""Testes unitários dos schemas Pydantic de Produto."""

from decimal import Decimal

import pytest
from app.schemas.produto import ProdutoCreate, ProdutoResponse, ProdutoUpdate
from pydantic import ValidationError


class TestProdutoCreate:
    """Testes para o schema ProdutoCreate."""

    def test_criar_produto_valido(self):
        produto = ProdutoCreate(nome="Caneta Azul", preco=Decimal("2.50"))
        assert produto.nome == "Caneta Azul"
        assert produto.preco == Decimal("2.50")
        assert produto.ativo is True

    def test_preco_negativo_levanta_erro(self):
        with pytest.raises(ValidationError) as exc_info:
            ProdutoCreate(nome="Teste", preco=Decimal("-1.00"))
        assert "greater than 0" in str(exc_info.value).lower()

    def test_preco_zero_levanta_erro(self):
        with pytest.raises(ValidationError):
            ProdutoCreate(nome="Teste", preco=Decimal("0.00"))

    def test_nome_vazio_levanta_erro(self):
        with pytest.raises(ValidationError):
            ProdutoCreate(nome="   ", preco=Decimal("10.00"))

    def test_nome_curto_levanta_erro(self):
        with pytest.raises(ValidationError):
            ProdutoCreate(nome="A", preco=Decimal("10.00"))

    def test_nome_longo_levanta_erro(self):
        with pytest.raises(ValidationError):
            ProdutoCreate(nome="X" * 101, preco=Decimal("10.00"))

    def test_nome_strip_espacos(self):
        produto = ProdutoCreate(nome="  Caneta  ", preco=Decimal("5.00"))
        assert produto.nome == "Caneta"

    def test_descricao_opcional(self):
        produto = ProdutoCreate(nome="Caneta", preco=Decimal("5.00"))
        assert produto.descricao is None

    def test_descricao_com_valor(self):
        produto = ProdutoCreate(
            nome="Caneta", preco=Decimal("5.00"), descricao="Ponta fina"
        )
        assert produto.descricao == "Ponta fina"


class TestProdutoUpdate:
    """Testes para o schema ProdutoUpdate."""

    def test_update_parcial_nome(self):
        update = ProdutoUpdate(nome="Novo Nome")
        assert update.nome == "Novo Nome"
        assert update.preco is None
        assert update.ativo is None

    def test_update_parcial_preco(self):
        update = ProdutoUpdate(preco=Decimal("15.00"))
        assert update.preco == Decimal("15.00")
        assert update.nome is None

    def test_update_preco_negativo_levanta_erro(self):
        with pytest.raises(ValidationError):
            ProdutoUpdate(preco=Decimal("-5.00"))

    def test_update_vazio_valido(self):
        update = ProdutoUpdate()
        dados = update.model_dump(exclude_unset=True)
        assert dados == {}


class TestProdutoResponse:
    """Testes para o schema ProdutoResponse."""

    def test_from_attributes(self):
        """Valida que o schema aceita objetos com atributos (ORM mode)."""

        class FakeProduto:
            id = 1
            nome = "Caneta"
            descricao = None
            preco = Decimal("2.50")
            ativo = True
            criado_em = "2025-01-01T00:00:00Z"
            atualizado_em = "2025-01-01T00:00:00Z"

        response = ProdutoResponse.model_validate(FakeProduto())
        assert response.id == 1
        assert response.nome == "Caneta"
