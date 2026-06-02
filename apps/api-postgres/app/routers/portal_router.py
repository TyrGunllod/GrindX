from pathlib import Path
from typing import List

import json
import structlog
import zipfile
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from shared.schemas.auth import TokenPayload
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.core.config import settings
from app.database import get_db
from app.models.portal import Aba, Modulo
from app.models.usuario import UsuarioModulo

logger = structlog.get_logger(__name__)

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
    fonte: str = "pasta"


@router.get("/menu", response_model=List[AbaResponse])
def obter_menu_dinamico(
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    abas = db.query(Aba).filter(Aba.ativo).order_by(Aba.ordem).all()

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
    api_dir = Path(__file__).resolve().parent.parent.parent
    frontend_modules_dir = api_dir.parent / "frontend-webapp" / "modules"

    vinculados = {}
    for mod in db.query(Modulo).all():
        vinculados[mod.slug] = mod.aba_id

    abas_map = {}
    for aba in db.query(Aba).all():
        abas_map[aba.id] = aba.nome

    result = []
    seen_slugs = set()

    if frontend_modules_dir.exists():
        for entry in sorted(frontend_modules_dir.iterdir()):
            if not entry.is_dir() or entry.name.startswith("_"):
                continue
            index_file = entry / "index.html"
            if not index_file.exists():
                continue

            slug = entry.name
            ja_vinculado = slug in vinculados
            aba_vinculada = abas_map.get(vinculados.get(slug)) if ja_vinculado else None

            result.append(AvailableModule(
                slug=slug,
                nome=slug.replace("-", " ").replace("_", " ").title(),
                url=f"modules/{slug}/index.html",
                ja_vinculado=ja_vinculado,
                aba_vinculada=aba_vinculada,
            ))
            seen_slugs.add(slug)

    import_dir = Path(settings.import_dir_path)
    if import_dir.exists():
        for zip_path in sorted(import_dir.glob("*.zip")):
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    if "module.json" not in zf.namelist():
                        continue
                    with zf.open("module.json") as f:
                        manifest = json.load(f)
            except Exception as e:
                logger.warning("Erro ao ler manifest de %s: %s", zip_path.name, e)
                continue

            slug = manifest.get("module_name", zip_path.stem)
            if slug in seen_slugs:
                continue

            frontend_url = manifest.get("frontend_url", f"modules/{slug}/index.html")
            ja_vinculado = slug in vinculados
            aba_vinculada = abas_map.get(vinculados.get(slug)) if ja_vinculado else None

            result.append(AvailableModule(
                slug=slug,
                nome=manifest.get("menu_label", slug.replace("-", " ").replace("_", " ").title()),
                url=frontend_url,
                ja_vinculado=ja_vinculado,
                aba_vinculada=aba_vinculada,
                fonte="zip",
            ))
            seen_slugs.add(slug)

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
    novo_mod = Modulo(aba_id=aba_id, nome=nome, slug=slug, url=url, icone=icone)
    db.add(novo_mod)
    db.commit()
    db.refresh(novo_mod)
    return novo_mod


@router.put("/modulos/{modulo_id}", response_model=ModuloSchema)
def atualizar_modulo(
    modulo_id: int,
    nome: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    mod = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not mod:
        raise HTTPException(404, "Módulo não encontrado")
    mod.nome = nome
    db.commit()
    db.refresh(mod)
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
    db.delete(mod)
    db.commit()
    return None
