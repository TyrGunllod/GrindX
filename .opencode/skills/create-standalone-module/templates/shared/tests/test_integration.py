from shared.exceptions.base import NotFoundError, ConflictError
from app.modules.{module_name}.schemas.{module_name} import {entity_name}Create, {entity_name}Update


class TestRepository:
    def test_criar_e_buscar_por_id(self, repository):
        obj = repository.criar({entity_name}Create(nome="Teste"))
        assert obj.id is not None
        assert repository.buscar_por_id(obj.id) is not None

    def test_listar_com_paginacao(self, repository):
        for i in range(5):
            repository.criar({entity_name}Create(nome=f"Item {i}"))
        items, total = repository.listar_todos(page=1, page_size=2)
        assert total == 5
        assert len(items) == 2

    def test_atualizar(self, repository):
        obj = repository.criar({entity_name}Create(nome="Original"))
        dados = {entity_name}Update(nome="Alterado")
        atualizado = repository.atualizar(obj, dados)
        assert atualizado.nome == "Alterado"

    def test_desativar(self, repository):
        obj = repository.criar({entity_name}Create(nome="Teste"))
        assert obj.ativo is True
        desativado = repository.desativar(obj)
        assert desativado.ativo is False


class TestService:
    def test_buscar_inexistente_lanca_not_found(self, service):
        with pytest.raises(NotFoundError):
            service.buscar(9999)

    def test_listar_retorna_todos(self, service, repository):
        for i in range(3):
            repository.criar({entity_name}Create(nome=f"Item {i}"))
        result = service.listar()
        assert result.total == 3
