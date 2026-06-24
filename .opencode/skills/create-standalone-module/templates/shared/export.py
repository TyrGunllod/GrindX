"""
export.py — Exporta o módulo {entity_name} para o sistema GrindX.

Uso:
    python -m app.modules.{module_name}.export [--dry-run] [--grindx-root PATH]

Sem --dry-run, copia arquivos e registra.
Com --dry-run, apenas exibe o que seria feito.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

MODULE_NAME = "{entity_name}"
MODULE_SRC = Path(__file__).parent
STANDALONE_ROOT = MODULE_SRC.parent.parent.parent  # raiz do modulo-{module_name}/
GRINDX_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent / "GrindX"
# postgres: "api-postgres" | sqlserver: "api-sqlserver"
GRINDX_API = GRINDX_ROOT / "apps" / "api-postgres"
GRINDX_FRONTEND = GRINDX_ROOT / "packages" / "frontend-webapp"
FRONTEND_SRC = STANDALONE_ROOT / "frontend"
MIGRATION_SRC = STANDALONE_ROOT / "migration"

ROUTER_IMPORT = "from app.modules.{module_name}.routers.{module_name}_router import router as {module_name}_router"
ROUTER_REGISTER = "app.include_router({module_name}_router)"


def copy_backend(dry_run: bool = False):
    dest = GRINDX_API / "app" / "modules" / "{module_name}"
    if dry_run:
        logger.info("[DRY-RUN] Copiaria %s -> %s", MODULE_SRC, dest)
    else:
        if dest.exists(): shutil.rmtree(dest)
        shutil.copytree(MODULE_SRC, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        logger.info("Backend copiado")


def copy_frontend(dry_run: bool = False):
    dest_base = GRINDX_FRONTEND / "modules"
    if dry_run:
        logger.info("[DRY-RUN] Copiaria sub-modulos de %s -> %s", FRONTEND_SRC, dest_base)
    else:
        for sub in FRONTEND_SRC.iterdir():
            if sub.is_dir():
                dest = dest_base / sub.name
                if dest.exists(): shutil.rmtree(dest)
                shutil.copytree(sub, dest)
                logger.info("Frontend copiado: %s -> %s", sub.name, dest)
            elif sub.is_file():
                dest = dest_base / sub.name
                shutil.copy2(sub, dest)
                logger.info("Arquivo copiado: %s", sub.name)


def copy_migration(dry_run: bool = False):
    dest = GRINDX_API / "alembic" / "versions"
    if dry_run:
        logger.info("[DRY-RUN] Copiaria migrations de %s -> %s", MIGRATION_SRC, dest)
    else:
        for f in MIGRATION_SRC.glob("*.py"):
            shutil.copy2(f, dest / f.name)
            logger.info("Migration %s copiada", f.name)


def register_routes(dry_run: bool = False):
    main_py = GRINDX_API / "app" / "main.py"
    content = main_py.read_text(encoding="utf-8")
    if ROUTER_IMPORT in content:
        logger.info("Rotas já registradas")
        return
    lines = content.splitlines(keepends=True)
    last_import = last_include = None
    for i, line in enumerate(lines):
        if "from app." in line and "import router as" in line: last_import = i
        if "app.include_router(" in line: last_include = i
    if last_import is not None:
        lines.insert(last_import + 1, ROUTER_IMPORT + "\n")
        if last_include is not None and last_include >= last_import: last_include += 1
    if last_include is not None:
        lines.insert(last_include + 1, ROUTER_REGISTER + "\n")
    if dry_run:
        logger.info("[DRY-RUN] main.py alterado")
    else:
        main_py.write_text("".join(lines), encoding="utf-8")
        logger.info("Rotas registradas")


def register_dependency(dry_run: bool = False):
    deps_py = GRINDX_API / "app" / "auth" / "dependencies.py"
    content = deps_py.read_text(encoding="utf-8")
    marker = "# --- Versões vinculadas das permissões ---"
    factory = (
        "from app.modules.{module_name}.repositories.{module_name}_repository import {entity_name}Repository\n"
        "from app.modules.{module_name}.services.{module_name}_service import {entity_name}Service\n\n\n"
        "def get_{module_name}_service(db: Session = Depends(get_db)) -> {entity_name}Service:\n"
        '    """Factory para o {entity_name}Service."""\n'
        "    repository = {entity_name}Repository(db)\n"
        "    return {entity_name}Service(repository)\n\n\n"
        f"{marker}\n"
    )
    if "get_{module_name}_service" in content:
        logger.info("Dependency já registrada")
        return
    if dry_run:
        logger.info("[DRY-RUN] auth/dependencies.py alterado")
    else:
        deps_py.write_text(content.replace(marker, factory), encoding="utf-8")
        logger.info("Dependency registrada")


def register_alembic_import(dry_run: bool = False):
    env_py = GRINDX_API / "alembic" / "env.py"
    content = env_py.read_text(encoding="utf-8")
    line = "from app.modules.{module_name}.models.{module_name} import {entity_name}  # noqa: F401"
    if line in content:
        logger.info("Import já registrado")
        return
    marker = "from app.modules.portal.models.portal import Aba, Modulo  # noqa: F401"
    if dry_run:
        logger.info("[DRY-RUN] alembic/env.py alterado")
    else:
        env_py.write_text(content.replace(marker, marker + "\n" + line), encoding="utf-8")
        logger.info("Import registrado")


def run_migrations(dry_run: bool = False):
    cmd = [sys.executable, "-m", "alembic", "upgrade", "head"]
    if dry_run:
        logger.info("[DRY-RUN] Comando: %s", " ".join(cmd))
    else:
        result = subprocess.run(cmd, cwd=GRINDX_API, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error("Migration falhou", stderr=result.stderr)
            raise RuntimeError(f"Migration error: {result.stderr}")
        logger.info("Migrations executadas")


def package(dry_run: bool = False):
    """Empacota o módulo em um .zip com module.json para distribuição.

    IMPORTANTE: O frontend no zip deve ser `frontend/custos/...`, NÃO `frontend/modules/custos/`.
    O GrindX importer coloca os arquivos de frontend em `modules/`, então se o zip
    tiver `frontend/modules/custos/`, o resultado será `modules/frontend/modules/custos/` (caminho errado).
    """
    module_dir = MODULE_SRC
    frontend_dir = FRONTEND_SRC
    migration_dir = MIGRATION_SRC
    dist_dir = STANDALONE_ROOT / "dist"
    zip_path = dist_dir / f"modulo-{MODULE_NAME.lower()}.zip"

    if dry_run:
        logger.info("[DRY-RUN] Criaria %s com:", zip_path)
        logger.info("  - module.json")
        logger.info("  - app/modules/%s/", MODULE_NAME)
        logger.info("  - frontend/")
        logger.info("  - migration/")
        return

    dist_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        manifest_path = STANDALONE_ROOT / "module.json"
        if manifest_path.exists():
            zf.write(manifest_path, "module.json")

        # Backend: mantém app/modules/{module_name}/ no zip
        for file in module_dir.rglob("*"):
            if file.is_file() and "__pycache__" not in file.parts and not file.name.endswith(".pyc"):
                arcname = str(file.relative_to(STANDALONE_ROOT))
                zf.write(file, arcname)

        if frontend_dir.exists():
            for file in frontend_dir.rglob("*"):
                if file.is_file():
                    # Remove prefixo 'modules/' para evitar path duplicado no importer
                    # frontend/modules/gp_dashboard/ → frontend/gp_dashboard/
                    rel = file.relative_to(frontend_dir)
                    parts = list(rel.parts)
                    if parts and parts[0] == "modules":
                        parts = parts[1:]
                    arcname = str(Path("frontend") / Path(*parts))
                    zf.write(file, arcname)

        # Incluir migration/ se existir (postgres apenas)
        if migration_dir.exists():
            for file in migration_dir.glob("*.py"):
                zf.write(file, f"migration/{file.name}")

    logger.info("Pacote criado: %s", zip_path)


def export(dry_run: bool = False):
    """Exporta módulo para o GrindX.

    Se GRINDX_API aponta para api-sqlserver (módulos read-only de ERP),
    pula migration, dependency factory e alembic import.
    """
    logger.info("Exportando módulo %s", MODULE_NAME, dry_run=dry_run)
    copy_backend(dry_run)
    copy_frontend(dry_run)
    is_sqlserver = "sqlserver" in str(GRINDX_API).lower()
    if not is_sqlserver:
        copy_migration(dry_run)
    register_routes(dry_run)
    if not is_sqlserver:
        register_dependency(dry_run)
        register_alembic_import(dry_run)
        run_migrations(dry_run)
    logger.info("Módulo exportado com sucesso")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Ferramentas do módulo {MODULE_NAME}")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # export
    export_parser = subparsers.add_parser("export", help="Exporta para o GrindX")
    export_parser.add_argument("--dry-run", action="store_true", help="Apenas simula")
    export_parser.add_argument("--grindx-root", default=None, help="Raiz do GrindX")

    # package
    pkg_parser = subparsers.add_parser("package", help="Empacota como .zip")
    pkg_parser.add_argument("--dry-run", action="store_true", help="Apenas simula")

    args = parser.parse_args()

    if args.command == "package":
        package(dry_run=args.dry_run)
    elif args.command == "export":
        if getattr(args, "grindx_root", None):
            global GRINDX_ROOT, GRINDX_API, GRINDX_FRONTEND
            GRINDX_ROOT = Path(args.grindx_root)
            GRINDX_API = GRINDX_ROOT / "apps" / "api-postgres"
            GRINDX_FRONTEND = GRINDX_ROOT / "packages" / "frontend-webapp"
        export(dry_run=args.dry_run)
