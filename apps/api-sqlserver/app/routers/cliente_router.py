"""
Router de Cliente — SOMENTE LEITURA.

Endpoints de consulta conectados ao SQL Server na nuvem.
Todas as rotas são protegidas por JWT (emitido pela api-postgres).
"""

from fastapi import APIRouter, Depends, Query
from shared.schemas.base import ErrorResponse, PaginatedResponse

from app.auth.dependencies import get_cliente_service, get_current_user
from app.schemas.cliente import ClienteResponse
from app.services.cliente_service import ClienteService

router = APIRouter(prefix="/v1/cadastro", tags=["Cadastro"])


@router.get(
    "/clientes",
    response_model=PaginatedResponse[ClienteResponse],
    summary="Listar clientes",
    description="Retorna lista paginada de clientes com filtros opcionais. Dados do SQL Server (somente leitura).",
    responses={401: {"model": ErrorResponse, "description": "Não autenticado"}},
    dependencies=[Depends(get_current_user)],
)
def listar_clientes(
    page: int = Query(default=1, ge=1, description="Número da página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    apenas_ativos: bool = Query(default=True, description="Filtrar somente ativos"),
    razao_social: str | None = Query(
        default=None, description="Filtro por razão social"
    ),
    cidade: str | None = Query(default=None, description="Filtro por cidade"),
    uf: str | None = Query(default=None, max_length=2, description="Filtro por UF"),
    service: ClienteService = Depends(get_cliente_service),
) -> PaginatedResponse:
    """Lista clientes com paginação e filtros."""
    return service.listar_clientes(
        page=page,
        page_size=page_size,
        apenas_ativos=apenas_ativos,
        razao_social=razao_social,
        cidade=cidade,
        uf=uf,
    )


@router.get(
    "/clientes/{cliente_id}",
    response_model=ClienteResponse,
    summary="Buscar cliente por ID",
    description="Retorna os dados de um cliente específico.",
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado"},
        404: {"model": ErrorResponse, "description": "Cliente não encontrado"},
    },
    dependencies=[Depends(get_current_user)],
)
def buscar_cliente(
    cliente_id: int,
    service: ClienteService = Depends(get_cliente_service),
) -> ClienteResponse:
    """Retorna um cliente pelo ID."""
    return service.buscar_cliente(cliente_id)


@router.get(
    "/clientes/cnpj/{cnpj}",
    response_model=ClienteResponse,
    summary="Buscar cliente por CNPJ",
    description="Retorna os dados de um cliente pelo CNPJ.",
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado"},
        404: {"model": ErrorResponse, "description": "Cliente não encontrado"},
    },
    dependencies=[Depends(get_current_user)],
)
def buscar_por_cnpj(
    cnpj: str,
    service: ClienteService = Depends(get_cliente_service),
) -> ClienteResponse:
    """Retorna um cliente pelo CNPJ."""
    return service.buscar_por_cnpj(cnpj)
