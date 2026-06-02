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
        "menu_label",
    ]
    missing = [k for k in required if k not in manifest]
    if missing:
        raise ValueError(f"Campos obrigatórios ausentes no module.json: {missing}")

    if "frontend_url" not in manifest and "frontend_tabs" not in manifest:
        raise ValueError(
            "Campo obrigatório ausente no module.json: frontend_url ou frontend_tabs"
        )

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
        import uuid
        tmp_dest = Path(tempfile.gettempdir()) / f"grindx_backend_{uuid.uuid4().hex[:8]}"
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
    src = import_dir / "frontend"
    frontend_dir = _get_monorepo_root() / "apps" / "frontend-webapp"
    dest_base = frontend_dir / "modules"

    if not src.exists():
        logger.warning("Diretório frontend não encontrado: %s", src)
        return

    for item in src.iterdir():
        if item.is_dir():
            dest = dest_base / item.name
            if dest.exists():
                if not force:
                    logger.warning("Frontend já existe: %s. Use --force para sobrescrever.", dest)
                    continue
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
            logger.info("Frontend copiado: %s -> %s", item.name, dest)
        elif item.is_file():
            dest = dest_base / item.name
            shutil.copy2(item, dest)
            logger.info("Arquivo copiado: %s", item.name)


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


def register_router(manifest: dict, force: bool, main_py: Path | None = None) -> None:
    module_name = manifest["module_name"]
    if main_py is None:
        api_dir = _get_monorepo_root() / "apps" / "api-postgres"
        main_py = api_dir / "app" / "main.py"

    content = main_py.read_text(encoding="utf-8")

    import_line = f"from app.modules.{module_name}.routers.{module_name}_router import router as {module_name}_router"
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
        if "from app." in line and "import router as" in line:
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
    if last_import_idx is None and last_include_idx is None:
        raise RuntimeError(
            "Não foi possível encontrar nenhum import de router em main.py. "
            "Adicione manualmente o import e o include_router."
        )

    if last_import_idx is not None and import_line not in content:
        lines.insert(last_import_idx + 1, import_line + "\n")
        if last_include_idx is not None and last_include_idx >= last_import_idx:
            last_include_idx += 1

    if last_include_idx is not None and register_line not in content:
        lines.insert(last_include_idx + 1, register_line + "\n")

    main_py.write_text("".join(lines), encoding="utf-8")
    logger.info("Router registrado em main.py")


def register_dependency(
    manifest: dict, force: bool, deps_py: Path | None = None
) -> None:
    module_name = manifest["module_name"]
    entity_name = manifest["entity_name"]
    if deps_py is None:
        api_dir = _get_monorepo_root() / "apps" / "api-postgres"
        deps_py = api_dir / "app" / "auth" / "dependencies.py"

    content = deps_py.read_text(encoding="utf-8")

    factory_name = f"get_{module_name}_service"
    import_repo = f"from app.modules.{module_name}.repositories.{module_name}_repository import {entity_name}Repository"
    import_svc = f"from app.modules.{module_name}.services.{module_name}_service import {entity_name}Service"
    factory_sig = (
        f"def {factory_name}(db: Session = Depends(get_db)) -> {entity_name}Service:"
    )

    if factory_name in content and import_repo in content and import_svc in content:
        logger.info("Dependency já registrado em dependencies.py")
        return

    if not force and (
        factory_name in content or import_repo in content or import_svc in content
    ):
        raise FileExistsError("Dependency parcialmente registrado. Use --force.")

    marker = "# --- Versões vinculadas das permissões ---"
    if marker not in content:
        raise RuntimeError(
            "Marker '# --- Versões vinculadas das permissões ---' não encontrado em dependencies.py. "
            "Adicione manualmente o factory."
        )

    factory_block = (
        f"{import_repo}\n"
        f"{import_svc}\n"
        f"\n"
        f"\n"
        f"{factory_sig}\n"
        f'    """Factory para o {entity_name}Service."""\n'
        f"    repository = {entity_name}Repository(db)\n"
        f"    return {entity_name}Service(repository)\n"
        f"\n"
        f"\n"
        f"{marker}\n"
    )

    content = content.replace(marker, factory_block)
    deps_py.write_text(content, encoding="utf-8")
    logger.info("Dependency registrado em dependencies.py: %s", factory_name)


def register_alembic_import(
    manifest: dict, force: bool, env_py: Path | None = None
) -> None:
    module_name = manifest["module_name"]
    entity_name = manifest["entity_name"]
    if env_py is None:
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


def _get_venv_python() -> str:
    """Retorna o caminho do Python do venv do GrindX, se existir."""
    venv_python = (
        _get_monorepo_root()
        / "apps"
        / "api-postgres"
        / ".venv"
        / "Scripts"
        / "python.exe"
    )
    if venv_python.exists():
        return str(venv_python)
    venv_python = (
        _get_monorepo_root() / "apps" / "api-postgres" / ".venv" / "bin" / "python"
    )
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def run_migrations() -> None:
    api_dir = _get_monorepo_root() / "apps" / "api-postgres"
    python_exe = _get_venv_python()
    logger.info("Usando Python: %s", python_exe)
    try:
        result = subprocess.run(
            [python_exe, "-m", "alembic", "upgrade", "head"],
            cwd=api_dir,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "Migration excedeu timeout de 120s. Verifique o banco de dados."
        )
    except KeyboardInterrupt:
        raise RuntimeError("Migration interrompida pelo usuário.")
    if result.returncode != 0:
        raise RuntimeError(
            f"Migration falhou:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )
    logger.info("Migrations executadas com sucesso")


def register_menu(manifest: dict) -> None:
    import sys as _sys

    module_name = manifest["module_name"]
    label = manifest.get("menu_label", module_name)
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
            logger.warning("Nenhuma aba encontrada — criando aba 'Principal'")
            aba = Aba(nome="Principal", icone="home", ordem=1)
            db.add(aba)
            db.commit()
            db.refresh(aba)
            logger.info("Aba criada: id=%d", aba.id)

        existing = db.query(Modulo).filter(Modulo.slug == slug).first()
        if existing:
            logger.info(
                "Módulo já registrado no menu (slug=%s, id=%d)", slug, existing.id
            )
        else:
            frontend_tabs = manifest.get("frontend_tabs", [])
            if frontend_tabs:
                for tab in frontend_tabs:
                    tab_name = tab.get("name", module_name)
                    tab_url = tab.get("url", f"modules/{module_name}/index.html")
                    tab_icone = tab.get("menu_icone", icone)
                    tab_slug = tab_url.split("/")[1] if "/" in tab_url else f"{module_name}_{tab_name.lower().replace(' ', '_')}"
                    tab_mod = Modulo(
                        aba_id=aba.id, nome=tab_name, slug=tab_slug,
                        url=tab_url, icone=tab_icone,
                    )
                    db.add(tab_mod)
                db.commit()
                logger.info(
                    "Menu registrado: %s (%d abas)", label, len(frontend_tabs)
                )
            else:
                url = manifest.get("frontend_url", f"modules/{module_name}/index.html")
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
            register_dependency(manifest, force)
        steps.append("Dependency registrado em dependencies.py")

        if not dry_run:
            register_alembic_import(manifest, force)
        steps.append("Import do model registrado no alembic/env.py")

        if not dry_run:
            register_menu(manifest)
        steps.append("Menu registrado")

        try:
            if not dry_run:
                run_migrations()
            steps.append("Migrations executadas")
        except Exception as e:
            logger.warning("Migration falhou (tabelas podem já existir): %s", str(e))
            steps.append(f"Migration ignorada: {str(e)[:100]}")

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
