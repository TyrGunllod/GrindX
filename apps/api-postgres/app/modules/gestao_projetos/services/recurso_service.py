import math

import structlog
from shared.exceptions.base import ConflictError, NotFoundError
from shared.schemas.base import PaginatedResponse

from app.modules.gestao_projetos.repositories.recurso_repository import RecursoRepository
from app.modules.gestao_projetos.schemas.recurso import RecursoCreate, RecursoUpdate

logger = structlog.get_logger(__name__)


class RecursoService:
    def __init__(self, repository: RecursoRepository) -> None:
        self.repository = repository

    def buscar(self, id: int):
        obj = self.repository.buscar_por_id(id)
        if not obj:
            raise NotFoundError(resource="Recurso", identifier=id)
        return obj

    def listar(self, page: int = 1, page_size: int = 20, projeto_id: int | None = None) -> PaginatedResponse:
        items, total = self.repository.listar_todos(page, page_size, projeto_id)
        return PaginatedResponse(
            items=items, total=total, page=page, page_size=page_size,
            total_pages=math.ceil(total / page_size) if total else 0,
        )

    def criar(self, dados: RecursoCreate):
        existente = self.repository.buscar_por_user_projeto(dados.user_id, dados.projeto_id)
        if existente:
            raise ConflictError(f"Recurso ja alocado neste projeto")
        obj = self.repository.criar(dados)
        logger.info("Recurso criado", id=obj.id, user_id=obj.user_id)
        return obj

    def atualizar(self, id: int, dados: RecursoUpdate):
        obj = self.buscar(id)
        return self.repository.atualizar(obj, dados)

    def desalocar(self, id: int):
        obj = self.buscar(id)
        return self.repository.desalocar(obj)
