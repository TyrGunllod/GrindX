"""
export.py — Exporta o modulo PopModelo para o sistema GrindX.

Uso:
    python -m app.modules.pop_modelos.export [--dry-run] [--grindx-root PATH]
"""

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

MODULE_NAME = "PopModelo"
EXCLUDE_DIRS = {"shared"}
MODULE_SRC = Path(__file__).parent
STANDALONE_ROOT = MODULE_SRC.parent.parent.parent

def _find_grindx_root():
    current = Path(__file__).resolve().parent
    while current.parent != current:
        if (current / "apps").is_dir() and (current / "packages").is_dir():
            return current
        current = current.parent
    return None

GRINDX_ROOT = _find_grindx_root() or (STANDALONE_ROOT.parent / "GrindX")
GRINDX_API = GRINDX_ROOT / "apps" / "api-postgres"
GRINDX_FRONTEND = GRINDX_ROOT / "packages" / "frontend-webapp"
FRONTEND_SRC = STANDALONE_ROOT / "frontend"
MIGRATION_SRC = STANDALONE_ROOT / "migration"

ROUTER_IMPORT = "from app.modules.pop_modelos.routers.pop_modelos_router import router as pop_modelos_router"
ROUTER_REGISTER = "app.include_router(pop_modelos_router)"


