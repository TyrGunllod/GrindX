"""
import_router.py — Endpoints para importação de módulos via UI.

Permite escanear a pasta import/ por .zips com module.json e
importar módulos completos (backend + frontend + migration + registro).
"""

import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.core.config import settings
from app.database import get_db
from app.models.portal import Modulo

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/import", tags=["Importação de Módulos"])


class ModuleInfo(BaseModel):
    slug: str
    module_name: str
    entity_name: str
    version: str
    menu_label: str
    schema_name: str
    ja_importado: bool


class ScanResponse(BaseModel):
    modules: list[ModuleInfo]


class ImportResult(BaseModel):
    success: bool
    message: str
    steps: list[str]
    error: str | None = None


def _get_import_dir() -> Path:
    return Path(settings.import_dir_path)


def _read_manifest_from_zip(zip_path: Path) -> dict | None:
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            if "module.json" in zf.namelist():
                with zf.open("module.json") as f:
                    return json.load(f)
    except Exception as e:
        logger.warning("Erro ao ler %s: %s", zip_path, e)
    return None


@router.get("/scan", response_model=ScanResponse, summary="Escaneia zips disponíveis")
def scan_imports(
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    import_dir = _get_import_dir()
    if not import_dir.exists():
        return ScanResponse(modules=[])

    existing_slugs = {m.slug for m in db.query(Modulo).all()}
    
    api_dir = Path(__file__).resolve().parent.parent.parent
    backend_modules_dir = api_dir / "app" / "modules"
    frontend_modules_dir = api_dir.parent / "frontend-webapp" / "modules"
    
    modules = []
    skipped = 0

    for zip_path in sorted(import_dir.glob("*.zip")):
        manifest = _read_manifest_from_zip(zip_path)
        if not manifest:
            skipped += 1
            continue

        slug = manifest.get("module_name", zip_path.stem)
        in_db = slug in existing_slugs
        in_backend_fs = (backend_modules_dir / slug).exists()
        in_frontend_fs = (frontend_modules_dir / slug).exists()
        
        modules.append(
            ModuleInfo(
                slug=slug,
                module_name=manifest.get("module_name", slug),
                entity_name=manifest.get("entity_name", ""),
                version=manifest.get("version", "0.0.0"),
                menu_label=manifest.get("menu_label", slug),
                schema_name=manifest.get("schema_name", "org"),
                ja_importado=in_db or in_backend_fs or in_frontend_fs,
            )
        )

    if skipped:
        logger.warning("%d zip(s) skipped — manifest inválido ou ausente", skipped)

    return ScanResponse(modules=modules)


@router.post("/{module_name}", response_model=ImportResult, summary="Importa um módulo")
def import_module(
    module_name: str,
    force: bool = Query(False, description="Sobrescrever módulo existente"),
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    import_dir = _get_import_dir()

    zip_path = import_dir / f"{module_name}.zip"
    if not zip_path.exists():
        matches = list(import_dir.glob(f"*{module_name}*.zip"))
        if not matches:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Arquivo .zip não encontrado para o módulo: {module_name}",
            )
        if len(matches) > 1:
            logger.warning(
                "Múltiplos zips correspondentes a '%s': %s. Usando %s",
                module_name,
                [m.name for m in matches],
                matches[0].name,
            )
        logger.info(
            "Fuzzy match para '%s' selecionou: %s", module_name, matches[0].name
        )
        zip_path = matches[0]

    tmp_dir = None
    try:
        tmp_dir = Path(tempfile.mkdtemp(prefix=f"grindx_import_{module_name}_"))
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_dir)

        logger.info("Zip extraído para %s", tmp_dir)

        manifest_path = tmp_dir / "module.json"
        if not manifest_path.exists():
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                f"module.json não encontrado dentro do .zip: {zip_path.name}",
            )

        script_path = (
            Path(__file__).resolve().parent.parent.parent
            / "scripts"
            / "import_module.py"
        )
        cmd = [
            sys.executable,
            str(script_path),
            module_name,
            f"--import-dir={tmp_dir}",
        ]
        if force:
            cmd.append("--force")

        logger.info("Executando subprocesso: %s", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        try:
            result_data = json.loads(result.stdout.strip())
        except (json.JSONDecodeError, ValueError):
            result_data = {
                "success": False,
                "steps": [],
                "error": result.stderr or result.stdout,
            }

        if result.stderr:
            for line in result.stderr.strip().split("\n"):
                if line:
                    logger.warning("[import subprocess] %s", line)

        return ImportResult(
            success=result_data.get("success", False),
            message="Módulo importado com sucesso"
            if result_data.get("success")
            else "Falha na importação",
            steps=result_data.get("steps", []),
            error=result_data.get("error"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro ao importar módulo")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, f"Erro interno: {str(e)}"
        )
    finally:
        if tmp_dir is not None and tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)


@router.delete("/{module_name}", response_model=ImportResult, summary="Remove um módulo importado")
def remove_module(
    module_name: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    steps = []
    
    api_dir = Path(__file__).resolve().parent.parent.parent
    backend_dir = api_dir / "app" / "modules" / module_name
    frontend_dir = api_dir.parent / "frontend-webapp" / "modules" / module_name
    
    if backend_dir.exists():
        shutil.rmtree(backend_dir)
        steps.append(f"Backend removido: {backend_dir}")
        logger.info("Backend removido: %s", backend_dir)
    
    if frontend_dir.exists():
        shutil.rmtree(frontend_dir)
        steps.append(f"Frontend removido: {frontend_dir}")
        logger.info("Frontend removido: %s", frontend_dir)
    
    deps_py = api_dir / "app" / "auth" / "dependencies.py"
    if deps_py.exists():
        content = deps_py.read_text(encoding="utf-8")
        marker = "# --- Versões vinculadas das permissões ---"
        if marker in content:
            lines = content.split("\n")
            marker_idx = None
            for i, line in enumerate(lines):
                if marker in line:
                    marker_idx = i
                    break
            if marker_idx is not None:
                new_lines = lines[:marker_idx]
                new_lines.append(marker)
                new_lines.extend(lines[marker_idx + 1:])
                deps_py.write_text("\n".join(new_lines), encoding="utf-8")
                steps.append("Dependency removida de dependencies.py")
                logger.info("Dependency removida: %s", module_name)
    
    env_py = api_dir / "alembic" / "env.py"
    if env_py.exists():
        content = env_py.read_text(encoding="utf-8")
        import_line = f"from app.modules.{module_name}.models.{module_name} import"
        if import_line in content:
            lines = content.split("\n")
            new_lines = [line for line in lines if import_line not in line]
            env_py.write_text("\n".join(new_lines), encoding="utf-8")
            steps.append("Import removida de alembic/env.py")
            logger.info("Import removida de env.py: %s", module_name)
    
    modulo = db.query(Modulo).filter(Modulo.slug == module_name).first()
    if modulo:
        db.delete(modulo)
        db.commit()
        steps.append(f"Registro removido do banco (id={modulo.id})")
        logger.info("Registro removido: slug=%s, id=%d", module_name, modulo.id)
    
    if not steps:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Módulo '{module_name}' não encontrado para remoção",
        )
    
    return ImportResult(
        success=True,
        message=f"Módulo '{module_name}' removido com sucesso",
        steps=steps,
    )
