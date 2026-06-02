import pytest
from shared.exceptions.base import NotFoundError


class TestRepository:
    def test_criar_e_buscar_por_id(self, tarefa_repository):
        from app.modules.gestao_projetos.schemas.tarefa import TarefaCreate
        obj = tarefa_repository.criar(TarefaCreate(titulo="Tarefa Teste", data_inicio="2026-01-01", data_fim="2026-01-15"))
        assert obj.id is not None
        assert obj.titulo == "Tarefa Teste"
        assert obj.status == "todo"

    def test_listar_com_filtro_status(self, tarefa_repository):
        from app.modules.gestao_projetos.schemas.tarefa import TarefaCreate
        tarefa_repository.criar(TarefaCreate(titulo="T1", data_inicio="2026-01-01", data_fim="2026-01-15", status="todo"))
        tarefa_repository.criar(TarefaCreate(titulo="T2", data_inicio="2026-01-01", data_fim="2026-01-15", status="done"))
        items, total = tarefa_repository.listar_todos(page=1, page_size=10, status="todo")
        assert total == 1
        assert items[0].titulo == "T1"


class TestService:
    def test_buscar_inexistente_lanca_not_found(self, tarefa_service):
        with pytest.raises(NotFoundError):
            tarefa_service.buscar(9999)