def copy_backend(dry_run: bool = False):
    dest = GRINDX_API / "app" / "modules" / "pop_modelos"
    if MODULE_SRC.resolve() == dest.resolve():
        logger.info("Backend ja esta no destino, pulando copia")
        return
    if dry_run:
        logger.info("[DRY-RUN] Copiaria %s -> %s", MODULE_SRC, dest)
    else:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(MODULE_SRC, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        logger.info("Backend copiado")


def copy_frontend(dry_run: bool = False):
    dest_base = GRINDX_FRONTEND / "modules"
    if dry_run:
        logger.info("[DRY-RUN] Copiaria %s -> %s", FRONTEND_SRC, dest_base)
    else:
        if not FRONTEND_SRC.exists():
            logger.info("Frontend source nao encontrado, pulando copia")
            return
        for sub in FRONTEND_SRC.iterdir():
            if sub.name in EXCLUDE_DIRS:
                logger.info("Pulando pasta excluída: %s", sub.name)
                continue
            if sub.is_dir():
                dest = dest_base / sub.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(sub, dest)
                logger.info("Frontend copiado: %s -> %s", sub.name, dest)
            elif sub.is_file():
                dest = dest_base / sub.name
                shutil.copy2(sub, dest)
                logger.info("Arquivo copiado: %s", sub.name)


def copy_migration(dry_run: bool = False):
    import json
    import re

    dest = GRINDX_API / "alembic" / "versions"

    if not dest.exists():
        logger.warning("Diretorio de migrations nao encontrado: %s", dest)
        return

    # Read migration_start_number from module.json
    manifest_path = MODULE_SRC / "module.json"
    start_num = 100
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            start_num = int(manifest.get("migration_start_number", 100))
        except Exception:
            pass

    # Find the last native revision (prefix < 100)
    last_rev = None
    last_num = 0
    for f in dest.glob("*.py"):
        m = re.match(r"^(\d+)_", f.name)
        if not m:
            continue
        num = int(m.group(1))
        if num >= 100:
            continue
        if num > last_num:
            content = f.read_text(encoding="utf-8")
            rev_match = re.search(
                r'revision\s*[=:]\s*(?:str\s*=\s*)?\"([^\"]+)\"', content
            )
            if rev_match:
                last_rev = rev_match.group(1)
                last_num = num

    if not last_rev:
        logger.error("Nenhuma migration nativa encontrada para encadear")
        return

    # Find highest module migration number (>= 100)
    highest_module = 99
    for f in dest.glob("*.py"):
        m = re.match(r"^(\d{3,})_", f.name)
        if m:
            num = int(m.group(1))
            if num >= 100 and num > highest_module:
                highest_module = num

    actual_start = max(start_num, highest_module + 1)

    # Remove existing migrations for this module (re-import)
    module_name = MODULE_NAME.lower()
    for f in dest.glob("*.py"):
        m = re.match(r"^\d{3,}_", f.name)
        if m:
            try:
                content = f.read_text(encoding="utf-8")
                if module_name in content.lower():
                    if dry_run:
                        logger.info("[DRY-RUN] Removeria %s", f)
                    else:
                        f.unlink()
                        logger.info("Migration removida para reexport: %s", f.name)
            except Exception:
                pass

    # If MIGRATION_SRC exists (standalone dev), process from source
    if MIGRATION_SRC.exists() and list(MIGRATION_SRC.glob("*.py")):
        migration_files = sorted(
            [f for f in MIGRATION_SRC.glob("*.py") if f.name != "__init__.py"]
        )
        prev_rev = last_rev
        for i, f in enumerate(migration_files):
            content = f.read_text(encoding="utf-8")
            rev_num = actual_start + i
            rev = str(rev_num).zfill(max(3, len(str(rev_num))))

            content = re.sub(
                r'revision(?:\s*:\s*\w+(?:\s*\|\s*None)?)?\s*=\s*"[^"]*"',
                f'revision: str = "{rev}"',
                content,
            )
            content = re.sub(
                r'down_revision(?:\s*:\s*\w+(?:\s*\|\s*None)?)?\s*=\s*[^#\n]+',
                f'down_revision: str | None = "{prev_rev}"',
                content,
            )

            name = f.name
            name = re.sub(r"^\d+_", "", name)
            new_name = f"{rev}_{name}"

            dest_path = dest / new_name
            if dry_run:
                logger.info("[DRY-RUN] Criaria %s (revision %s, down_revision %s)", dest_path, rev, prev_rev)
            else:
                dest_path.write_text(content, encoding="utf-8")
                logger.info("Migration %s copiada como %s (revision %s, down_revision %s)", f.name, new_name, rev, prev_rev)

            prev_rev = rev
    else:
        # Processing already-copied migrations (rename in-place)
        for old_file in dest.glob(f"*_{module_name}*.py"):
            content = old_file.read_text(encoding="utf-8")
            old_rev = re.search(r'revision\s*[=:]\s*(?:str\s*=\s*)?\"(\d+)\"', content)
            if old_rev:
                old_rev_val = int(old_rev.group(1))
                if old_rev_val >= 100 and old_rev_val == actual_start:
                    logger.info("Migration ja esta com revision %d, pulando", actual_start)
                    return
            if dry_run:
                logger.info("[DRY-RUN] Renomearia %s", old_file.name)
                return

            new_rev_num = actual_start
            rev = str(new_rev_num).zfill(max(3, len(str(new_rev_num))))

            content = re.sub(
                r'revision(?:\s*:\s*\w+(?:\s*\|\s*None)?)?\s*=\s*"[^"]*"',
                f'revision: str = "{rev}"',
                content,
            )
            content = re.sub(
                r'down_revision(?:\s*:\s*\w+(?:\s*\|\s*None)?)?\s*=\s*[^#\n]+',
                f'down_revision: str | None = "{last_rev}"',
                content,
            )

            new_name = re.sub(r"^\d+_", f"{rev}_", old_file.name)
            dest_path = dest / new_name
            if dry_run:
                logger.info("[DRY-RUN] Renomearia %s -> %s", old_file.name, new_name)
                return

            old_file.rename(dest_path)
            dest_path.write_text(content, encoding="utf-8")
            logger.info("Migration renomeada: %s -> %s (revision %s, down_revision %s)", old_file.name, new_name, rev, last_rev)


def register_routes(dry_run: bool = False):
    main_py = GRINDX_API / "app" / "main.py"
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


def register_dependency(dry_run: bool = False):
    deps_py = GRINDX_API / "app" / "auth" / "dependencies.py"
    if not deps_py.exists():
        return
    content = deps_py.read_text(encoding="utf-8")
    marker = "# --- Versões vinculadas das permissões ---"
    factory = (
        "from app.modules.pop_modelos.repositories.pop_modelos_repository import PopModeloRepository\n"
        "from app.modules.pop_modelos.services.pop_modelos_service import PopModeloService\n\n\n"
        "def get_pop_modelos_service(db: Session = Depends(get_db)) -> PopModeloService:\n"
        '    """Factory para o PopModeloService."""\n'
        "    repository = PopModeloRepository(db)\n"
        "    return PopModeloService(repository)\n\n\n"
        f"{marker}\n"
    )
    if "get_pop_modelos_service" in content:
        logger.info("Dependency já registrada")
        return
    if dry_run:
        logger.info("[DRY-RUN] auth/dependencies.py alterado")
    else:
        deps_py.write_text(content.replace(marker, factory), encoding="utf-8")
        logger.info("Dependency registrada")


def register_alembic_import(dry_run: bool = False):
    env_py = GRINDX_API / "alembic" / "env.py"
    if not env_py.exists():
        return
    content = env_py.read_text(encoding="utf-8")
    line = "from app.modules.pop_modelos.models.pop_modelo import PopModelo  # noqa: F401"
    if line in content:
        logger.info("Alembic import já registrado")
        return
    marker = "from app.modules.portal.models.portal import Aba, Modulo  # noqa: F401"
    if dry_run:
        logger.info("[DRY-RUN] alembic/env.py alterado")
    else:
        env_py.write_text(content.replace(marker, marker + "\n" + line), encoding="utf-8")
        logger.info("Alembic import registrado")


def run_migrations(dry_run: bool = False):
    cmd = [sys.executable, "-m", "alembic", "upgrade", "head"]
    if dry_run:
        logger.info("[DRY-RUN] Comando: %s", " ".join(cmd))
    else:
        result = subprocess.run(cmd, cwd=GRINDX_API, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error("Migration falhou", stderr=result.stderr)
            raise RuntimeError("Migration error: %s" % result.stderr)
        logger.info("Migrations executadas")


def unregister_routes(dry_run: bool = False):
    main_py = GRINDX_API / "app" / "main.py"
    if not main_py.exists():
        return
    content = main_py.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    removed_imports = [l.strip() for l in lines if "pop_modelos" in l and "from app." in l]
    removed_routers = [l.strip() for l in lines if "pop_modelos" in l and "include_router" in l]
    new_lines = [l for l in lines if "pop_modelos" not in l]
    if len(new_lines) == len(lines):
        logger.info("Rotas nao registradas em main.py")
        return
    if dry_run:
        logger.info("[DRY-RUN] Removeria de main.py: %d linhas", len(lines) - len(new_lines))
    else:
        main_py.write_text("".join(new_lines), encoding="utf-8")
        logger.info("Removido de main.py: import=%s, include=%s", removed_imports, removed_routers)


def unregister_dependency(dry_run: bool = False):
    deps_py = GRINDX_API / "app" / "auth" / "dependencies.py"
    if not deps_py.exists():
        return
    import re

    content = deps_py.read_text(encoding="utf-8")
    orig_len = len(content)
    module_name = "pop_modelos"
    # Remove imports do modulo
    content_clean = re.sub(
        rf"^from app\.modules\.{re.escape(module_name)}\..*\n?",
        "",
        content,
        flags=re.MULTILINE,
    )
    # Remove factories geradas pelo register_dependency (prefixo get_{module_name}_)
    content_clean = re.sub(
        rf"^def get_{re.escape(module_name)}_.*(?:\n[ \t]+.*)*\n?",
        "",
        content_clean,
        flags=re.MULTILINE,
    )
    # Fallback: remove qualquer linha restante que referencie o modulo
    lines = content_clean.splitlines(keepends=True)
    module_path_prefix = f"app.modules.{module_name}"
    lines = [line for line in lines if module_path_prefix not in line]
    content_clean = "".join(lines)
    content_clean = re.sub(r"\n{3,}", "\n\n", content_clean)
    if len(content_clean) != orig_len:
        if dry_run:
            logger.info("[DRY-RUN] Limparia dependencies.py")
        else:
            deps_py.write_text(content_clean, encoding="utf-8")
            logger.info("Dependencies limpas em auth/dependencies.py")


def unregister_alembic_import(dry_run: bool = False):
    env_py = GRINDX_API / "alembic" / "env.py"
    if not env_py.exists():
        return
    content = env_py.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    removed = [l.strip() for l in lines if "pop_modelos" in l]
    new_lines = [l for l in lines if "pop_modelos" not in l]
    if len(new_lines) == len(lines):
        logger.info("Alembic import nao registrado em env.py")
        return
    if dry_run:
        logger.info("[DRY-RUN] Removeria de env.py: %s", removed)
    else:
        env_py.write_text("".join(new_lines), encoding="utf-8")
        logger.info("Removido de env.py: %s", removed)


def remove_backend(dry_run: bool = False):
    dest = GRINDX_API / "app" / "modules" / "pop_modelos"
    if not dest.exists():
        return
    if dry_run:
        logger.info("[DRY-RUN] Removeria %s", dest)
    else:
        shutil.rmtree(dest)
        logger.info("Backend removido: %s", dest)


def remove_frontend(dry_run: bool = False):
    dest_base = GRINDX_FRONTEND / "modules"
    for sub in ["pop_modelos"]:
        dest = dest_base / sub
        if dest.exists():
            if dry_run:
                logger.info("[DRY-RUN] Removeria %s", dest)
            else:
                shutil.rmtree(dest)
                logger.info("Frontend removido: %s", dest)


def remove_migration(dry_run: bool = False):
    dest = GRINDX_API / "alembic" / "versions"
    for f in dest.glob("*.py"):
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if "pop_modelos" in content:
            if dry_run:
                logger.info("[DRY-RUN] Removeria %s", f)
            else:
                f.unlink()
                logger.info("Migration removida: %s", f.name)


def clean_requirements_txt(dry_run: bool = False):
    req_file = GRINDX_API / "requirements.txt"
    if not req_file.exists():
        return
    content = req_file.read_text(encoding="utf-8")
    marker = "# === Modulo pop_modelos ==="
    if marker not in content:
        return
    lines = content.splitlines(keepends=True)
    cleaned = []
    skip = False
    for line in lines:
        if line.strip() == marker:
            skip = True
            continue
        if skip:
            if line.strip().startswith("#") or not line.strip():
                skip = False
                continue
            skip = False
            continue
        cleaned.append(line)
    if dry_run:
        logger.info("[DRY-RUN] Limparia requirements.txt")
    else:
        req_file.write_text("".join(cleaned))
        logger.info("Dependencias removidas do requirements.txt")


def uninstall(dry_run: bool = False):
    unregister_routes(dry_run)
    unregister_dependency(dry_run)
    unregister_alembic_import(dry_run)
    remove_backend(dry_run)
    remove_frontend(dry_run)
    remove_migration(dry_run)
    clean_requirements_txt(dry_run)
    logger.info("Modulo removido do GrindX")


def package(dry_run: bool = False):
    dist_dir = STANDALONE_ROOT / "dist"
    zip_path = dist_dir / "modulo-pop_modelos.zip"
    if dry_run:
        logger.info("[DRY-RUN] Criaria %s com:", zip_path)
        logger.info("  - module.json")
        logger.info("  - app/modules/pop_modelos/")
        logger.info("  - frontend/")
        logger.info("  - migration/")
        return
    dist_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        manifest = STANDALONE_ROOT / "module.json"
        if manifest.exists():
            zf.write(manifest, "module.json")
        for f in MODULE_SRC.rglob("*"):
            if f.is_file() and "__pycache__" not in f.parts and not f.name.endswith(".pyc"):
                if any(part in EXCLUDE_DIRS for part in f.parts):
                    continue
                arcname = str(f.relative_to(STANDALONE_ROOT))
                zf.write(f, arcname)
        for f in FRONTEND_SRC.rglob("*"):
            if f.is_file():
                if any(part in EXCLUDE_DIRS for part in f.parts):
                    continue
                arcname = str(f.relative_to(STANDALONE_ROOT))
                zf.write(f, arcname)
        for f in MIGRATION_SRC.glob("*.py"):
            zf.write(f, "migration/" + f.name)
    logger.info("Zip gerado: %s", zip_path)


def main():
    parser = argparse.ArgumentParser(description="Exporta modulo PopModelo para o GrindX")
    parser.add_argument("--dry-run", action="store_true", help="Apenas exibe o que seria feito")
    parser.add_argument("--grindx-root", type=str, help="Caminho para a raiz do GrindX")
    parser.add_argument("action", nargs="?", default="export", choices=["export", "package", "uninstall"], help="Acao a executar")
    args = parser.parse_args()
    dry = args.dry_run
    if args.grindx_root:
        global GRINDX_ROOT, GRINDX_API, GRINDX_FRONTEND
        GRINDX_ROOT = Path(args.grindx_root)
        GRINDX_API = GRINDX_ROOT / "apps" / "api-postgres"
        GRINDX_FRONTEND = GRINDX_ROOT / "apps" / "frontend-webapp"
    if args.action == "package":
        package(dry)
        return
    if args.action == "uninstall":
        uninstall(dry)
        return
    copy_backend(dry)
    copy_frontend(dry)
    copy_migration(dry)
    register_routes(dry)
    register_dependency(dry)
    register_alembic_import(dry)
    if not dry:
        run_migrations(dry)
        logger.info("Exportacao concluida com sucesso!")
    else:
        logger.info("[DRY-RUN] Exportacao simulada concluida")


if __name__ == "__main__":
    main()
