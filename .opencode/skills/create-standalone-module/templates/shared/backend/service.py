import math

import structlog
from shared.exceptions.base import ConflictError, NotFoundError
from shared.schemas.base import PaginatedResponse

from app.modules.{module_name}.repositories.{module_name}_repository import {entity_name}Repository
from app.modules.{module_name}.schemas.{module_name} import {entity_name}Create, {entity_name}Update

logger = structlog.get_logger(__name__)


class {entity_name}Service:
    def __init__(self, repository: {entity_name}Repository) -> None:
        self.repository = repository

    def buscar(self, id: int):
        obj = self.repository.buscar_por_id(id)
        if not obj:
            raise NotFoundError(resource="{entity_name}", identifier=id)
        return obj

    def listar(self, page: int = 1, page_size: int = 20) -> PaginatedResponse:
        items, total = self.repository.listar_todos(page, page_size)
        return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, total_pages=math.ceil(total / page_size) if total else 0)

    def criar(self, dados: {entity_name}Create):
        obj = self.repository.criar(dados)
        logger.info("{entity_name} criado", id=obj.id, nome=obj.nome)
        return obj

    def atualizar(self, id: int, dados: {entity_name}Update):
        obj = self.buscar(id)
        return self.repository.atualizar(obj, dados)

    def desativar(self, id: int):
        obj = self.buscar(id)
        return self.repository.desativar(obj)
