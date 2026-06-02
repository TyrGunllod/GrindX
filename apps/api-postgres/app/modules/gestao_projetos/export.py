"""
export.py — Exporta o módulo GestaoProjetos para o sistema GrindX.

Uso:
    python -m app.modules.gestao_projetos.export [--dry-run] [--grindx-root PATH]
"""

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

MODULE_NAME = "gestao_projetos"
MODULE_SRC = Path(__file__).parent
STANDALONE_ROOT = MODULE_SRC.parent.parent.parent
GRINDX_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent / "GrindX"
GRINDX_API = GRINDX_ROOT / "packages" / "api-postgres"
GRINDX_FRONTEND = GRINDX_ROOT / "packages" / "frontend-webapp"
FRONTEND_SRC = STANDALONE_ROOT / "frontend"
MIGRATION_SRC = STANDALONE_ROOT / "migration"

ROUTERS_IMPORT = """from app.modules.gestao_projetos.routers.projeto_router import router as projeto_router
from app.modules.gestao_projetos.routers.tarefa_router import router as tarefa_router
from app.modules.gestao_projetos.routers.recurso_router import router as recurso_router
from app.modules.gestao_projetos.routers.dashboard_router import router as dashboard_router
from app.modules.gestao_projetos.routers.cronograma_router import router as cronograma_router"""

ROUTERS_REGISTER = """app.include_router(projeto_router)
app.include_router(tarefa_router)
app.include_router(recurso_router)
app.include_router(dashboard_router)
app.include_router(cronograma_router)"""


def copy_backend(dry_run: bool = False):
    dest = GRINDX_API / "app" / "modules" / "gestao_projetos"
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
    if "gestao_projetos" in content:
        logger.info("Rotas já registradas")
        return
    lines = content.splitlines(keepends=True)
    last_import = last_include = None
    for i, line in enumerate(lines):
        if "from app." in line and "import router as" in line: last_import = i
        if "app.include_router(" in line: last_include = i
    if last_import is not None:
        lines.insert(last_import + 1, ROUTERS_IMPORT + "\n")
        if last_include is not None and last_include >= last_import: last_include += 1
    if last_include is not None:
        lines.insert(last_include + 1, ROUTERS_REGISTER + "\n")
    if dry_run:
        logger.info("[DRY-RUN] main.py alterado")
    else:
        main_py.write_text("".join(lines), encoding="utf-8")
        logger.info("Rotas registradas")


def register_dependencies(dry_run: bool = False):
    deps_py = GRINDX_API / "app" / "auth" / "dependencies.py"
    content = deps_py.read_text(encoding="utf-8")
    marker = "# --- Versões vinculadas das permissões ---"
    factory = """from app.modules.gestao_projetos.repositories.projeto_repository import ProjetoRepository
from app.modules.gestao_projetos.services.projeto_service import ProjetoService
from app.modules.gestao_projetos.repositories.tarefa_repository import TarefaRepository
from app.modules.gestao_projetos.services.tarefa_service import TarefaService
from app.modules.gestao_projetos.repositories.registro_repository import RegistroRepository
from app.modules.gestao_projetos.services.registro_service import RegistroService
from app.modules.gestao_projetos.repositories.recurso_repository import RecursoRepository
from app.modules.gestao_projetos.services.recurso_service import RecursoService
from app.modules.gestao_projetos.repositories.dashboard_repository import DashboardRepository
from app.modules.gestao_projetos.services.dashboard_service import DashboardService
from app.modules.gestao_projetos.repositories.cronograma_repository import CronogramaRepository
from app.modules.gestao_projetos.services.cronograma_service import CronogramaService


def get_gestao_projetos_service(db: Session = Depends(get_db)) -> ProjetoService:
    repository = ProjetoRepository(db)
    return ProjetoService(repository)


def get_gestao_projetos_tarefa_service(db: Session = Depends(get_db)) -> TarefaService:
    repository = TarefaRepository(db)
    return TarefaService(repository)


def get_gestao_projetos_registro_service(db: Session = Depends(get_db)) -> RegistroService:
    repository = RegistroRepository(db)
    return RegistroService(repository)


def get_gestao_projetos_recurso_service(db: Session = Depends(get_db)) -> RecursoService:
    repository = RecursoRepository(db)
    return RecursoService(repository)


def get_gestao_projetos_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    repository = DashboardRepository(db)
    return DashboardService(repository)


def get_gestao_projetos_cronograma_service(db: Session = Depends(get_db)) -> CronogramaService:
    repository = CronogramaRepository(db)
    return CronogramaService(repository)


""" + marker
    if "get_gestao_projetos_service" in content:
        logger.info("Dependencies já registradas")
        return
    if dry_run:
        logger.info("[DRY-RUN] auth/dependencies.py alterado")
    else:
        deps_py.write_text(content.replace(marker, factory), encoding="utf-8")
        logger.info("Dependencies registradas")


