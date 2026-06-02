from fastapi import APIRouter, Depends, Query
from shared.schemas.base import PaginatedResponse
from shared.security.permissions import Role

from app.auth.dependencies import get_gestao_projetos_cronograma_service, require_role
from app.modules.gestao_projetos.schemas.cronograma import TarefaGanttResponse
from app.modules.gestao_projetos.services.cronograma_service import CronogramaService

router = APIRouter(prefix="/v1/cronograma", tags=["Cronograma"])


@router.get(
    "/tarefas",
    response_model=PaginatedResponse[TarefaGanttResponse],
    summary="Listar tarefas para Gantt",
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA))],
)
def listar_tarefas(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    projeto_id: int | None = Query(default=None),
    service: CronogramaService = Depends(get_gestao_projetos_cronograma_service),
):
    return service.listar_tarefas_gantt(page, page_size, projeto_id)
