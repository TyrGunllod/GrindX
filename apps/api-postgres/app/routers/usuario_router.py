from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from shared.schemas.auth import TokenPayload
from shared.schemas.base import PaginatedResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role_or_higher
from app.database import get_db
from app.models.usuario import Usuario, UsuarioModulo
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioModulosResponse,
    UsuarioModulosUpdate,
    UsuarioResponse,
    UsuarioUpdate,
)
from app.services.usuario_service import UsuarioService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/usuarios", tags=["Gestão de Usuários"])


@router.get("", response_model=PaginatedResponse[UsuarioResponse])
def listar_usuarios(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: None = Depends(require_role_or_higher("operador")),
):
    """Lista todos os usuários. Acesso: operador ou superior."""
    service = UsuarioService(db)
    items, total = service.listar_usuarios(page, page_size, role)

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    schema: UsuarioCreate,
    request: Request,
    current_user: TokenPayload = Depends(require_role_or_higher("operador")),
    db: Session = Depends(get_db),
):
    """Cria um novo usuário. Acesso: operador ou superior."""
    if schema.role == "admin" and current_user.role != "admin":
        raise HTTPException(403, "Apenas administradores podem criar usuários admin.")
    service = UsuarioService(db)
    result = service.criar_usuario(schema, empresa_id=current_user.company_id)
    client_ip = request.client.host if request.client else "unknown"
    logger.info(
        "usuario_criado",
        usuario_id=result.id,
        username=result.username,
        role=schema.role,
        ip=client_ip,
    )
    return result


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role_or_higher("operador")),
):
    """Busca um usuário por ID. Acesso: operador ou superior."""
    service = UsuarioService(db)
    return service.buscar_por_id(usuario_id)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int,
    schema: UsuarioUpdate,
    current_user: TokenPayload = Depends(require_role_or_higher("operador")),
    db: Session = Depends(get_db),
):
    """Atualiza dados de um usuário. Acesso: operador ou superior."""
    if current_user.role != "admin":
        target = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if target and target.role == "admin":
            raise HTTPException(
                403, "Apenas administradores podem alterar usuários admin."
            )
        if schema.role == "admin":
            raise HTTPException(
                403, "Apenas administradores podem definir o perfil admin."
            )
    service = UsuarioService(db)
    return service.atualizar_usuario(usuario_id, schema)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar_usuario(
    usuario_id: int,
    request: Request,
    current_user: TokenPayload = Depends(require_role_or_higher("operador")),
    db: Session = Depends(get_db),
):
    """Desativa um usuário (soft delete). Acesso: operador ou superior."""
    if current_user.role != "admin":
        target = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if target and target.role == "admin":
            raise HTTPException(
                403, "Apenas administradores podem desativar usuários admin."
            )
    service = UsuarioService(db)
    service.desativar_usuario(usuario_id)
    client_ip = request.client.host if request.client else "unknown"
    logger.info(
        "usuario_desativado",
        usuario_id=usuario_id,
        ip=client_ip,
    )
    return None


@router.get("/{usuario_id}/modulos", response_model=UsuarioModulosResponse)
def listar_modulos_usuario(
    usuario_id: int,
    current_user: TokenPayload = Depends(require_role_or_higher("operador")),
    db: Session = Depends(get_db),
):
    """Retorna lista de modulo_ids liberados para o usuário. Acesso: operador ou superior."""
    modulos = (
        db.query(UsuarioModulo.modulo_id)
        .filter(UsuarioModulo.usuario_id == usuario_id)
        .all()
    )
    return UsuarioModulosResponse(
        usuario_id=usuario_id, modulos=[m[0] for m in modulos]
    )


@router.put("/{usuario_id}/modulos", response_model=UsuarioModulosResponse)
def atualizar_modulos_usuario(
    usuario_id: int,
    schema: UsuarioModulosUpdate,
    current_user: TokenPayload = Depends(require_role_or_higher("operador")),
    db: Session = Depends(get_db),
):
    """Substitui a lista completa de módulos liberados. Acesso: operador ou superior."""
    # Deleta existentes
    db.query(UsuarioModulo).filter(UsuarioModulo.usuario_id == usuario_id).delete()

    # Insere novos
    for mod_id in schema.modulo_ids:
        db.add(UsuarioModulo(usuario_id=usuario_id, modulo_id=mod_id))

    db.commit()
    return UsuarioModulosResponse(usuario_id=usuario_id, modulos=schema.modulo_ids)