def register_alembic_import(dry_run: bool = False):
    env_py = GRINDX_API / "alembic" / "env.py"
    content = env_py.read_text(encoding="utf-8")
    imports = """from app.modules.gestao_projetos.models.projeto import Projeto  # noqa: F401
from app.modules.gestao_projetos.models.tarefa import Tarefa  # noqa: F401
from app.modules.gestao_projetos.models.registro_tarefa import RegistroTarefa  # noqa: F401
from app.modules.gestao_projetos.models.recurso import Recurso  # noqa: F401"""
    if "gestao_projetos" in content:
        logger.info("Import já registrado")
        return
    marker = "from app.modules.portal.models.portal import Aba, Modulo  # noqa: F401"
    if dry_run:
        logger.info("[DRY-RUN] alembic/env.py alterado")
    else:
        env_py.write_text(content.replace(marker, marker + "\n" + imports), encoding="utf-8")
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
    module_dir = MODULE_SRC
    frontend_dir = FRONTEND_SRC
    migration_dir = MIGRATION_SRC
    dist_dir = STANDALONE_ROOT / "dist"
    zip_path = dist_dir / f"modulo-{MODULE_NAME.lower()}.zip"

    if dry_run:
        logger.info("[DRY-RUN] Criaria %s com:", zip_path)
        logger.info("  - module.json")
        logger.info("  - app/modules/gestao_projetos/")
        logger.info("  - frontend/")
        logger.info("  - migration/")
        return

    dist_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        manifest_path = STANDALONE_ROOT / "module.json"
        if manifest_path.exists():
            zf.write(manifest_path, "module.json")

        for file in MODULE_SRC.rglob("*"):
            if file.is_file() and "__pycache__" not in file.parts and not file.name.endswith(".pyc"):
                arcname = str(file.relative_to(STANDALONE_ROOT))
                zf.write(file, arcname)

        if frontend_dir.exists():
            for file in frontend_dir.rglob("*"):
                if file.is_file():
                    arcname = str(Path("frontend") / file.relative_to(frontend_dir))
                    zf.write(file, arcname)

        if migration_dir.exists():
            for file in migration_dir.glob("*.py"):
                zf.write(file, f"migration/{file.name}")

    logger.info("Pacote criado: %s", zip_path)


def export(dry_run: bool = False):
    logger.info("Exportando módulo %s", MODULE_NAME, dry_run=dry_run)
    copy_backend(dry_run)
    copy_frontend(dry_run)
    copy_migration(dry_run)
    register_routes(dry_run)
    register_dependencies(dry_run)
    register_alembic_import(dry_run)
    run_migrations(dry_run)
    logger.info("Módulo exportado com sucesso")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Ferramentas do módulo {MODULE_NAME}")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    export_parser = subparsers.add_parser("export", help="Exporta para o GrindX")
    export_parser.add_argument("--dry-run", action="store_true", help="Apenas simula")
    export_parser.add_argument("--grindx-root", default=None, help="Raiz do GrindX")

    pkg_parser = subparsers.add_parser("package", help="Empacota como .zip")
    pkg_parser.add_argument("--dry-run", action="store_true", help="Apenas simula")

    args = parser.parse_args()

    if args.command == "package":
        package(dry_run=args.dry_run)
    elif args.command == "export":
        if getattr(args, "grindx_root", None):
            _update_paths(args.grindx_root)
        export(dry_run=args.dry_run)


def _update_paths(grindx_root: str):
    global GRINDX_ROOT, GRINDX_API, GRINDX_FRONTEND
    GRINDX_ROOT = Path(grindx_root)
    GRINDX_API = GRINDX_ROOT / "packages" / "api-postgres"
    GRINDX_FRONTEND = GRINDX_ROOT / "packages" / "frontend-webapp"
