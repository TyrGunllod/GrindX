"""
Router para gestão de temas/skins de empresas.

Endpoints para CRUD de temas e ativação.
"""

import os

import filetype
import structlog
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from shared.exceptions.base import ConflictError, NotFoundError
from shared.schemas.base import ErrorResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_db, require_role
from app.repositories.theme_repository import ThemeRepository
from app.schemas.theme import ThemeCreate, ThemeFontResponse, ThemeResponse, ThemeUpdate
from app.schemas.theme_history import ThemeHistoryResponse
from app.services.theme_service import ThemeService


class TemplateRequest(BaseModel):
    template_slug: str
    name: str


logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/themes", tags=["Temas"])


def _validate_file_magic(
    file_bytes: bytes, allowed_mimes: set[str], file_label: str
) -> None:
    """Valida magic bytes do arquivo contra tipos MIME permitidos.

    Args:
        file_bytes: Conteúdo do arquivo.
        allowed_mimes: Conjunto de MIME types permitidos.
        file_label: Rótulo para mensagem de erro (ex: 'logo', 'fonte').

    Raises:
        HTTPException: Se o tipo não for detectável ou não corresponder.
    """
    kind = filetype.guess(file_bytes[:261])
    if kind is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não foi possível detectar o tipo do arquivo de {file_label}. "
            "Verifique se o arquivo não está corrompido.",
        )
    if kind.mime not in allowed_mimes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo de {file_label} não corresponde ao conteúdo. "
            f"Esperado: {', '.join(allowed_mimes)}. Detectado: {kind.mime}",
        )


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
    responses={
        404: {"model": ErrorResponse, "description": "Nenhum tema ativo encontrado"}
    },
)
def get_active_theme(
    current_user=Depends(get_current_user),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Retorna o tema ativo da empresa do usuário."""
    if not current_user.company_id:
        raise HTTPException(
            status_code=404, detail="Usuário não possui empresa vinculada"
        )

    theme = service.get_active_theme(current_user.company_id)
    if theme is None:
        raise HTTPException(
            status_code=404, detail="Nenhum tema ativo encontrado para esta empresa"
        )
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
    """Lista todos os temas da empresa. Retorna vazio se não houver empresa vinculada."""
    if not current_user.company_id:
        return []
    return service.list_themes(current_user.company_id)


@router.get(
    "/templates",
    response_model=list[dict],
    summary="Listar templates de skin",
    description="Lista todos os templates de skin disponíveis. Requer role admin.",
)
def list_skin_templates(
    _: None = Depends(require_role("admin")),
) -> list[dict]:
    """Lista todos os templates de skin disponíveis."""
    import json

    templates_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "skin-templates"
    )
    templates = []

    if os.path.exists(templates_dir):
        for filename in os.listdir(templates_dir):
            if filename.endswith(".json"):
                try:
                    with open(
                        os.path.join(templates_dir, filename), "r", encoding="utf-8"
                    ) as f:
                        template_data = json.load(f)

                    preview = {}
                    if "colors" in template_data:
                        colors = template_data["colors"]
                        for key in [
                            "--skin-primary",
                            "--skin-bg-main",
                            "--skin-text-main",
                            "--skin-danger",
                        ]:
                            if key in colors:
                                preview[key] = colors[key]

                    templates.append(
                        {
                            "slug": filename.replace(".json", ""),
                            "name": template_data.get(
                                "name", filename.replace(".json", "")
                            ),
                            "preview": preview,
                        }
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to load template", filename=filename, error=str(e)
                    )

    return templates


@router.post(
    "/from-template",
    response_model=ThemeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tema a partir de template",
    description="Cria um novo tema baseado em um template existente. Requer role admin.",
    responses={400: {"model": ErrorResponse, "description": "Template não encontrado"}},
)
def create_theme_from_template(
    dados: TemplateRequest,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Cria um novo tema a partir de um template."""
    company_id = _require_company_id(current_user)

    import json

    templates_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "skin-templates"
    )
    template_path = os.path.join(templates_dir, f"{dados.template_slug}.json")

    # Path traversal protection: ensure resolved path is within templates_dir
    if not os.path.realpath(template_path).startswith(os.path.realpath(templates_dir)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template slug contém caracteres inválidos",
        )

    if not os.path.exists(template_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template '{dados.template_slug}' não encontrado",
        )

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template_data = json.load(f)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao carregar template: {str(e)}",
        )

    colors = template_data.get("colors")
    fonts = template_data.get("fonts")
    icon_library = template_data.get("icon_library", "fontawesome")
    tokens = template_data.get("tokens")
    company_name = template_data.get("company_name")
    copyright_text = template_data.get("copyright_text")
    logo_url = template_data.get("logo_url")
    logo_short_url = template_data.get("logo_short_url")
    layout_mode = template_data.get("layout_mode", "topbar")

    return service.create_theme(
        company_id=company_id,
        name=dados.name,
        colors=colors,
        fonts=fonts,
        icon_library=icon_library,
        tokens=tokens,
        logo_url=logo_url,
        logo_short_url=logo_short_url,
        company_name=company_name,
        copyright_text=copyright_text,
        layout_mode=layout_mode,
    )


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
    if not current_user.company_id:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    theme = service.get_theme_by_id(theme_id)
    if theme is None or theme["company_id"] != current_user.company_id:
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


