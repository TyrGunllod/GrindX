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

from app.auth.dependencies import get_current_user, require_role
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
    modules = []
    skipped = 0

    for zip_path in sorted(import_dir.glob("*.zip")):
        manifest = _read_manifest_from_zip(zip_path)
        if not manifest:
            skipped += 1
            continue

        slug = manifest.get("module_name", zip_path.stem)
        modules.append(
            ModuleInfo(
                slug=slug,
                module_name=manifest.get("module_name", slug),
                entity_name=manifest.get("entity_name", ""),
                version=manifest.get("version", "0.0.0"),
                menu_label=manifest.get("menu_label", slug),
                schema_name=manifest.get("schema_name", "org"),
                ja_importado=slug in existing_slugs,
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
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Arquivo .zip não encontrado para o módulo: {module_name}")
        if len(matches) > 1:
            logger.warning("Múltiplos zips correspondentes a '%s': %s. Usando %s", module_name, [m.name for m in matches], matches[0].name)
        logger.info("Fuzzy match para '%s' selecionou: %s", module_name, matches[0].name)
        zip_path = matches[0]

    tmp_dir = None
    try:
        tmp_dir = Path(tempfile.mkdtemp(prefix=f"grindx_import_{module_name}_"))
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_dir)

        logger.info("Zip extraído para %s", tmp_dir)

        manifest_path = tmp_dir / "module.json"
        if not manifest_path.exists():
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, f"module.json não encontrado dentro do .zip: {zip_path.name}")

        script_path = Path(__file__).resolve().parent.parent.parent / "scripts" / "import_module.py"
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
            result_data = {"success": False, "steps": [], "error": result.stderr or result.stdout}

        if result.stderr:
            for line in result.stderr.strip().split("\n"):
                if line:
                    logger.warning("[import subprocess] %s", line)

        return ImportResult(
            success=result_data.get("success", False),
            message="Módulo importado com sucesso" if result_data.get("success") else "Falha na importação",
            steps=result_data.get("steps", []),
            error=result_data.get("error"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro ao importar módulo")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Erro interno: {str(e)}")
    finally:
        if tmp_dir is not None and tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)
