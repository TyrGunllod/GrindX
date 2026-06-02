import math

from shared.schemas.base import PaginatedResponse

from app.modules.gestao_projetos.repositories.cronograma_repository import CronogramaRepository
from app.modules.gestao_projetos.schemas.cronograma import TarefaGanttResponse


class CronogramaService:
    def __init__(self, repository: CronogramaRepository) -> None:
        self.repository = repository

    def listar_tarefas_gantt(
        self, page: int = 1, page_size: int = 100, projeto_id: int | None = None,
    ) -> PaginatedResponse:
        items, total = self.repository.listar_tarefas_gantt(page, page_size, projeto_id)
        gantt_items = [TarefaGanttResponse(**item) for item in items]
        return PaginatedResponse(
            items=gantt_items, total=total, page=page, page_size=page_size,
            total_pages=math.ceil(total / page_size) if total else 0,
        )
