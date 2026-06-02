from unittest.mock import MagicMock

import pytest
from shared.exceptions.base import NotFoundError


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.buscar_por_nome.return_value = []
    return repo


@pytest.fixture
def service(mock_repository):
    from app.modules.gestao_projetos.services.projeto_service import ProjetoService
    return ProjetoService(mock_repository)


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
        from app.modules.gestao_projetos.schemas.projeto import ProjetoCreate
        dados = ProjetoCreate(nome="Projeto Teste", data_inicio="2026-01-01", data_fim="2026-03-31")
        result = service.criar(dados)
        assert result.id == 1
        mock_repository.criar.assert_called_once_with(dados)

    def test_cria_com_nome_duplicado_lanca_conflict(self, service, mock_repository):
        mock_repository.buscar_por_nome.return_value = [MagicMock()]
        from app.modules.gestao_projetos.schemas.projeto import ProjetoCreate
        dados = ProjetoCreate(nome="Duplicado", data_inicio="2026-01-01", data_fim="2026-03-31")
        with pytest.raises(Exception):
            service.criar(dados)


class TestAtualizar:
    def test_atualiza_campos_fornecidos(self, service, mock_repository):
        from app.modules.gestao_projetos.schemas.projeto import ProjetoUpdate
        obj = MagicMock(id=1)
        mock_repository.buscar_por_id.return_value = obj
        dados = ProjetoUpdate(nome="Novo Nome")
        service.atualizar(1, dados)
        mock_repository.atualizar.assert_called_once_with(obj, dados)


class TestDesativar:
    def test_desativa_projeto_existente(self, service, mock_repository):
        obj = MagicMock(id=1)
        mock_repository.buscar_por_id.return_value = obj
        service.desativar(1)
        mock_repository.desativar.assert_called_once_with(obj)
