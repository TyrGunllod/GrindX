from unittest.mock import MagicMock

import pytest
from shared.exceptions.base import NotFoundError


@pytest.fixture
def mock_repository():
    return MagicMock()


@pytest.fixture
def service(mock_repository):
    from app.modules.gestao_projetos.services.tarefa_service import TarefaService
    return TarefaService(mock_repository)


class TestBuscar:
    def test_quando_encontrado_retorna_objeto(self, service, mock_repository):
        mock_repository.buscar_por_id.return_value = MagicMock(id=1)
        result = service.buscar(1)
        assert result.id == 1

    def test_quando_nao_encontrado_lanca_not_found(self, service, mock_repository):
        mock_repository.buscar_por_id.return_value = None
        with pytest.raises(NotFoundError):
            service.buscar(999)


class TestCriar:
    def test_cria_com_sucesso(self, service, mock_repository):
        mock_repository.criar.return_value = MagicMock(id=1)
        from app.modules.gestao_projetos.schemas.tarefa import TarefaCreate
        dados = TarefaCreate(titulo="Tarefa Teste", data_inicio="2026-01-01", data_fim="2026-01-15")
        result = service.criar(dados)
        assert result.id == 1