@router.get(
    "/{theme_id}/original-snapshot",
    summary="Snapshot original do tema",
    description="Retorna o snapshot do tema no momento da criação. Requer role admin.",
    responses={404: {"model": ErrorResponse, "description": "Snapshot original não encontrado"}},
)
def get_original_theme_snapshot(
    theme_id: int,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Retorna o snapshot original (primeira criação) do tema."""
    if not current_user.company_id:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    theme = service.get_theme_by_id(theme_id)
    if theme is None or theme["company_id"] != current_user.company_id:
        raise HTTPException(status_code=404, detail="Tema não encontrado")

    history = service.get_theme_history(theme_id, current_user.company_id)
    # History is ordered by criado_em DESC; find the "created" entry
    created = next((h for h in history if h.get("action") == "created"), None)
    if created and created.get("theme_snapshot"):
        return created["theme_snapshot"]
    raise HTTPException(status_code=404, detail="Snapshot original não encontrado")


@router.get(
    "/{theme_id}/history",
    response_model=list[ThemeHistoryResponse],
    summary="Histórico do tema",
    description="Retorna o histórico de alterações de um tema específico. Requer role admin.",
    responses={404: {"model": ErrorResponse, "description": "Tema não encontrado"}},
)
def get_theme_history(
    theme_id: int,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> list[dict]:
    """Retorna o histórico de alterações de um tema."""
    if not current_user.company_id:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    # Verify theme belongs to company
    theme = service.get_theme_by_id(theme_id)
    if theme is None or theme["company_id"] != current_user.company_id:
        raise HTTPException(status_code=404, detail="Tema não encontrado")

    # Get history from service
    return service.get_theme_history(theme_id, current_user.company_id)


@router.post(
    "/fonts/upload",
    response_model=ThemeFontResponse,
    summary="Upload de fonte",
    description="Faz upload de um arquivo de fonte. Retorna a URL pública.",
    responses={
        400: {"model": ErrorResponse, "description": "Arquivo inválido"},
        413: {"model": ErrorResponse, "description": "Arquivo muito grande"},
    },
)
async def upload_font(
    file: UploadFile = File(...),
    current_user=Depends(require_role("admin")),
) -> dict:
    """Faz upload de um arquivo de fonte e retorna a URL pública."""

    # Validate file extension
    allowed_exts = {".ttf", ".otf", ".woff", ".woff2"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não permitido. Extensões permitidas: {', '.join(allowed_exts)}",
        )

    # Read file content for magic bytes validation
    content = await file.read()

    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo muito grande. Tamanho máximo: {max_size // (1024 * 1024)}MB",
        )

    # Validate magic bytes
    _validate_file_magic(
        content,
        {"font/sfnt", "font/woff", "font/woff2", "application/octet-stream"},
        "fonte",
    )

    import uuid

    unique_filename = f"{uuid.uuid4()}{ext}"

    # Ensure fonts directory exists
    uploads_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"
    )
    fonts_dir = os.path.join(uploads_dir, "fonts")
    os.makedirs(fonts_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(fonts_dir, unique_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    font_url = f"/uploads/fonts/{unique_filename}"

    logger.info("Font uploaded", filename=unique_filename, size=len(content))
    return {"url": font_url}


@router.post(
    "/{theme_id}/logo",
    response_model=ThemeResponse,
    summary="Upload de logo",
    description="Faz upload de um logo para o tema. Requer role admin.",
    responses={
        400: {"model": ErrorResponse, "description": "Arquivo inválido"},
        404: {"model": ErrorResponse, "description": "Tema não encontrado"},
        413: {"model": ErrorResponse, "description": "Arquivo muito grande"},
    },
)
async def upload_logo(
    theme_id: int,
    file: UploadFile = File(...),
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Faz upload de um logo para o tema."""
    company_id = _require_company_id(current_user)

    # Validate file type (content_type check)
    allowed_types = ["image/jpeg", "image/png", "image/svg+xml", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não permitido. Tipos permitidos: {', '.join(allowed_types)}",
        )

    # Read file content for magic bytes validation
    content = await file.read()

    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo muito grande. Tamanho máximo: {max_size // (1024 * 1024)}MB",
        )

    # SVG não suportado por magic bytes — validação por content_type
    if file.content_type != "image/svg+xml":
        _validate_file_magic(
            content,
            {"image/jpeg", "image/png", "image/gif", "image/webp"},
            "logo",
        )

    # Verify theme belongs to company
    theme = service.get_theme_by_id(theme_id)
    if theme is None or theme["company_id"] != company_id:
        raise HTTPException(status_code=404, detail="Tema não encontrado")

    # Generate unique filename
    import uuid

    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    if file_extension.lower() not in ["jpg", "jpeg", "png", "svg", "gif"]:
        # Default extension based on content type
        ext_map = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/svg+xml": "svg",
            "image/gif": "gif",
        }
        file_extension = ext_map.get(file.content_type, "jpg")

    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    # Ensure uploads directory exists (mesmo diretorio usado em main.py para StaticFiles)
    uploads_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"
    )
    logos_dir = os.path.join(uploads_dir, "logos")
    os.makedirs(logos_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(logos_dir, unique_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # Construct URL
    logo_url = f"/uploads/logos/{unique_filename}"

    # Update theme with logo URL
    updated_theme = service.update_theme(
        theme_id=theme_id, company_id=company_id, logo_url=logo_url
    )

    logger.info(
        "Logo uploaded", theme_id=theme_id, filename=unique_filename, size=len(content)
    )
    return updated_theme
