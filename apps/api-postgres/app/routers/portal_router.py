import json
import shutil
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from shared.exceptions import ConflictError
from shared.schemas.auth import TokenPayload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.core.cache import _portal_cache, _portal_lock, get_or_set, invalidate
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

    model_config = ConfigDict(from_attributes=True)


class AbaResponse(BaseModel):
    id: int
    nome: str
    icone: str
    ordem: int
    parent_id: int | None = None
    modulos: List[ModuloSchema] = []
    children: List["AbaResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class AvailableModule(BaseModel):
    slug: str
    nome: str
    url: str
    ja_vinculado: bool
    aba_vinculada: str | None = None


@router.get("/menu", response_model=List[AbaResponse])
def obter_menu_dinamico(
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    # Cache apenas a query base de abas ativas (antes do filtro por role)
    def _fetch_abas():
        return db.query(Aba).filter(Aba.ativo).order_by(Aba.ordem).all()

    abas = get_or_set(_portal_cache, _portal_lock, "abas:active", _fetch_abas)

    if current_user.role != "admin":
        accessible_ids = {
            row[0]
            for row in db.query(UsuarioModulo.modulo_id)
            .filter(UsuarioModulo.usuario_id == int(current_user.sub))
            .all()
        }

    def build_tree(abas_list, parent_id=None):
        result = []
        for aba in abas_list:
            if aba.parent_id == parent_id:
                children = build_tree(abas_list, aba.id)
                if current_user.role != "admin":
                    mods = [m for m in (aba.modulos or []) if m.id in accessible_ids]
                    if not mods and not children:
                        continue
                else:
                    mods = list(aba.modulos or [])
                result.append(
                    AbaResponse(
                        id=aba.id,
                        nome=aba.nome,
                        icone=aba.icone,
                        ordem=aba.ordem,
                        parent_id=aba.parent_id,
                        modulos=[ModuloSchema.model_validate(m) for m in mods],
                        children=children,
                    )
                )
        return result

    return build_tree(abas)


@router.get("/modules/available", response_model=List[AvailableModule])
def listar_modulos_disponiveis(
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    abas_map = {}
    for aba in db.query(Aba).all():
        abas_map[aba.id] = aba.nome

    modulos_vinculados = set()
    result = []
    for mod in db.query(Modulo).all():
        modulos_vinculados.add(mod.slug)
        result.append(
            AvailableModule(
                slug=mod.slug,
                nome=mod.nome,
                url=mod.url,
                ja_vinculado=True,
                aba_vinculada=abas_map.get(mod.aba_id),
            )
        )

    # Adiciona modulos instalados no filesystem que nao estao vinculados
    api_dir = Path(__file__).resolve().parent.parent.parent
    for base_dir in [api_dir / "app" / "modules", api_dir.parent / "api-sqlserver" / "app" / "modules"]:
        if not base_dir.exists():
            continue
        for module_dir in sorted(base_dir.iterdir()):
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue
            slug = module_dir.name
            if slug in modulos_vinculados:
                continue
            # Le module.json se existir para obter metadados
            manifest_path = module_dir / "module.json"
            nome = slug
            url = ""
            if manifest_path.exists():
                try:
                    m = json.loads(manifest_path.read_text(encoding="utf-8"))
                    nome = m.get("module_name", slug)
                    frontend_tabs = m.get("frontend_tabs", [])
                    if frontend_tabs:
                        url = frontend_tabs[0].get("url", "")
                    else:
                        url = m.get("menu_label", "")
                except Exception:
                    pass
            result.append(
                AvailableModule(
                    slug=slug,
                    nome=nome,
                    url=url,
                    ja_vinculado=False,
                )
            )

    return result


# --- Gerenciamento de Abas ---


@router.post("/abas", response_model=AbaResponse, status_code=status.HTTP_201_CREATED)
def criar_aba(
    nome: str,
    icone: str,
    ordem: int = 0,
    parent_id: int | None = None,
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    nova_aba = Aba(nome=nome, icone=icone, ordem=ordem, parent_id=parent_id)
    db.add(nova_aba)
    db.commit()
    db.refresh(nova_aba)

    # Invalida cache de abas ativas
    invalidate(_portal_cache, _portal_lock, "abas:active")
    return nova_aba


@router.put("/abas/{aba_id}", response_model=AbaResponse)
def atualizar_aba(
    aba_id: int,
    nome: str,
    icone: str,
    ordem: int,
    parent_id: int | None = None,
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    aba = db.query(Aba).filter(Aba.id == aba_id).first()
    if not aba:
        raise HTTPException(404, "Aba não encontrada")
    if parent_id is not None and parent_id == aba_id:
        raise HTTPException(422, "Uma aba não pode ser sub-aba de si mesma")
    if parent_id is not None:
        cur = db.query(Aba).filter(Aba.id == parent_id).first()
        while cur and cur.parent_id:
            if cur.parent_id == aba_id:
                raise HTTPException(422, "Ciclo detectado na hierarquia de abas")
            cur = db.query(Aba).filter(Aba.id == cur.parent_id).first()
    aba.nome = nome
    aba.icone = icone
    aba.ordem = ordem
    aba.parent_id = parent_id
    db.commit()
    db.refresh(aba)

    # Invalida cache de abas ativas
    invalidate(_portal_cache, _portal_lock, "abas:active")
    return aba


@router.delete("/abas/{aba_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_aba(
    aba_id: int, db: Session = Depends(get_db), _: None = Depends(require_role("admin"))
):
    aba = db.query(Aba).filter(Aba.id == aba_id).first()
    if not aba:
        raise HTTPException(404, "Aba não encontrada")
    db.delete(aba)
    db.commit()

    # Invalida cache de abas ativas
    invalidate(_portal_cache, _portal_lock, "abas:active")
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
    _: None = Depends(require_role("admin")),
):
    try:
        novo_mod = Modulo(aba_id=aba_id, nome=nome, slug=slug, url=url, icone=icone)
        db.add(novo_mod)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        err_msg = str(e.orig).lower() if e.orig else ""
        if "unique" in err_msg or "duplicate" in err_msg:
            raise ConflictError(f"Slug '{slug}' já existe. Use um slug diferente.")
        if "foreign" in err_msg:
            raise ConflictError(f"Aba {aba_id} não encontrada. Verifique o aba_id.")
        raise ConflictError("Erro de integridade ao criar módulo.")
    db.refresh(novo_mod)
    invalidate(_portal_cache, _portal_lock, "abas:active")
    return novo_mod


@router.put("/modulos/{modulo_id}", response_model=ModuloSchema)
def atualizar_modulo(
    modulo_id: int,
    nome: str,
    aba_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    mod = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not mod:
        raise HTTPException(404, "Módulo não encontrado")
    mod.nome = nome
    mod.aba_id = aba_id
    db.commit()
    db.refresh(mod)
    invalidate(_portal_cache, _portal_lock, "abas:active")
    return mod


@router.delete("/modulos/{modulo_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_modulo(
    modulo_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    mod = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not mod:
        raise HTTPException(404, "Módulo não encontrado")
    aba = db.query(Aba).filter(Aba.id == mod.aba_id).first()
    if aba and aba.nome.lower() in ("gestão", "gestao"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Módulos da aba Gestão são protegidos e não podem ser excluídos.",
        )

    db.query(UsuarioModulo).filter(UsuarioModulo.modulo_id == modulo_id).delete()

    api_dir = Path(__file__).resolve().parent.parent.parent

    frontend_dir = api_dir.parent / "frontend-webapp" / "modules" / mod.slug
    if frontend_dir.exists():
        shutil.rmtree(frontend_dir)

    db.delete(mod)
    db.commit()
    invalidate(_portal_cache, _portal_lock, "abas:active")
    return None
