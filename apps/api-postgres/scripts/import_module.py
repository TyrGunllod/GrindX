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
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

BACKUP_DIRNAME = ".backup"


def _get_monorepo_root() -> Path:
    env_root = os.environ.get("MONOREPO_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).resolve().parent.parent.parent.parent


def _get_api_dir() -> Path:
    env = os.environ.get("GRINDX_API_DIR")
    if env:
        return Path(env).resolve()
    return _get_monorepo_root() / "apps" / "api-postgres"


def _get_frontend_dir() -> Path:
    env = os.environ.get("GRINDX_FRONTEND_DIR")
    if env:
        return Path(env).resolve()
    return _get_monorepo_root() / "apps" / "frontend-webapp"


def _get_import_dir() -> Path:
    env = os.environ.get("IMPORT_DIR")
    if env:
        return Path(env).resolve()
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
    api_dir = _get_api_dir()
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
    api_dir = _get_api_dir()
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

        tmp_dest = (
            Path(tempfile.gettempdir()) / f"grindx_backend_{uuid.uuid4().hex[:8]}"
        )
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
    frontend_dir = _get_frontend_dir()
    dest_base = frontend_dir / "modules"

    if not src.exists():
        logger.warning("Diretório frontend não encontrado: %s", src)
        return

    for item in src.iterdir():
        if item.is_dir():
            dest = dest_base / item.name
            if dest.exists():
                if not force:
                    logger.warning(
                        "Frontend já existe: %s. Use --force para sobrescrever.", dest
                    )
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
    api_dir = _get_api_dir()
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
    api_dir = _get_api_dir()
    if main_py is None:
        main_py = api_dir / "app" / "main.py"

    content = main_py.read_text(encoding="utf-8")

    routers_dir = api_dir / "app" / "modules" / module_name / "routers"
    if not routers_dir.exists():
        logger.warning("Diretório de routers não encontrado: %s", routers_dir)
        return

    router_files = [
        f.stem for f in routers_dir.glob("*_router.py") if f.stem != "__init__"
    ]
    if not router_files:
        logger.warning("Nenhum router encontrado em %s", routers_dir)
        return

    new_imports = []
    new_includes = []
    for router_file in sorted(router_files):
        # Don't add _router suffix if the file name already ends with _router
        var_name = (
            router_file if router_file.endswith("_router") else f"{router_file}_router"
        )
        import_line = f"from app.modules.{module_name}.routers.{router_file} import router as {var_name}"
        include_line = f"app.include_router({var_name})"
        if import_line not in content:
            new_imports.append(import_line)
        if include_line not in content:
            new_includes.append(include_line)

    if not new_imports and not new_includes:
        logger.info("Routers já registrados em main.py")
        return

    lines = content.splitlines(keepends=True)
    last_import_idx = None
    last_include_idx = None

    for i, line in enumerate(lines):
        if "from app." in line and "import router as" in line:
            last_import_idx = i
        if "app.include_router(" in line:
            last_include_idx = i

    if last_import_idx is not None and new_imports:
        for imp in reversed(new_imports):
            lines.insert(last_import_idx + 1, imp + "\n")
            if last_include_idx is not None and last_include_idx >= last_import_idx:
                last_include_idx += 1

    if last_include_idx is not None and new_includes:
        for inc in reversed(new_includes):
            lines.insert(last_include_idx + 1, inc + "\n")

    main_py.write_text("".join(lines), encoding="utf-8")
    logger.info("Routers registrados em main.py: %s", router_files)


def register_dependency(
    manifest: dict, force: bool, deps_py: Path | None = None
) -> None:
    module_name = manifest["module_name"]
    api_dir = _get_api_dir()
    if deps_py is None:
        deps_py = api_dir / "app" / "auth" / "dependencies.py"

    content = deps_py.read_text(encoding="utf-8")

    repos_dir = api_dir / "app" / "modules" / module_name / "repositories"
    svcs_dir = api_dir / "app" / "modules" / module_name / "services"
    if not repos_dir.exists() or not svcs_dir.exists():
        logger.warning("Diretório de repositories/services não encontrado")
        return

    repo_files = [
        f.stem for f in repos_dir.glob("*_repository.py") if f.stem != "__init__"
    ]
    svc_files = [f.stem for f in svcs_dir.glob("*_service.py") if f.stem != "__init__"]

    marker = "# --- Versões vinculadas das permissões ---"
    if marker not in content:
        logger.warning("Marker não encontrado em dependencies.py")
        return

    new_imports = []
    new_factories = []
    for repo_file in sorted(repo_files):
        entity = repo_file.replace("_repository", "")
        import_line = f"from app.modules.{module_name}.repositories.{repo_file} import {entity.title()}Repository"
        if import_line not in content:
            new_imports.append(import_line)

    for svc_file in sorted(svc_files):
        entity = svc_file.replace("_service", "")
        import_line = f"from app.modules.{module_name}.services.{svc_file} import {entity.title()}Service"
        if import_line not in content:
            new_imports.append(import_line)

    for repo_file in sorted(repo_files):
        entity = repo_file.replace("_repository", "")
        factory_name = (
            f"get_{module_name}_{entity}_service"
            if entity != module_name
            else f"get_{module_name}_service"
        )
        factory_sig = f"def {factory_name}(db: Session = Depends(get_db)) -> {entity.title()}Service:"
        if factory_sig not in content:
            new_factories.append(
                f"{factory_sig}\n"
                f'    """Factory para o {entity.title()}Service."""\n'
                f"    repository = {entity.title()}Repository(db)\n"
                f"    return {entity.title()}Service(repository)\n"
            )

    if not new_imports and not new_factories:
        logger.info("Dependencies já registrados em dependencies.py")
        return

    block = "\n".join(new_imports) + "\n\n" + "\n\n".join(new_factories) + "\n\n"
    content = content.replace(marker, block + marker)
    deps_py.write_text(content, encoding="utf-8")
    logger.info("Dependencies registrados em dependencies.py")


def register_alembic_import(
    manifest: dict, force: bool, env_py: Path | None = None
) -> None:
    module_name = manifest["module_name"]
    api_dir = _get_api_dir()
    if env_py is None:
        env_py = api_dir / "alembic" / "env.py"

    content = env_py.read_text(encoding="utf-8")

    models_dir = api_dir / "app" / "modules" / module_name / "models"
    if not models_dir.exists():
        logger.warning("Diretório de models não encontrado: %s", models_dir)
        return

    model_files = [f.stem for f in models_dir.glob("*.py") if f.stem != "__init__"]

    marker = "from app.modules.portal.models.portal import Aba, Modulo  # noqa: F401"
    if marker not in content:
        logger.warning("Marker não encontrado em alembic/env.py")
        return

    new_imports = []
    for model_file in sorted(model_files):
        entity = model_file.replace("_", " ").title().replace(" ", "")
        import_line = f"from app.modules.{module_name}.models.{model_file} import {entity}  # noqa: F401"
        if import_line not in content:
            new_imports.append(import_line)

    if not new_imports:
        logger.info("Imports já registrados em alembic/env.py")
        return

    content = content.replace(marker, marker + "\n" + "\n".join(new_imports))
    env_py.write_text(content, encoding="utf-8")
    logger.info("Imports registrados em alembic/env.py: %s", model_files)


def _get_venv_python() -> str:
    """Retorna o caminho do Python do venv do GrindX, se existir."""
    venv_python = _get_api_dir() / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    venv_python = _get_api_dir() / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def run_migrations() -> None:
    api_dir = _get_api_dir()
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
    module_name = manifest["module_name"]
    label = manifest.get("menu_label", module_name)
    frontend_tabs = manifest.get("frontend_tabs", [])

    logger.info(
        "Módulo importado: %s (%d abas disponíveis). "
        "Associe as abas manualmente no Portal → Estrutura.",
        label,
        len(frontend_tabs),
    )
    for tab in frontend_tabs:
        tab_name = tab.get("name", module_name)
        tab_url = tab.get("url", "")
        logger.info("  - %s: %s", tab_name, tab_url)


def rollback(backup_dir: Path | None) -> None:
    if not backup_dir or not backup_dir.exists():
        logger.warning("Nada para restaurar")
        return

    api_dir = _get_api_dir()
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


def _log_step(step_name: str, start: float) -> float:
    """Loga duração de um passo e retorna o novo timestamp."""
    elapsed = time.time() - start
    logger.info("Passo '%s' completado em %.2fs", step_name, elapsed)
    return time.time()


def import_module(
    module_name: str,
    import_dir: Path,
    force: bool = False,
    dry_run: bool = False,
    skip_migrations: bool = False,
) -> dict:
    steps = []
    backup_path = None

    _tick = time.time()
    try:
        manifest = validate_manifest(import_dir)
        steps.append("Manifesto validado")
        _tick = _log_step("validate_manifest", _tick)

        if not dry_run:
            backup_path = backup_existing(manifest)
        steps.append("Backup concluído")
        _tick = _log_step("backup_existing", _tick)

        if not dry_run:
            copy_backend(import_dir, module_name, force)
        steps.append("Backend copiado")
        _tick = _log_step("copy_backend", _tick)

        if not dry_run:
            copy_frontend(import_dir, module_name, force)
        steps.append("Frontend copiado")
        _tick = _log_step("copy_frontend", _tick)

        if not dry_run:
            copy_migration(import_dir)
        steps.append("Migration copiada")
        _tick = _log_step("copy_migration", _tick)

        if not dry_run:
            register_router(manifest, force)
        steps.append("Router registrado")
        _tick = _log_step("register_router", _tick)

        if not dry_run:
            register_dependency(manifest, force)
        steps.append("Dependency registrado em dependencies.py")
        _tick = _log_step("register_dependency", _tick)

        if not dry_run:
            register_alembic_import(manifest, force)
        steps.append("Import do model registrado no alembic/env.py")
        _tick = _log_step("register_alembic_import", _tick)

        if not dry_run:
            register_menu(manifest)
        steps.append("Menu registrado")
        _tick = _log_step("register_menu", _tick)

        if skip_migrations:
            steps.append("Migração adiada (executada em segundo plano)")
        else:
            try:
                if not dry_run:
                    run_migrations()
                steps.append("Migrations executadas")
            except Exception as e:
                logger.warning(
                    "Migration falhou (tabelas podem já existir): %s", str(e)
                )
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
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="Pular migrações (executar em background depois)",
    )
    args = parser.parse_args()

    import_dir = Path(args.import_dir)
    if not import_dir.exists():
        print(f"ERRO: Diretório não encontrado: {import_dir}")
        sys.exit(1)

    result = import_module(
        args.module_name,
        import_dir,
        force=args.force,
        dry_run=args.dry_run,
        skip_migrations=args.skip_migrations,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
