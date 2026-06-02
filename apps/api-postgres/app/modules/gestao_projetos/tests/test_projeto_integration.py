import pytest
from shared.exceptions.base import NotFoundError


class TestRepository:
    def test_criar_e_buscar_por_id(self, repository):
        from app.modules.gestao_projetos.schemas.projeto import ProjetoCreate
        obj = repository.criar(ProjetoCreate(nome="Teste", data_inicio="2026-01-01", data_fim="2026-03-31"))
        assert obj.id is not None
        assert obj.nome == "Teste"
        assert obj.status == "planning"
        assert repository.buscar_por_id(obj.id) is not None

    def test_listar_com_paginacao(self, repository):
        from app.modules.gestao_projetos.schemas.projeto import ProjetoCreate
        for i in range(5):
            repository.criar(ProjetoCreate(nome=f"Item {i}", data_inicio="2026-01-01", data_fim="2026-03-31"))
        items, total = repository.listar_todos(page=1, page_size=2)
        assert total == 5
        assert len(items) == 2

    def test_atualizar(self, repository):
        from app.modules.gestao_projetos.schemas.projeto import ProjetoCreate, ProjetoUpdate
        obj = repository.criar(ProjetoCreate(nome="Original", data_inicio="2026-01-01", data_fim="2026-03-31"))
        dados = ProjetoUpdate(nome="Alterado")
        atualizado = repository.atualizar(obj, dados)
        assert atualizado.nome == "Alterado"

    def test_desativar(self, repository):
        from app.modules.gestao_projetos.schemas.projeto import ProjetoCreate
        obj = repository.criar(ProjetoCreate(nome="Teste", data_inicio="2026-01-01", data_fim="2026-03-31"))
        assert obj.ativo is True
        desativado = repository.desativar(obj)
        assert desativado.ativo is False


class TestService:
    def test_buscar_inexistente_lanca_not_found(self, service):
        with pytest.raises(NotFoundError):
            service.buscar(9999)

    def test_listar_retorna_todos(self, service, repository):
        from app.modules.gestao_projetos.schemas.projeto import ProjetoCreate
        for i in range(3):
            repository.criar(ProjetoCreate(nome=f"Item {i}", data_inicio="2026-01-01", data_fim="2026-03-31"))
        result = service.listar()
        assert result.total == 3
