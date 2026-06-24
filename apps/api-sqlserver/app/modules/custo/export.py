"""
export.py — Exporta o módulo Custo Produto para o sistema GrindX.

Uso:
    python -m app.modules.custo.export [export|package] [--dry-run] [--grindx-root PATH]
    python export.py [export|package] [--dry-run] [--grindx-root PATH]
"""

import argparse
import shutil
import zipfile
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

MODULE_NAME = "custo"
MODULE_SRC = Path(__file__).parent
STANDALONE_ROOT = MODULE_SRC.parent.parent.parent
GRINDX_ROOT = STANDALONE_ROOT.parent / "GrindX"
GRINDX_API = GRINDX_ROOT / "apps" / "api-sqlserver"
GRINDX_FRONTEND = GRINDX_ROOT / "packages" / "frontend-webapp"
FRONTEND_SRC = STANDALONE_ROOT / "frontend"

ROUTER_IMPORT = (
    "from app.modules.custo.routers.custo_produto_router import router as custo_router"
)
ROUTER_REGISTER = "app.include_router(custo_router)"


def copy_backend(dry_run: bool = False):
    dest = GRINDX_API / "app" / "modules" / "custo"
    if dry_run:
        logger.info("[DRY-RUN] Copiaria %s -> %s", MODULE_SRC, dest)
    else:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(
            MODULE_SRC,
            dest,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "tests"),
        )
        logger.info("Backend copiado")


def copy_frontend(dry_run: bool = False):
    dest_base = GRINDX_FRONTEND / "modules"
    if dry_run:
        logger.info(
            "[DRY-RUN] Copiaria sub-modulos de %s -> %s", FRONTEND_SRC, dest_base
        )
    else:
        for sub in FRONTEND_SRC.iterdir():
            if sub.is_dir():
                dest = dest_base / sub.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(sub, dest)
                logger.info("Frontend copiado: %s", sub.name)
            elif sub.is_file():
                dest = dest_base / sub.name
                shutil.copy2(sub, dest)
                logger.info("Arquivo copiado: %s", sub.name)


def register_routes(dry_run: bool = False):
    main_py = GRINDX_API / "app" / "main.py"
    if not main_py.exists():
        logger.warning("main.py nao encontrado, pulando registro de rotas")
        return

    content = main_py.read_text(encoding="utf-8")
    if ROUTER_IMPORT in content:
        logger.info("Rotas ja registradas")
        return

    lines = content.splitlines(keepends=True)
    last_import = last_include = None
    for i, line in enumerate(lines):
        if "from app." in line and "import router as" in line:
            last_import = i
        if "app.include_router(" in line:
            last_include = i

    if last_import is not None:
        lines.insert(last_import + 1, ROUTER_IMPORT + "\n")
        if last_include is not None and last_include >= last_import:
            last_include += 1
    if last_include is not None:
        lines.insert(last_include + 1, ROUTER_REGISTER + "\n")

    if dry_run:
        logger.info("[DRY-RUN] main.py alterado")
    else:
        main_py.write_text("".join(lines), encoding="utf-8")
        logger.info("Rotas registradas")


def package(dry_run: bool = False):
    module_dir = MODULE_SRC
    frontend_dir = FRONTEND_SRC
    dist_dir = STANDALONE_ROOT / "dist"
    zip_path = dist_dir / "modulo-custo.zip"

    if dry_run:
        logger.info("[DRY-RUN] Criaria %s com:", zip_path)
        logger.info("  - module.json")
        logger.info("  - app/modules/custo/")
        logger.info("  - frontend/")
        return

    dist_dir.mkdir(parents=True, exist_ok=True)
    added = set()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        manifest_path = STANDALONE_ROOT / "module.json"
        if manifest_path.exists():
            zf.write(manifest_path, "module.json")
            added.add("module.json")

        for file in module_dir.rglob("*"):
            if (
                file.is_file()
                and "__pycache__" not in file.parts
                and not file.name.endswith(".pyc")
                and "tests" not in file.parts
            ):
                arcname = str(file.relative_to(STANDALONE_ROOT))
                if arcname not in added:
                    zf.write(file, arcname)
                    added.add(arcname)

        for file in frontend_dir.rglob("*"):
            if file.is_file():
                rel = file.relative_to(frontend_dir)
                parts = list(rel.parts)
                if parts and parts[0] == "modules":
                    parts = parts[1:]
                arcname = str(Path("frontend") / Path(*parts))
                if arcname not in added:
                    zf.write(file, arcname)
                    added.add(arcname)

    logger.info("Pacote criado", path=str(zip_path), files=len(added))


def export(dry_run: bool = False):
    copy_backend(dry_run=dry_run)
    copy_frontend(dry_run=dry_run)
    register_routes(dry_run=dry_run)
    logger.info("Exportacao concluida")


def main():
    parser = argparse.ArgumentParser(description="Ferramentas do modulo Custo Produto")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["export", "package"],
        default="package",
        help="Comando a executar (export|package)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Apenas simula")
    parser.add_argument(
        "--grindx-root", type=str, default=None, help="Caminho para o GrindX"
    )

    args = parser.parse_args()

    if args.grindx_root:
        global GRINDX_ROOT, GRINDX_API, GRINDX_FRONTEND
        GRINDX_ROOT = Path(args.grindx_root)
        GRINDX_API = GRINDX_ROOT / "apps" / "api-sqlserver"
        GRINDX_FRONTEND = GRINDX_ROOT / "packages" / "frontend-webapp"

    if args.command == "export":
        export(dry_run=args.dry_run)
    elif args.command == "package":
        package(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
