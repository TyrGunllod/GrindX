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
        in_backend_fs = (backend_modules_dir / slug).exists()
        in_frontend_fs = (
            any(
                item.name.startswith(f"{slug}_") or item.name.startswith(f"{slug}-")
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
                ja_importado=in_backend_fs or in_frontend_fs,
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
            "--skip-migrations",
        ]
        if force:
            cmd.append("--force")

        logger.info("Executando subprocesso: %s", " ".join(cmd))

        stdout_lines: list[str] = []
        stderr_lines: list[str] = []
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=(
                    subprocess.CREATE_NEW_PROCESS_GROUP
                    if sys.platform == "win32"
                    else 0
                ),
            )
            try:
                stdout, stderr = proc.communicate(timeout=60)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                if stdout:
                    stdout_lines.append(stdout.strip())
                if stderr:
                    for line in stderr.strip().split("\n"):
                        line = line.strip()
                        if line:
                            logger.warning("[import:stderr] %s", line)
                            stderr_lines.append(line)
                logger.error(
                    "Subprocesso excedeu 60s ao importar '%s'. stdout: %s",
                    module_name,
                    "\n".join(stdout_lines) or "(vazio)",
                )
                return ImportResult(
                    success=False,
                    message="Falha na importação: subprocesso excedeu timeout de 60s",
                    steps=stdout_lines + stderr_lines,
                    error="Timeout do subprocesso.",
                )

            if stdout:
                for line in stdout.strip().split("\n"):
                    line = line.strip()
                    if line:
                        if line.startswith("[TIMING]"):
                            logger.info("[import] %s", line)
                        stdout_lines.append(line)

            if stderr:
                for line in stderr.strip().split("\n"):
                    line = line.strip()
                    if line:
                        logger.info("[import] %s", line)
                        stderr_lines.append(line)

        except FileNotFoundError:
            logger.error("Script não encontrado: %s", script_path)
            return ImportResult(
                success=False,
                message="Falha na importação: script não encontrado",
                steps=["Script não encontrado"],
                error=f"Script não encontrado: {script_path}",
            )

        stdout_data = "\n".join(stdout_lines)
        try:
            result_data = json.loads(stdout_data)
        except (json.JSONDecodeError, ValueError):
            result_data = {
                "success": False,
                "steps": [],
                "error": stderr or stdout_data,
            }

        if result_data.get("success"):
            zip_path.unlink(missing_ok=True)
            logger.info("Zip removido após importação: %s", zip_path.name)
            threading.Thread(
                target=_run_migrations_background,
                args=(module_name,),
                daemon=True,
            ).start()
            result_data["steps"].append("Migrações agendadas em segundo plano")
            logger.info("Import de '%s' concluído em <60s", module_name)

        return ImportResult(
            success=result_data.get("success", False),
            message=(
                "Módulo importado com sucesso. Migrações rodando em segundo plano."
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


@router.delete(
    "/{module_name}", response_model=ImportResult, summary="Remove um módulo importado"
)
def remove_module(
    module_name: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    steps = []

    api_dir = Path(__file__).resolve().parent.parent.parent

    main_py = api_dir / "app" / "main.py"
    if main_py.exists():
        content = main_py.read_text(encoding="utf-8")
        lines = content.split("\n")
        router_vars = set()
        for line in lines:
            if f"from app.modules.{module_name}" in line and "import router as" in line:
                parts = line.split("import router as")
                if len(parts) == 2:
                    router_vars.add(parts[1].strip())
        new_lines = []
        for line in lines:
            if f"from app.modules.{module_name}" in line:
                continue
            stripped = line.strip()
            if any(stripped == f"app.include_router({v})" for v in router_vars):
                continue
            new_lines.append(line)
        if len(new_lines) != len(lines):
            main_py.write_text("\n".join(new_lines), encoding="utf-8")
            steps.append("Router removido de main.py")

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
                before_marker = lines[:marker_idx]
                clean_lines = []
                skip_until_def = False
                for line in before_marker:
                    if f"from app.modules.{module_name}" in line:
                        continue
                    if line.strip().startswith("def get_") and module_name in line:
                        skip_until_def = True
                        continue
                    if skip_until_def:
                        if line.strip() == "" or line.strip().startswith("return"):
                            continue
                        skip_until_def = False
                    clean_lines.append(line)
                clean_lines.append(marker)
                clean_lines.extend(lines[marker_idx + 1 :])
                deps_py.write_text("\n".join(clean_lines), encoding="utf-8")
                steps.append("Dependency removida de dependencies.py")

    env_py = api_dir / "alembic" / "env.py"
    if env_py.exists():
        content = env_py.read_text(encoding="utf-8")
        lines = content.split("\n")
        new_lines = [
            line for line in lines if f"from app.modules.{module_name}" not in line
        ]
        if len(new_lines) != len(lines):
            env_py.write_text("\n".join(new_lines), encoding="utf-8")
            steps.append("Import removida de alembic/env.py")

    backend_dir = api_dir / "app" / "modules" / module_name
    if backend_dir.exists():
        shutil.rmtree(backend_dir)
        steps.append(f"Backend removido: {backend_dir}")

    frontend_dir = api_dir.parent / "frontend-webapp" / "modules"
    if frontend_dir.exists():
        for item in frontend_dir.iterdir():
            if (
                item.is_dir()
                and item.name.startswith(f"{module_name}_")
                or item.name.startswith(f"{module_name}-")
            ):
                shutil.rmtree(item)
                steps.append(f"Frontend removido: {item}")

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
