"""
Router para gestão de temas/skins de empresas.

Endpoints para CRUD de temas e ativação.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from shared.exceptions.base import ConflictError, NotFoundError
from shared.schemas.base import ErrorResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_db, require_role
from app.repositories.theme_repository import ThemeRepository
from app.schemas.theme import ThemeCreate, ThemeResponse, ThemeUpdate
from app.services.theme_service import ThemeService

router = APIRouter(prefix="/v1/themes", tags=["Temas"])


def _get_theme_service(db: Session = Depends(get_db)) -> ThemeService:
    repo = ThemeRepository(db)
    return ThemeService(repo)


def _require_company_id(current_user) -> int:
    """Valida que o usuário possui empresa vinculada."""
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não possui empresa vinculada. Vincule uma empresa antes de gerenciar temas.",
        )
    return current_user.company_id


@router.get(
    "/active",
    response_model=ThemeResponse,
    summary="Tema ativo da empresa",
    description="Retorna o tema ativo da empresa do usuário logado.",
    responses={404: {"model": ErrorResponse, "description": "Nenhum tema ativo encontrado"}},
)
def get_active_theme(
    current_user=Depends(get_current_user),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Retorna o tema ativo da empresa do usuário."""
    if not current_user.company_id:
        raise HTTPException(status_code=404, detail="Usuário não possui empresa vinculada")

    theme = service.get_active_theme(current_user.company_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Nenhum tema ativo encontrado para esta empresa")
    return theme


@router.get(
    "",
    response_model=list[ThemeResponse],
    summary="Listar temas",
    description="Lista todos os temas da empresa do usuário logado. Requer role admin.",
)
def list_themes(
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> list[dict]:
    """Lista todos os temas da empresa."""
    company_id = _require_company_id(current_user)
    return service.list_themes(company_id)


@router.get(
    "/{theme_id}",
    response_model=ThemeResponse,
    summary="Detalhes do tema",
    description="Retorna detalhes de um tema específico. Requer role admin.",
    responses={404: {"model": ErrorResponse, "description": "Tema não encontrado"}},
)
def get_theme(
    theme_id: int,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Retorna detalhes de um tema."""
    company_id = _require_company_id(current_user)
    theme = service.get_theme_by_id(theme_id)
    if theme is None or theme["company_id"] != company_id:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    return theme


@router.post(
    "",
    response_model=ThemeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tema",
    description="Cria um novo tema para a empresa. Requer role admin.",
)
def create_theme(
    dados: ThemeCreate,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Cria um novo tema."""
    company_id = _require_company_id(current_user)
    return service.create_theme(company_id=company_id, **dados.model_dump())


@router.put(
    "/{theme_id}",
    response_model=ThemeResponse,
    summary="Atualizar tema",
    description="Atualiza um tema existente. Requer role admin.",
    responses={404: {"model": ErrorResponse, "description": "Tema não encontrado"}},
)
def update_theme(
    theme_id: int,
    dados: ThemeUpdate,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Atualiza um tema."""
    company_id = _require_company_id(current_user)
    update_data = dados.model_dump(exclude_unset=True)
    return service.update_theme(theme_id, company_id=company_id, **update_data)


@router.post(
    "/{theme_id}/activate",
    response_model=ThemeResponse,
    summary="Ativar tema",
    description="Ativa um tema e desativa os outros da mesma empresa. Requer role admin.",
    responses={404: {"model": ErrorResponse, "description": "Tema não encontrado"}},
)
def activate_theme(
    theme_id: int,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Ativa um tema."""
    company_id = _require_company_id(current_user)
    try:
        return service.activate_theme(theme_id, company_id=company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete(
    "/{theme_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar tema",
    description="Deleta um tema. Não pode deletar tema ativo. Requer role admin.",
    responses={
        404: {"model": ErrorResponse, "description": "Tema não encontrado"},
        409: {"model": ErrorResponse, "description": "Tema está ativo"},
    },
)
def delete_theme(
    theme_id: int,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> None:
    """Deleta um tema."""
    _require_company_id(current_user)
    try:
        service.delete_theme(theme_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
