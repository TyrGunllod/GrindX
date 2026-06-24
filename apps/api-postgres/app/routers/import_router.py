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
import threading
import zipfile
from pathlib import Path

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.core.config import settings
from app.database import get_db

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/import", tags=["Importação de Módulos"])


def _run_migrations_background(module_name: str) -> None:
    """Roda alembic upgrade head em background."""
    api_dir = Path(__file__).resolve().parent.parent.parent
    python_exe = sys.executable
    cmd = [python_exe, "-m", "alembic", "upgrade", "head"]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(api_dir),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            logger.info("Migrações de '%s' concluídas com sucesso", module_name)
        else:
            logger.warning(
                "Migrações de '%s' falharam: %s",
                module_name,
                result.stderr.strip() or result.stdout.strip(),
            )
    except subprocess.TimeoutExpired:
        logger.error(
            "Migrações de '%s' excederam timeout de 120s. "
            "Execute manualmente: make migrate",
            module_name,
        )


class ModuleInfo(BaseModel):
    slug: str
    module_name: str
    entity_name: str
    version: str
    menu_label: str
    schema_name: str
    target_api: str = "postgres"
    ja_importado: bool
    pode_remover: bool = False


class ScanResponse(BaseModel):
    modules: list[ModuleInfo]
    instalados: list[ModuleInfo]


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
        return ScanResponse(modules=[], instalados=[])

    api_dir = Path(__file__).resolve().parent.parent.parent
    postgres_backend = api_dir / "app" / "modules"
    sqlserver_backend = api_dir.parent / "api-sqlserver" / "app" / "modules"
    frontend_modules_dir = api_dir.parent / "frontend-webapp" / "modules"

    modules = []
    instalados = []
    skipped = 0
    seen_slugs: set[str] = set()

    # 1. Escaneia zips disponiveis
    for zip_path in sorted(import_dir.glob("*.zip")):
        manifest = _read_manifest_from_zip(zip_path)
        if not manifest:
            skipped += 1
            continue

        slug = manifest.get("module_name", zip_path.stem)
        seen_slugs.add(slug)
        in_backend_fs = (postgres_backend / slug).exists() or (
            sqlserver_backend / slug
        ).exists()
        in_frontend_fs = (
            any(
                item.name.startswith(slug)
                or (
                    item.name.startswith(f"{slug}_") or item.name.startswith(f"{slug}-")
                )
                for item in frontend_modules_dir.iterdir()
                if item.is_dir()
            )
            if frontend_modules_dir.exists()
            else False
        )

        modules.append(
            ModuleInfo(
                slug=slug,
                module_name=manifest.get("module_name", slug),
                entity_name=manifest.get("entity_name", ""),
                version=manifest.get("version", "0.0.0"),
                menu_label=manifest.get("menu_label", slug),
                schema_name=manifest.get("schema_name", "org"),
                target_api=manifest.get("target_api", "postgres"),
                ja_importado=in_backend_fs or in_frontend_fs,
                pode_remover=True,
            )
        )

    # 2. Mapeia frontend_dirs -> slug (do module.json dos backends)
    frontend_map: dict[str, str] = {}  # frontend_dir_name -> slug
    for base in [postgres_backend, sqlserver_backend]:
        if not base.exists():
            continue
        for mod_dir in sorted(base.iterdir()):
            if not mod_dir.is_dir() or mod_dir.name.startswith("_"):
                continue
            mf = mod_dir / "module.json"
            if not mf.exists():
                continue
            try:
                m = json.loads(mf.read_text(encoding="utf-8"))
            except Exception:
                continue
            slug = m.get("module_name", mod_dir.name)
            for tab in m.get("frontend_tabs", []):
                url = tab.get("url", "")
                parts = url.split("/")
                if len(parts) >= 2:
                    frontend_map[parts[1]] = slug
            if not m.get("frontend_tabs"):
                frontend_map[mod_dir.name] = slug

    # 3. Escaneia modulos instalados (frontend directories + backends sem frontend previsto)
    seen_frontend: set[str] = set()
    if frontend_modules_dir.exists():
        for fe_dir in sorted(frontend_modules_dir.iterdir()):
            if not fe_dir.is_dir() or fe_dir.name.startswith("_"):
                continue
            fn = fe_dir.name
            if fn in seen_frontend:
                continue
            seen_frontend.add(fn)
            slug = frontend_map.get(fn, fn)
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)

            tem_backend = (postgres_backend / slug).exists() or (sqlserver_backend / slug).exists()

            manifest = {}
            for base in [postgres_backend, sqlserver_backend]:
                mp = base / slug / "module.json"
                if mp.exists():
                    try:
                        manifest = json.loads(mp.read_text(encoding="utf-8"))
                    except Exception:
                        pass
                    break

            instalados.append(
                ModuleInfo(
                    slug=slug,
                    module_name=manifest.get("module_name", slug) if manifest else slug,
                    entity_name=manifest.get("entity_name", ""),
                    version=manifest.get("version", "0.0.0"),
                    menu_label=manifest.get("menu_label", slug) if manifest else slug,
                    schema_name=manifest.get("schema_name", "org"),
                    target_api=manifest.get("target_api", "postgres"),
                    ja_importado=True,
                    pode_remover=tem_backend,
                )
            )

    # 4. Backends sem frontend correspondente
    MODULOS_SISTEMA = {"iam", "org", "portal"}
    for base in [postgres_backend, sqlserver_backend]:
        if not base.exists():
            continue
        for mod_dir in sorted(base.iterdir()):
            if not mod_dir.is_dir() or mod_dir.name.startswith("_"):
                continue
            slug = mod_dir.name
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            mf = mod_dir / "module.json"
            manifest = {}
            if mf.exists():
                try:
                    manifest = json.loads(mf.read_text(encoding="utf-8"))
                except Exception:
                    pass
            instalados.append(
                ModuleInfo(
                    slug=slug,
                    module_name=manifest.get("module_name", slug),
                    entity_name=manifest.get("entity_name", ""),
                    version=manifest.get("version", "0.0.0"),
                    menu_label=manifest.get("menu_label", slug),
                    schema_name=manifest.get("schema_name", "org"),
                    target_api=manifest.get("target_api", "postgres"),
                    ja_importado=True,
                    pode_remover=slug not in MODULOS_SISTEMA,
                )
            )

    if skipped:
        logger.warning("%d zip(s) skipped — manifest inválido ou ausente", skipped)

    return ScanResponse(modules=modules, instalados=instalados)


