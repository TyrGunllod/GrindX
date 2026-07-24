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
    import re

    dest = GRINDX_API / "alembic" / "versions"

    # Escanear prefixo numerico dos arquivos de migration do GrindX
    last_num = 0
    last_rev = "000"
    if dest.exists():
        files = list(dest.glob("*.py"))
        logger.info("Diretorio de migrations: %s (%d arquivos .py)", dest, len(files))
        for f in files:
            m = re.match(r"^(\d+)", f.name)
            if m:
                n = int(m.group(1))
                logger.info("  Encontrado: %s (prefixo %d)", f.name, n)
                if n > last_num:
                    last_num = n
                    last_rev = m.group(1)
    else:
        logger.warning("Diretorio de migrations nao encontrado: %s", dest)

    next_rev = str(last_num + 1).zfill(3)

    # Se MIGRATION_SRC nao existe (rodando dentro do GrindX), procura migration
    # ja copiada no dest e renomeia/atualiza in-place
    if not MIGRATION_SRC.exists() or not list(MIGRATION_SRC.glob("*.py")):
        for old_file in dest.glob("*_pop_modelos*.py"):
            content = old_file.read_text(encoding="utf-8")
            old_rev = re.search(r'revision\s*=\s*"(\d+)"', content)
            if old_rev and old_rev.group(1) == next_rev:
                logger.info("Migration ja esta com revision %s, pulando", next_rev)
                return
            if dry_run:
                logger.info("[DRY-RUN] Renomearia %s para %s (revision %s, down_revision %s)", old_file.name, next_rev + "_criar_tabela_pop_modelos.py", next_rev, last_rev)
                return
            content = re.sub(r'revision\s*=\s*"[^"]*"', f'revision = "{next_rev}"', content)
            content = re.sub(r'down_revision\s*=\s*[^#\n]+', f'down_revision = "{last_rev}"', content)
            new_name = re.sub(r'^\d+', next_rev, old_file.name)
            dest_path = dest / new_name
            old_file.rename(dest_path)
            dest_path.write_text(content, encoding="utf-8")
            logger.info("Migration renomeada: %s -> %s (revision %s, down_revision %s)", old_file.name, new_name, next_rev, last_rev)
        return

    for f in MIGRATION_SRC.glob("*.py"):
        content = f.read_text(encoding="utf-8")
        src_rev_match = re.search(r'revision\s*=\s*"(\d+)"', content)
        src_rev = int(src_rev_match.group(1)) if src_rev_match else 0
        # Se a revision da fonte for maior que a ultima existente, mantem
        use_rev = str(src_rev).zfill(3) if src_rev > last_num else next_rev
        down = last_rev if src_rev > last_num else last_rev
        content = re.sub(r'revision\s*=\s*"[^"]*"', f'revision = "{use_rev}"', content)
        content = re.sub(r'down_revision\s*=\s*[^#\n]+', f'down_revision = "{down}"', content)
        if re.match(r'^\d+', f.name):
            new_name = re.sub(r'^\d+', use_rev, f.name)
        else:
            new_name = use_rev + "_" + f.name
        dest_path = dest / new_name
        if dry_run:
            logger.info("[DRY-RUN] Criaria %s (revision %s, down_revision %s)", dest_path, use_rev, down)
        else:
            dest_path.write_text(content, encoding="utf-8")
            logger.info("Migration %s copiada como %s (revision %s, down_revision %s)", f.name, new_name, use_rev, down)


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
    line = "from app.modules.pop_modelos.models.pop_modelos import PopModelo  # noqa: F401"
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
    new_lines = [l for l in lines if "pop_modelos" not in l]
    if len(new_lines) == len(lines):
        logger.info("Rotas nao registradas nada a fazer")
        return
    if dry_run:
        logger.info("[DRY-RUN] Removeria rotas de main.py")
    else:
        main_py.write_text("".join(new_lines), encoding="utf-8")
        logger.info("Rotas removidas de main.py")


def unregister_dependency(dry_run: bool = False):
    import re

    deps_py = GRINDX_API / "app" / "auth" / "dependencies.py"
    if not deps_py.exists():
        return
    content = deps_py.read_text(encoding="utf-8")
    # Encontra bloco: do primeiro import pop_modelos ate a linha do marker
    pattern = re.compile(
        r"(from app\.modules\.pop_modelos\.[^\n]*\n.*?)(\n?# --- Vers.oes vinculadas)",
        re.DOTALL
    )
    match = pattern.search(content)
    if not match:
        logger.info("Dependency nao registrada nada a fazer")
        return
    if dry_run:
        logger.info("[DRY-RUN] Removeria block de dependencies.py")
    else:
        new_content = content[:match.start()] + content[match.start(2):]
        deps_py.write_text(new_content, encoding="utf-8")
        logger.info("Dependency removida de dependencies.py")


def unregister_alembic_import(dry_run: bool = False):
    env_py = GRINDX_API / "alembic" / "env.py"
    if not env_py.exists():
        return
    content = env_py.read_text(encoding="utf-8")
    line = "from app.modules.pop_modelos.models.pop_modelos import PopModelo  # noqa: F401"
    if line not in content:
        logger.info("Alembic import nao registrado nada a fazer")
        return
    if dry_run:
        logger.info("[DRY-RUN] Removeria import de alembic/env.py")
    else:
        env_py.write_text(content.replace(line + "\n", ""), encoding="utf-8")
        logger.info("Alembic import removido")


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


def uninstall(dry_run: bool = False):
    unregister_routes(dry_run)
    unregister_dependency(dry_run)
    unregister_alembic_import(dry_run)
    remove_backend(dry_run)
    remove_frontend(dry_run)
    remove_migration(dry_run)
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
                arcname = str(f.relative_to(STANDALONE_ROOT))
                zf.write(f, arcname)
        for f in FRONTEND_SRC.rglob("*"):
            if f.is_file():
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
        GRINDX_FRONTEND = GRINDX_ROOT / "packages" / "frontend-webapp"
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
