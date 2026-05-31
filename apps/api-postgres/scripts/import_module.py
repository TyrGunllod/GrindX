"""
import_module.py — Importa um módulo empacotado em .zip para o GrindX.

Uso:
    python scripts/import_module.py projetos --import-dir=C:/tmp/extracted --force

Processo:
    1. Valida module.json no diretório extraído
    2. Faz backup dos arquivos que serão modificados
    3. Copia backend → app/modules/{module_name}/
    4. Copia frontend → packages/frontend-webapp/modules/{module_name}/
    5. Copia migração → alembic/versions/
    6. Edita main.py (import + include_router)
    7. Edita alembic/env.py (import do model)
    8. Roda alembic upgrade head
    9. Registra em portal_modulos

Args:
    module_name: Nome do módulo (snake_case) — corresponde ao diretório no zip
    --import-dir: Caminho do diretório extraído contendo module.json
    --force: Sobrescrever módulo existente sem perguntar
    --dry-run: Apenas simular
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

BACKUP_DIRNAME = ".backup"


def _get_monorepo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def _get_import_dir() -> Path:
    return _get_monorepo_root() / "import"


def validate_manifest(import_dir: Path) -> dict:
    manifest_path = import_dir / "module.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"module.json não encontrado em {import_dir}")

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    required = [
        "module_name",
        "entity_name",
        "schema_name",
        "route_prefix",
        "frontend_url",
        "menu_label",
    ]
    missing = [k for k in required if k not in manifest]
    if missing:
        raise ValueError(f"Campos obrigatórios ausentes no module.json: {missing}")

    return manifest


def backup_existing(manifest: dict) -> Path | None:
    api_dir = _get_monorepo_root() / "apps" / "api-postgres"
    backup_root = _get_import_dir() / BACKUP_DIRNAME
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / f"{manifest['module_name']}_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    files_to_backup = [
        api_dir / "app" / "main.py",
        api_dir / "app" / "auth" / "dependencies.py",
        api_dir / "alembic" / "env.py",
    ]
    for f in files_to_backup:
        if f.exists():
            shutil.copy2(f, backup_dir / f.name)
            logger.info("Backup criado: %s -> %s", f, backup_dir / f.name)

    return backup_dir


def copy_backend(import_dir: Path, module_name: str, force: bool) -> None:
    import tempfile

    src = import_dir / "app" / "modules" / module_name
    api_dir = _get_monorepo_root() / "apps" / "api-postgres"
    dest = api_dir / "app" / "modules" / module_name

    if not src.exists():
        logger.warning("Diretório backend não encontrado: %s", src)
        return

    if dest.exists():
        if not force:
            raise FileExistsError(
                f"Backend já existe em {dest}. Use --force para sobrescrever."
            )
        tmp_dest = Path(tempfile.mktempdir(suffix="_backend"))
        try:
            shutil.copytree(
                src, tmp_dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
            )
            shutil.rmtree(dest)
            shutil.move(str(tmp_dest), str(dest))
        except Exception:
            if tmp_dest.exists():
                shutil.rmtree(tmp_dest, ignore_errors=True)
            raise
        logger.info("Backend copiado: %s -> %s", src, dest)
    else:
        shutil.copytree(
            src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
        )
        logger.info("Backend copiado: %s -> %s", src, dest)


def copy_frontend(import_dir: Path, module_name: str, force: bool) -> None:
    import tempfile

    src = import_dir / "frontend"
    frontend_dir = _get_monorepo_root() / "apps" / "frontend-webapp"
    dest = frontend_dir / "modules" / module_name

    if not src.exists():
        logger.warning("Diretório frontend não encontrado: %s", src)
        return

    if dest.exists():
        if not force:
            raise FileExistsError(
                f"Frontend já existe em {dest}. Use --force para sobrescrever."
            )
        tmp_dest = Path(tempfile.mktempdir(suffix="_frontend"))
        try:
            shutil.copytree(src, tmp_dest)
            shutil.rmtree(dest)
            shutil.move(str(tmp_dest), str(dest))
        except Exception:
            if tmp_dest.exists():
                shutil.rmtree(tmp_dest, ignore_errors=True)
            raise
        logger.info("Frontend copiado: %s -> %s", src, dest)
    else:
        shutil.copytree(src, dest)
        logger.info("Frontend copiado: %s -> %s", src, dest)


def copy_migration(import_dir: Path) -> None:
    src_dir = import_dir / "migration"
    api_dir = _get_monorepo_root() / "apps" / "api-postgres"
    dest_dir = api_dir / "alembic" / "versions"

    if not src_dir.exists():
        logger.warning("Diretório migration não encontrado: %s", src_dir)
        return

    for f in src_dir.glob("*.py"):
        if f.name == "__init__.py":
            continue
        dest_path = dest_dir / f.name
        if dest_path.exists():
            logger.warning("Migration já existe, sobrescrevendo: %s", dest_path)
        shutil.copy2(f, dest_path)
        logger.info("Migration copiada: %s -> %s", f, dest_path)


def register_router(manifest: dict, force: bool) -> None:
    module_name = manifest["module_name"]
    api_dir = _get_monorepo_root() / "apps" / "api-postgres"
    main_py = api_dir / "app" / "main.py"

    content = main_py.read_text(encoding="utf-8")

    import_line = (
        f"from app.routers.{module_name}_router import router as {module_name}_router"
    )
    register_line = f"app.include_router({module_name}_router)"

    if import_line in content and register_line in content:
        logger.info("Router já registrado em main.py")
        return

    if not force and (import_line in content or register_line in content):
        raise FileExistsError("Router parcialmente registrado. Use --force.")

    lines = content.splitlines(keepends=True)
    last_import_idx = None
    last_include_idx = None

    for i, line in enumerate(lines):
        if "from app.routers." in line and "import router as" in line:
            last_import_idx = i
        if "app.include_router(" in line:
            last_include_idx = i

    if last_import_idx is None:
        logger.warning(
            "Não foi possível encontrar local para inserir import do router em main.py"
        )
    if last_include_idx is None:
        logger.warning(
            "Não foi possível encontrar local para inserir app.include_router() em main.py"
        )

    if last_import_idx is not None and import_line not in content:
        lines.insert(last_import_idx + 1, import_line + "\n")
        if last_include_idx is not None and last_include_idx >= last_import_idx:
            last_include_idx += 1

    if last_include_idx is not None and register_line not in content:
        lines.insert(last_include_idx + 1, register_line + "\n")

    main_py.write_text("".join(lines), encoding="utf-8")
    logger.info("Router registrado em main.py")


def register_alembic_import(manifest: dict, force: bool) -> None:
    module_name = manifest["module_name"]
    entity_name = manifest["entity_name"]
    api_dir = _get_monorepo_root() / "apps" / "api-postgres"
    env_py = api_dir / "alembic" / "env.py"

    content = env_py.read_text(encoding="utf-8")

    import_line = f"from app.modules.{module_name}.models.{module_name} import {entity_name}  # noqa: F401"

    if import_line in content:
        logger.info("Import já registrado em alembic/env.py")
        return

    marker = "from app.modules.portal.models.portal import Aba, Modulo  # noqa: F401"
    if marker in content:
        content = content.replace(marker, marker + "\n" + import_line)
        env_py.write_text(content, encoding="utf-8")
        logger.info("Import registrado em alembic/env.py")
    else:
        logger.warning(
            "Marker não encontrado em alembic/env.py. Adicione manualmente: %s",
            import_line,
        )


def run_migrations() -> None:
    api_dir = _get_monorepo_root() / "apps" / "api-postgres"
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=api_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Migration falhou:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )
    logger.info("Migrations executadas com sucesso")


def register_menu(manifest: dict) -> None:
    import sys as _sys

    module_name = manifest["module_name"]
    label = manifest.get("menu_label", module_name)
    url = manifest.get("frontend_url", f"modules/{module_name}/index.html")
    icone = manifest.get("menu_icone", "folder")
    slug = module_name

    api_dir = _get_monorepo_root() / "apps" / "api-postgres"
    if str(api_dir) not in _sys.path:
        _sys.path.insert(0, str(api_dir))

    from app.database import SessionLocal
    from app.models.portal import Aba, Modulo

    with SessionLocal() as db:
        aba = db.query(Aba).filter(Aba.nome.ilike("%principal%")).first()
        if not aba:
            aba = db.query(Aba).order_by(Aba.id).first()
        if not aba:
            logger.warning("Nenhuma aba encontrada para registrar o módulo no menu")
            return

        existing = db.query(Modulo).filter(Modulo.slug == slug).first()
        if existing:
            logger.info(
                "Módulo já registrado no menu (slug=%s, id=%d)", slug, existing.id
            )
        else:
            mod = Modulo(aba_id=aba.id, nome=label, slug=slug, url=url, icone=icone)
            db.add(mod)
            db.commit()
            logger.info("Menu registrado: %s (slug=%s)", label, slug)


def rollback(backup_dir: Path | None) -> None:
    if not backup_dir or not backup_dir.exists():
        logger.warning("Nada para restaurar")
        return

    api_dir = _get_monorepo_root() / "apps" / "api-postgres"
    restored = 0
    for f in backup_dir.iterdir():
        if f.name == "main.py":
            dest = api_dir / "app" / "main.py"
        elif f.name == "dependencies.py":
            dest = api_dir / "app" / "auth" / "dependencies.py"
        elif f.name == "env.py":
            dest = api_dir / "alembic" / "env.py"
        else:
            continue
        shutil.copy2(f, dest)
        restored += 1
        logger.info("Restaurado: %s -> %s", f, dest)

    logger.info("Rollback concluído: %d arquivos restaurados", restored)


def import_module(
    module_name: str, import_dir: Path, force: bool = False, dry_run: bool = False
) -> dict:
    steps = []
    backup_path = None

    try:
        manifest = validate_manifest(import_dir)
        steps.append("Manifesto validado")

        if not dry_run:
            backup_path = backup_existing(manifest)
        steps.append("Backup concluído")

        if not dry_run:
            copy_backend(import_dir, module_name, force)
        steps.append("Backend copiado")

        if not dry_run:
            copy_frontend(import_dir, module_name, force)
        steps.append("Frontend copiado")

        if not dry_run:
            copy_migration(import_dir)
        steps.append("Migration copiada")

        if not dry_run:
            register_router(manifest, force)
        steps.append("Router registrado")

        if not dry_run:
            register_alembic_import(manifest, force)
        steps.append("Import do model registrado no alembic/env.py")

        if not dry_run:
            run_migrations()
        steps.append("Migrations executadas")

        if not dry_run:
            register_menu(manifest)
        steps.append("Menu registrado")

        return {"success": True, "steps": steps}

    except Exception as e:
        logger.error("Erro na importação: %s", str(e))
        if not dry_run and backup_path:
            rollback(backup_path)
        return {"success": False, "steps": steps, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Importa um módulo .zip para o GrindX")
    parser.add_argument("module_name", help="Nome do módulo (snake_case)")
    parser.add_argument(
        "--import-dir", required=True, help="Diretório com o conteúdo extraído do .zip"
    )
    parser.add_argument(
        "--force", action="store_true", help="Sobrescrever módulo existente"
    )
    parser.add_argument("--dry-run", action="store_true", help="Apenas simular")
    args = parser.parse_args()

    import_dir = Path(args.import_dir)
    if not import_dir.exists():
        print(f"ERRO: Diretório não encontrado: {import_dir}")
        sys.exit(1)

    result = import_module(
        args.module_name, import_dir, force=args.force, dry_run=args.dry_run
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
