from unittest.mock import MagicMock
import pytest
from shared.exceptions.base import NotFoundError, ConflictError
from app.modules.{module_name}.schemas.{module_name} import {entity_name}Create, {entity_name}Update
from app.modules.{module_name}.services.{module_name}_service import {entity_name}Service


@pytest.fixture
def mock_repository():
    return MagicMock()


@pytest.fixture
def service(mock_repository):
    return {entity_name}Service(mock_repository)


class TestBuscar:
    def test_quando_encontrado_retorna_objeto(self, service, mock_repository):
        mock_repository.buscar_por_id.return_value = MagicMock(id=1)
        result = service.buscar(1)
        assert result.id == 1
        mock_repository.buscar_por_id.assert_called_once_with(1)

    def test_quando_nao_encontrado_lanca_not_found(self, service, mock_repository):
        mock_repository.buscar_por_id.return_value = None
        with pytest.raises(NotFoundError):
            service.buscar(999)


class TestCriar:
    def test_cria_com_sucesso(self, service, mock_repository):
        mock_repository.criar.return_value = MagicMock(id=1)
        dados = {entity_name}Create(nome="Teste")
        result = service.criar(dados)
        assert result.id == 1
        mock_repository.criar.assert_called_once_with(dados)


class TestAtualizar:
    def test_atualiza_campos_fornecidos(self, service, mock_repository):
        obj = MagicMock(id=1)
        mock_repository.buscar_por_id.return_value = obj
        dados = {entity_name}Update(nome="Novo Nome")
        service.atualizar(1, dados)
        mock_repository.atualizar.assert_called_once_with(obj, dados)


class TestDesativar:
    def test_desativa_recurso_existente(self, service, mock_repository):
        obj = MagicMock(id=1)
        mock_repository.buscar_por_id.return_value = obj
        service.desativar(1)
        mock_repository.desativar.assert_called_once_with(obj)
