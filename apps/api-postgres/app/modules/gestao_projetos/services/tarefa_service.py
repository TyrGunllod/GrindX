import math

import structlog
from shared.exceptions.base import NotFoundError
from shared.schemas.base import PaginatedResponse

from app.modules.gestao_projetos.repositories.tarefa_repository import TarefaRepository
from app.modules.gestao_projetos.schemas.tarefa import TarefaCreate, TarefaUpdate

logger = structlog.get_logger(__name__)


class TarefaService:
    def __init__(self, repository: TarefaRepository) -> None:
        self.repository = repository

    def buscar(self, id: int):
        obj = self.repository.buscar_por_id(id)
        if not obj:
            raise NotFoundError(resource="Tarefa", identifier=id)
        return obj

    def listar(
        self, page: int = 1, page_size: int = 20,
        projeto_id: int | None = None, status: str | None = None,
    ) -> PaginatedResponse:
        items, total = self.repository.listar_todos(page, page_size, projeto_id, status)
        return PaginatedResponse(
            items=items, total=total, page=page, page_size=page_size,
            total_pages=math.ceil(total / page_size) if total else 0,
        )

    def criar(self, dados: TarefaCreate):
        obj = self.repository.criar(dados)
        logger.info("Tarefa criada", id=obj.id, titulo=obj.titulo)
        return obj

    def atualizar(self, id: int, dados: TarefaUpdate):
        obj = self.buscar(id)
        return self.repository.atualizar(obj, dados)

    def desativar(self, id: int):
        obj = self.buscar(id)
        return self.repository.desativar(obj)
