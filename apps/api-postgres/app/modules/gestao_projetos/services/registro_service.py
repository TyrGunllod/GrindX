import math

import structlog
from shared.exceptions.base import NotFoundError
from shared.schemas.base import PaginatedResponse

from app.modules.gestao_projetos.repositories.registro_repository import RegistroRepository
from app.modules.gestao_projetos.schemas.registro_tarefa import RegistroCreate, RegistroUpdate

logger = structlog.get_logger(__name__)


class RegistroService:
    def __init__(self, repository: RegistroRepository) -> None:
        self.repository = repository

    def buscar(self, id: int):
        obj = self.repository.buscar_por_id(id)
        if not obj:
            raise NotFoundError(resource="Registro", identifier=id)
        return obj

    def listar_por_tarefa(
        self, tarefa_id: int, page: int = 1, page_size: int = 50, tipo: str | None = None,
    ) -> PaginatedResponse:
        items, total = self.repository.listar_por_tarefa(tarefa_id, page, page_size, tipo)
        return PaginatedResponse(
            items=items, total=total, page=page, page_size=page_size,
            total_pages=math.ceil(total / page_size) if total else 0,
        )

    def criar(self, tarefa_id: int, dados: RegistroCreate):
        obj = self.repository.criar(tarefa_id, dados)
        logger.info("Registro criado", id=obj.id, tarefa_id=tarefa_id, tipo=obj.tipo)
        return obj

    def atualizar(self, id: int, dados: RegistroUpdate):
        obj = self.buscar(id)
        return self.repository.atualizar(obj, dados)

    def desativar(self, id: int):
        obj = self.buscar(id)
        return self.repository.desativar(obj)
