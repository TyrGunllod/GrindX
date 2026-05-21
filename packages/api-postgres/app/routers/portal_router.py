from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from shared.schemas.auth import TokenPayload
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.database import get_db
from app.models.portal import Aba, Modulo
from app.models.usuario import UsuarioModulo

router = APIRouter(prefix="/v1/portal", tags=["Estrutura do Portal"])


# Schemas
class ModuloSchema(BaseModel):
    id: int
    aba_id: int
    nome: str
    url: str
    icone: str
    slug: str
    role_minima: str


class AbaResponse(BaseModel):
    id: int
    nome: str
    icone: str
    ordem: int
    modulos: List[ModuloSchema]


@router.get("/menu", response_model=List[AbaResponse])
def obter_menu_dinamico(
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    if current_user.role == "admin":
        abas = db.query(Aba).filter(Aba.ativo).order_by(Aba.ordem).all()
    else:
        # Só retorna módulos que o usuário tem permissão
        modulos_ids = (
            db.query(UsuarioModulo.modulo_id)
            .filter(UsuarioModulo.usuario_id == int(current_user.sub))
            .subquery()
        )
        abas = (
            db.query(Aba)
            .join(Modulo)
            .filter(Aba.ativo, Modulo.id.in_(modulos_ids))
            .order_by(Aba.ordem)
            .all()
        )
    return abas


# --- Gerenciamento de Abas ---


@router.post("/abas", response_model=AbaResponse, status_code=status.HTTP_201_CREATED)
def criar_aba(
    nome: str,
    icone: str,
    ordem: int = 0,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin")),
):
    nova_aba = Aba(nome=nome, icone=icone, ordem=ordem)
    db.add(nova_aba)
    db.commit()
    db.refresh(nova_aba)
    return nova_aba


@router.put("/abas/{aba_id}", response_model=AbaResponse)
def atualizar_aba(
    aba_id: int,
    nome: str,
    icone: str,
    ordem: int,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin")),
):
    aba = db.query(Aba).filter(Aba.id == aba_id).first()
    if not aba:
        raise HTTPException(404, "Aba não encontrada")
    aba.nome = nome
    aba.icone = icone
    aba.ordem = ordem
    db.commit()
    db.refresh(aba)
    return aba


@router.delete("/abas/{aba_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_aba(
    aba_id: int, db: Session = Depends(get_db), admin=Depends(require_role("admin"))
):
    aba = db.query(Aba).filter(Aba.id == aba_id).first()
    if not aba:
        raise HTTPException(404, "Aba não encontrada")
    db.delete(aba)
    db.commit()
    return None


# --- Gerenciamento de Módulos ---


@router.post(
    "/modulos", response_model=ModuloSchema, status_code=status.HTTP_201_CREATED
)
def criar_modulo(
    aba_id: int,
    nome: str,
    slug: str,
    url: str,
    icone: str,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin")),
):
    novo_mod = Modulo(aba_id=aba_id, nome=nome, slug=slug, url=url, icone=icone)
    db.add(novo_mod)
    db.commit()
    db.refresh(novo_mod)
    return novo_mod


@router.put("/modulos/{modulo_id}", response_model=ModuloSchema)
def atualizar_modulo(
    modulo_id: int,
    nome: str,
    slug: str,
    url: str,
    icone: str,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin")),
):
    mod = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not mod:
        raise HTTPException(404, "Módulo não encontrado")
    mod.nome = nome
    mod.slug = slug
    mod.url = url
    mod.icone = icone
    db.commit()
    db.refresh(mod)
    return mod


@router.delete("/modulos/{modulo_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_modulo(
    modulo_id: int, db: Session = Depends(get_db), admin=Depends(require_role("admin"))
):
    mod = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not mod:
        raise HTTPException(404, "Módulo não encontrado")
    db.delete(mod)
    db.commit()
    return None