@router.post("/{module_name}", response_model=ImportResult, summary="Importa um módulo")
def import_module(
    module_name: str,
    force: bool = Query(True, description="Sobrescrever módulo existente"),
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
    out_path = None
    err_path = None
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

        with open(manifest_path, encoding="utf-8") as f:
            manifest_data = json.load(f)
        target_api = manifest_data.get("target_api", "postgres")

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
            "--skip-migrations",
            "--skip-install",
        ]
        if target_api == "sqlserver":
            cmd.append("--target-api=sqlserver")
        if force:
            cmd.append("--force")

        logger.info("Executando import in-process: %s", module_name)

        from scripts.import_module import import_module as run_import

        steps: list[str] = []
        try:
            result_data = run_import(
                module_name,
                tmp_dir,
                force=force,
                skip_migrations=True,
                skip_install=True,
                target_api=target_api,
            )
        except Exception as exc:
            logger.exception("Import falhou")
            result_data = {"success": False, "steps": steps, "error": str(exc)}

        if result_data.get("success"):
            zip_path.unlink(missing_ok=True)
            logger.info("Zip removido após importação: %s", zip_path.name)
            steps = result_data.get("steps", [])
            if target_api != "sqlserver":
                threading.Thread(
                    target=_run_migrations_background,
                    args=(module_name,),
                    daemon=True,
                ).start()
                steps.append("Migrações agendadas em segundo plano")
            else:
                steps.append("Módulo sqlserver importado — sem migrações")
            logger.info("Import de '%s' concluído", module_name)

        return ImportResult(
            success=result_data.get("success", False),
            message=(
                "Módulo importado com sucesso."
                if result_data.get("success")
                else "Falha na importação"
            ),
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
        if out_path is not None and out_path.exists():
            out_path.unlink(missing_ok=True)
        if err_path is not None and err_path.exists():
            err_path.unlink(missing_ok=True)


@router.delete(
    "/{module_name}", response_model=ImportResult, summary="Remove um módulo importado"
)
def remove_module(
    module_name: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    from scripts.import_module import remove_module as run_remove

    result = run_remove(module_name)

    # Remove vinculo com aba no banco
    try:
        from app.models.portal import Modulo
        mod = db.query(Modulo).filter(Modulo.slug == module_name).first()
        if mod:
            from app.models.usuario import UsuarioModulo
            db.query(UsuarioModulo).filter(UsuarioModulo.modulo_id == mod.id).delete()
            db.delete(mod)
            db.commit()
            if "steps" not in result:
                result["steps"] = []
            result["steps"].append("Vínculo com aba removido do banco")
    except Exception as e:
        logger.warning("Erro ao remover vinculo do modulo '%s': %s", module_name, e)

    if not result.get("success"):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Erro ao remover módulo '{module_name}': {result.get('error', 'desconhecido')}",
        )

    steps = result.get("steps", [])
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
