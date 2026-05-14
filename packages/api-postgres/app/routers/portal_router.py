from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.portal import Aba, Modulo
from app.auth.dependencies import require_role
from pydantic import BaseModel

router = APIRouter(prefix="/v1/portal", tags=["Estrutura do Portal"])

# Schemas Simples
class ModuloSchema(BaseModel):
    id: int
    nome: str
    url: str
    icone: str
    role_minima: str

class AbaResponse(BaseModel):
    id: int
    nome: str
    icone: str
    modulos: List[ModuloSchema]

@router.get("/menu", response_model=List[AbaResponse])
def obter_menu_dinamico(db: Session = Depends(get_db)):
    """Retorna a estrutura de abas e módulos ativos para montar o menu."""
    abas = db.query(Aba).filter(Aba.ativo == True).order_by(Aba.ordem).all()
    return abas

@router.post("/abas", status_code=status.HTTP_201_CREATED)
def criar_aba(nome: str, icone: str, ordem: int = 0, db: Session = Depends(get_db), admin = Depends(require_role("admin"))):
    nova_aba = Aba(nome=nome, icone=icone, ordem=ordem)
    db.add(nova_aba)
    db.commit()
    return {"message": "Aba criada"}

@router.post("/modulos", status_code=status.HTTP_201_CREATED)
def criar_modulo(aba_id: int, nome: str, slug: str, url: str, icone: str, db: Session = Depends(get_db), admin = Depends(require_role("admin"))):
    novo_mod = Modulo(aba_id=aba_id, nome=nome, slug=slug, url=url, icone=icone)
    db.add(novo_mod)
    db.commit()
    return {"message": "Módulo criado"}
