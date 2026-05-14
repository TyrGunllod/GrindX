from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.services.usuario_service import UsuarioService
from app.auth.dependencies import require_role
from shared.schemas.base import PaginatedResponse

router = APIRouter(prefix="/v1/usuarios", tags=["Gestão de Usuários"])

@router.get("", response_model=PaginatedResponse[UsuarioResponse])
def listar_usuarios(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Lista todos os usuários. Acesso: admin."""
    service = UsuarioService(db)
    items, total = service.listar_usuarios(page, page_size, role)
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )

@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    schema: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Cria um novo usuário. Acesso: admin."""
    service = UsuarioService(db)
    return service.criar_usuario(schema)

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Busca um usuário por ID. Acesso: admin."""
    service = UsuarioService(db)
    return service.buscar_por_id(usuario_id)

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int,
    schema: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Atualiza dados de um usuário. Acesso: admin."""
    service = UsuarioService(db)
    return service.atualizar_usuario(usuario_id, schema)

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Desativa um usuário (soft delete). Acesso: admin."""
    service = UsuarioService(db)
    service.desativar_usuario(usuario_id)
    return None
