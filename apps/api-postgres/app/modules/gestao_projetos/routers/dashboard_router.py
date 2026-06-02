from fastapi import APIRouter, Depends
from shared.security.permissions import Role

from app.auth.dependencies import get_gestao_projetos_dashboard_service, require_role
from app.modules.gestao_projetos.schemas.dashboard import DashboardResponse
from app.modules.gestao_projetos.services.dashboard_service import DashboardService

router = APIRouter(prefix="/v1/dashboard", tags=["Dashboard"])


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Dados completos do dashboard",
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA))],
)
def carregar(service: DashboardService = Depends(get_gestao_projetos_dashboard_service)):
    return service.carregar_dados()
