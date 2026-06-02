import pytest
from shared.exceptions.base import NotFoundError, ConflictError


class TestRepository:
    def test_criar_e_buscar_por_id(self, recurso_repository):
        from app.modules.gestao_projetos.schemas.recurso import RecursoCreate
        obj = recurso_repository.criar(RecursoCreate(user_id=1, projeto_id=1))
        assert obj.id is not None
        assert recurso_repository.buscar_por_id(obj.id) is not None

    def test_listar_por_projeto(self, recurso_repository):
        from app.modules.gestao_projetos.schemas.recurso import RecursoCreate
        recurso_repository.criar(RecursoCreate(user_id=1, projeto_id=1))
        recurso_repository.criar(RecursoCreate(user_id=2, projeto_id=1))
        recurso_repository.criar(RecursoCreate(user_id=3, projeto_id=2))
        items, total = recurso_repository.listar_todos(page=1, page_size=10, projeto_id=1)
        assert total == 2

    def test_desalocar(self, recurso_repository):
        from app.modules.gestao_projetos.schemas.recurso import RecursoCreate
        obj = recurso_repository.criar(RecursoCreate(user_id=1, projeto_id=1))
        assert obj.alocado is True
        desalocado = recurso_repository.desalocar(obj)
        assert desalocado.alocado is False


class TestService:
    def test_criar_duplicado_lanca_conflict(self, recurso_service, recurso_repository):
        from app.modules.gestao_projetos.schemas.recurso import RecursoCreate
        recurso_repository.criar(RecursoCreate(user_id=1, projeto_id=1))
        with pytest.raises(ConflictError):
            recurso_service.criar(RecursoCreate(user_id=1, projeto_id=1))
