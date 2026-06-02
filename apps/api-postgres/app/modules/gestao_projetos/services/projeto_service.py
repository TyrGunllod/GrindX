import math

import structlog
from shared.exceptions.base import ConflictError, NotFoundError
from shared.schemas.base import PaginatedResponse

from app.modules.gestao_projetos.repositories.projeto_repository import ProjetoRepository
from app.modules.gestao_projetos.schemas.projeto import ProjetoCreate, ProjetoUpdate

logger = structlog.get_logger(__name__)


class ProjetoService:
    def __init__(self, repository: ProjetoRepository) -> None:
        self.repository = repository

    def buscar(self, id: int):
        obj = self.repository.buscar_por_id(id)
        if not obj:
            raise NotFoundError(resource="Projeto", identifier=id)
        return obj

    def listar(self, page: int = 1, page_size: int = 20) -> PaginatedResponse:
        items, total = self.repository.listar_todos(page, page_size)
        return PaginatedResponse(
            items=items, total=total, page=page, page_size=page_size,
            total_pages=math.ceil(total / page_size) if total else 0,
        )

    def criar(self, dados: ProjetoCreate):
        existente = self.repository.buscar_por_nome(dados.nome)
        if existente:
            raise ConflictError(f"Projeto '{dados.nome}' ja existe")
        obj = self.repository.criar(dados)
        logger.info("Projeto criado", id=obj.id, nome=obj.nome)
        return obj

    def atualizar(self, id: int, dados: ProjetoUpdate):
        obj = self.buscar(id)
        return self.repository.atualizar(obj, dados)

    def desativar(self, id: int):
        obj = self.buscar(id)
        return self.repository.desativar(obj)
