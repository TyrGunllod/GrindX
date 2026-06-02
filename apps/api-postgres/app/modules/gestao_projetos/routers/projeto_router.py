from fastapi import APIRouter, Depends, Query
from shared.schemas.base import ErrorResponse, MessageResponse, PaginatedResponse
from shared.security.permissions import Role

from app.auth.dependencies import get_gestao_projetos_service, require_role
from app.modules.gestao_projetos.schemas.projeto import ProjetoCreate, ProjetoResponse, ProjetoUpdate
from app.modules.gestao_projetos.services.projeto_service import ProjetoService

router = APIRouter(prefix="/v1/projetos", tags=["Projetos"])


@router.get(
    "",
    response_model=PaginatedResponse[ProjetoResponse],
    summary="Listar",
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA))],
)
def listar(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ProjetoService = Depends(get_gestao_projetos_service),
):
    return service.listar(page, page_size)


@router.get(
    "/{id}",
    response_model=ProjetoResponse,
    summary="Buscar por ID",
    responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA))],
)
def buscar(id: int, service: ProjetoService = Depends(get_gestao_projetos_service)):
    return service.buscar(id)


@router.post(
    "",
    response_model=ProjetoResponse,
    status_code=201,
    summary="Criar",
    responses={409: {"model": ErrorResponse}},
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR))],
)
def criar(dados: ProjetoCreate, service: ProjetoService = Depends(get_gestao_projetos_service)):
    return service.criar(dados)


@router.put(
    "/{id}",
    response_model=ProjetoResponse,
    summary="Atualizar",
    responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR))],
)
def atualizar(id: int, dados: ProjetoUpdate, service: ProjetoService = Depends(get_gestao_projetos_service)):
    return service.atualizar(id, dados)


@router.delete(
    "/{id}",
    response_model=MessageResponse,
    summary="Desativar",
    responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def desativar(id: int, service: ProjetoService = Depends(get_gestao_projetos_service)):
    service.desativar(id)
    return MessageResponse(message=f"Projeto {id} desativado com sucesso.")
