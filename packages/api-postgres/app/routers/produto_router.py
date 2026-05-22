"""
Router de Produto — CRUD completo com RBAC.

Todas as rotas são protegidas por JWT e prefixadas com /v1/estoque.
Controle de acesso por role:
- GET: leitura, operador, admin
- POST: operador, admin
- PUT: operador, admin
- DELETE: admin
"""

from fastapi import APIRouter, Depends, Query
from shared.schemas.base import ErrorResponse, MessageResponse, PaginatedResponse
from shared.security.permissions import Role

from app.auth.dependencies import (
    get_produto_service,
    require_role,
)
from app.schemas.produto import ProdutoCreate, ProdutoResponse, ProdutoUpdate
from app.services.produto_service import ProdutoService

router = APIRouter(prefix="/v1/estoque", tags=["Estoque"])


@router.get(
    "/produtos",
    response_model=PaginatedResponse[ProdutoResponse],
    summary="Listar produtos",
    description="Retorna lista paginada de produtos. Por padrão, somente ativos. Acesso: todos.",
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado"},
    },
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA))],
)
def listar_produtos(
    page: int = Query(default=1, ge=1, description="Número da página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    apenas_ativos: bool = Query(default=True, description="Filtrar somente ativos"),
    service: ProdutoService = Depends(get_produto_service),
) -> PaginatedResponse:
    """Lista produtos com paginação e filtro de ativos."""
    return service.listar_produtos(
        page=page,
        page_size=page_size,
        apenas_ativos=apenas_ativos,
    )


@router.get(
    "/produtos/{produto_id}",
    response_model=ProdutoResponse,
    summary="Buscar produto por ID",
    description="Retorna os dados de um produto específico pelo seu ID. Acesso: todos.",
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado"},
        404: {"model": ErrorResponse, "description": "Produto não encontrado"},
    },
    dependencies=[Depends(require_role(Role.ADMIN, Role.OPERADOR, Role.LEITURA))],
)
def buscar_produto(
    produto_id: int,
    service: ProdutoService = Depends(get_produto_service),
) -> ProdutoResponse:
    """Retorna um produto pelo ID."""
    return service.buscar_produto(produto_id)


@router.post(
    "/produtos",
    response_model=ProdutoResponse,
    status_code=201,
    summary="Criar produto",
    description="Cria um novo produto no sistema. Acesso: operador, admin.",
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado"},
        403: {
            "model": ErrorResponse,
            "description": "Permissão insuficiente (requer operador ou admin)",
        },
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
    dependencies=[Depends(require_role(Role.OPERADOR, Role.ADMIN))],
)
def criar_produto(
    dados: ProdutoCreate,
    service: ProdutoService = Depends(get_produto_service),
) -> ProdutoResponse:
    """Cria um novo produto."""
    return service.criar_produto(dados)


@router.put(
    "/produtos/{produto_id}",
    response_model=ProdutoResponse,
    summary="Atualizar produto",
    description="Atualiza campos de um produto existente. Acesso: operador, admin.",
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado"},
        403: {
            "model": ErrorResponse,
            "description": "Permissão insuficiente (requer operador ou admin)",
        },
        404: {"model": ErrorResponse, "description": "Produto não encontrado"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
    dependencies=[Depends(require_role(Role.OPERADOR, Role.ADMIN))],
)
def atualizar_produto(
    produto_id: int,
    dados: ProdutoUpdate,
    service: ProdutoService = Depends(get_produto_service),
) -> ProdutoResponse:
    """Atualiza um produto existente."""
    return service.atualizar_produto(produto_id, dados)


@router.delete(
    "/produtos/{produto_id}",
    response_model=MessageResponse,
    summary="Desativar produto",
    description="Realiza soft delete (desativação) de um produto. Acesso: admin.",
    responses={
        401: {"model": ErrorResponse, "description": "Não autenticado"},
        403: {
            "model": ErrorResponse,
            "description": "Permissão insuficiente (requer admin)",
        },
        404: {"model": ErrorResponse, "description": "Produto não encontrado"},
    },
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def desativar_produto(
    produto_id: int,
    service: ProdutoService = Depends(get_produto_service),
) -> MessageResponse:
    """Desativa (soft delete) um produto."""
    service.desativar_produto(produto_id)
    return MessageResponse(message=f"Produto {produto_id} desativado com sucesso.")
