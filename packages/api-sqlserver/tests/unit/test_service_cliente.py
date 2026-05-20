"""Testes unitários do ClienteService com mock do repositório."""

from unittest.mock import MagicMock

import pytest
from app.services.cliente_service import ClienteService
from shared.exceptions.base import ClienteNaoEncontradoError, CnpjNaoEncontradoError


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    return ClienteService(mock_repo)


class TestBuscarCliente:

    def test_cliente_encontrado(self, service, mock_repo):
        mock_cliente = MagicMock()
        mock_cliente.id = 1
        mock_repo.buscar_por_id.return_value = mock_cliente

        resultado = service.buscar_cliente(1)
        assert resultado.id == 1

    def test_cliente_inexistente(self, service, mock_repo):
        mock_repo.buscar_por_id.return_value = None
        with pytest.raises(ClienteNaoEncontradoError):
            service.buscar_cliente(999)


class TestBuscarPorCnpj:

    def test_cnpj_encontrado(self, service, mock_repo):
        mock_cliente = MagicMock()
        mock_cliente.cnpj = "12.345.678/0001-90"
        mock_repo.buscar_por_cnpj.return_value = mock_cliente

        resultado = service.buscar_por_cnpj("12.345.678/0001-90")
        assert resultado.cnpj == "12.345.678/0001-90"

    def test_cnpj_inexistente(self, service, mock_repo):
        mock_repo.buscar_por_cnpj.return_value = None
        with pytest.raises(CnpjNaoEncontradoError):
            service.buscar_por_cnpj("00.000.000/0000-00")


class TestListarClientes:

    def test_listar_retorna_paginado(self, service, mock_repo):
        mock_repo.listar.return_value = ([], 0)

        resultado = service.listar_clientes(page=1, page_size=20)
        assert resultado.total == 0
        assert resultado.items == []
        assert resultado.total_pages == 0
