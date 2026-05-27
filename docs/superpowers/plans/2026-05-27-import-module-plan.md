# Importação de Módulos via UI — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow importing standalone modules by placing a `.zip` in `import/` folder and clicking a button in the frontend.

**Architecture:** Backend FastAPI router (`import_router.py`) exposes scan/import endpoints. An executor script (`scripts/import_module.py`) handles file copying, code registration, and migration. Frontend (`modules/importer/`) provides the UI. The `create-standalone-module` skill is updated to generate `module.json` and a `package` command.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, subprocess, zipfile, vanilla JS, structlog

---

### Task 1: Create `import/` directory and config setting

**Files:**
- Create: `D:\_Projetos\GrindX\import\` (empty directory)
- Modify: `packages/api-postgres/app/core/config.py`

- [ ] **Step 1: Create import directory**

```bash
mkdir D:\_Projetos\GrindX\import
```

- [ ] **Step 2: Add IMPORT_DIR config to Settings**

Edit `packages/api-postgres/app/core/config.py` to add:

```python
# --- Import de Módulos ---
IMPORT_DIR: str = ""
```

And add after the existing properties a computed default:

```python
@property
def import_dir_path(self) -> str:
    """Resolved import directory path."""
    if self.IMPORT_DIR:
        return self.IMPORT_DIR
    # Default: $MONOREPO_ROOT/import/
    return str(Path(__file__).resolve().parent.parent.parent.parent / "import")
```

- [ ] **Step 3: Add import at top of config.py**

```python
from pathlib import Path
```

- [ ] **Step 4: Commit**

```bash
git add packages/api-postgres/app/core/config.py && git commit -m "feat(import): add IMPORT_DIR config setting"
```

---

### Task 2: Create import executor script (`scripts/import_module.py`)

**Files:**
- Create: `packages/api-postgres/scripts/import_module.py`
- Test: (manual verification in Task 3)

This script handles the actual import. It is called as a subprocess by the API.

- [ ] **Step 1: Create `scripts/__init__.py`**

```bash
New-Item -ItemType File -Path "packages/api-postgres/scripts/__init__.py"
```

- [ ] **Step 2: Write `scripts/import_module.py`**

```python
"""
import_module.py — Importa um módulo empacotado em .zip para o GrindX.

Uso:
    python scripts/import_module.py projetos --import-dir=C:\tmp\extracted --force

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
    """Retorna a raiz do monorepo (GrindX/)."""
    return Path(__file__).resolve().parent.parent.parent.parent


def _get_import_dir() -> Path:
    """Retorna o diretório import/ na raiz do monorepo."""
    return _get_monorepo_root() / "import"


def validate_manifest(import_dir: Path) -> dict:
    """Valida e retorna o conteúdo do module.json."""
    manifest_path = import_dir / "module.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"module.json não encontrado em {import_dir}")

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    required = ["module_name", "entity_name", "schema_name", "route_prefix", "frontend_url", "menu_label"]
    missing = [k for k in required if k not in manifest]
    if missing:
        raise ValueError(f"Campos obrigatórios ausentes no module.json: {missing}")

    return manifest


def backup_existing(manifest: dict) -> Path | None:
    """Faz backup de main.py, dependencies.py e env.py."""
    api_dir = _get_monorepo_root() / "packages" / "api-postgres"
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
    """Copia app/modules/{module_name}/ para api-postgres."""
    src = import_dir / "app" / "modules" / module_name
    api_dir = _get_monorepo_root() / "packages" / "api-postgres"
    dest = api_dir / "app" / "modules" / module_name

    if not src.exists():
        logger.warning("Diretório backend não encontrado: %s", src)
        return

    if dest.exists():
        if not force:
            raise FileExistsError(f"Backend já existe em {dest}. Use --force para sobrescrever.")
        shutil.rmtree(dest)
        logger.info("Backend existente removido: %s", dest)

    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    logger.info("Backend copiado: %s -> %s", src, dest)


def copy_frontend(import_dir: Path, module_name: str, force: bool) -> None:
    """Copia frontend/ para frontend-webapp/modules/{module_name}/."""
    src = import_dir / "frontend"
    frontend_dir = _get_monorepo_root() / "packages" / "frontend-webapp"
    dest = frontend_dir / "modules" / module_name

    if not src.exists():
        logger.warning("Diretório frontend não encontrado: %s", src)
        return

    if dest.exists():
        if not force:
            raise FileExistsError(f"Frontend já existe em {dest}. Use --force para sobrescrever.")
        shutil.rmtree(dest)
        logger.info("Frontend existente removido: %s", dest)

    shutil.copytree(src, dest)
    logger.info("Frontend copiado: %s -> %s", src, dest)


def copy_migration(import_dir: Path) -> None:
    """Copia migration/*.py para alembic/versions/."""
    src_dir = import_dir / "migration"
    api_dir = _get_monorepo_root() / "packages" / "api-postgres"
    dest_dir = api_dir / "alembic" / "versions"

    if not src_dir.exists():
        logger.warning("Diretório migration não encontrado: %s", src_dir)
        return

    for f in src_dir.glob("*.py"):
        dest_path = dest_dir / f.name
        if dest_path.exists():
            logger.warning("Migration já existe, sobrescrevendo: %s", dest_path)
        shutil.copy2(f, dest_path)
        logger.info("Migration copiada: %s -> %s", f, dest_path)


def register_router(manifest: dict, force: bool) -> None:
    """Adiciona import + include_router no main.py."""
    module_name = manifest["module_name"]
    api_dir = _get_monorepo_root() / "packages" / "api-postgres"
    main_py = api_dir / "app" / "main.py"

    content = main_py.read_text(encoding="utf-8")

    import_line = f"from app.routers.{module_name}_router import router as {module_name}_router"
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

    if last_import_idx is not None and import_line not in content:
        lines.insert(last_import_idx + 1, import_line + "\n")
        last_include_idx = last_include_idx + 1 if last_include_idx and last_include_idx >= last_import_idx else last_include_idx

    if last_include_idx is not None and register_line not in content:
        lines.insert(last_include_idx + 1, register_line + "\n")

    main_py.write_text("".join(lines), encoding="utf-8")
    logger.info("Router registrado em main.py")


def register_alembic_import(manifest: dict, force: bool) -> None:
    """Adiciona import do model no alembic/env.py."""
    module_name = manifest["module_name"]
    entity_name = manifest["entity_name"]
    api_dir = _get_monorepo_root() / "packages" / "api-postgres"
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
        logger.warning("Marker não encontrado em alembic/env.py. Adicione manualmente: %s", import_line)


def run_migrations() -> None:
    """Executa alembic upgrade head via subprocess."""
    api_dir = _get_monorepo_root() / "packages" / "api-postgres"
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=api_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Migration falhou:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
    logger.info("Migrations executadas com sucesso")


def register_menu(manifest: dict) -> None:
    """Registra o módulo na tabela portal_modulos."""
    module_name = manifest["module_name"]
    label = manifest.get("menu_label", module_name)
    url = manifest.get("frontend_url", f"modules/{module_name}/index.html")
    icone = manifest.get("menu_icone", "folder")
    slug = module_name

    api_dir = _get_monorepo_root() / "packages" / "api-postgres"

    # Need to find the Principal aba_id (first Aba with nome=Principal or id=1)
    result = subprocess.run(
        [sys.executable, "-c", f"""
import sys
sys.path.insert(0, r"{api_dir}")
from app.database import SessionLocal
from app.models.portal import Aba, Modulo

with SessionLocal() as db:
    aba = db.query(Aba).filter(Aba.nome.ilike("%principal%")).first()
    if not aba:
        aba = db.query(Aba).order_by(Aba.id).first()
    if not aba:
        print("ERROR: nenhuma aba encontrada")
        sys.exit(1)

    existing = db.query(Modulo).filter(Modulo.slug == "{slug}").first()
    if existing:
        print(f"EXISTS:{{existing.id}}")
    else:
        mod = Modulo(aba_id=aba.id, nome="{label}", slug="{slug}", url="{url}", icone="{icone}")
        db.add(mod)
        db.commit()
        print(f"OK:{{mod.id}}")
"""],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        logger.warning("Registro no menu falhou: %s", result.stderr)
    else:
        logger.info("Menu registrado: %s", result.stdout.strip())


def rollback(backup_dir: Path | None) -> None:
    """Restaura arquivos do backup em caso de erro."""
    if not backup_dir or not backup_dir.exists():
        logger.warning("Nada para restaurar")
        return

    api_dir = _get_monorepo_root() / "packages" / "api-postgres"
    restored = 0
    for f in backup_dir.iterdir():
        dest = api_dir / "app" / f.name
        if f.name == "env.py":
            dest = api_dir / "alembic" / "env.py"
        shutil.copy2(f, dest)
        restored += 1
        logger.info("Restaurado: %s -> %s", f, dest)

    logger.info("Rollback concluído: %d arquivos restaurados", restored)


def import_module(module_name: str, import_dir: Path, force: bool = False, dry_run: bool = False) -> dict:
    """Executa o fluxo completo de importação."""
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
    parser.add_argument("--import-dir", required=True, help="Diretório com o conteúdo extraído do .zip")
    parser.add_argument("--force", action="store_true", help="Sobrescrever módulo existente")
    parser.add_argument("--dry-run", action="store_true", help="Apenas simular")
    args = parser.parse_args()

    import_dir = Path(args.import_dir)
    if not import_dir.exists():
        print(f"ERRO: Diretório não encontrado: {import_dir}")
        sys.exit(1)

    result = import_module(args.module_name, import_dir, force=args.force, dry_run=args.dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Commit**

```bash
git add packages/api-postgres/scripts/ && git commit -m "feat(import): add import_module.py executor script"
```

---

### Task 3: Create import router (`import_router.py`)

**Files:**
- Create: `packages/api-postgres/app/routers/import_router.py`
- Modify: `packages/api-postgres/app/main.py`
- Test: `packages/api-postgres/tests/unit/test_import_router.py`

- [ ] **Step 1: Write `import_router.py`**

```python
"""
import_router.py — Endpoints para importação de módulos via UI.

Permite escanear a pasta import/ por .zips com module.json e
importar módulos completos (backend + frontend + migration + registro).
"""

import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from shared.schemas.base import ErrorResponse
from shared.security.permissions import Role
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.core.config import settings
from app.database import get_db
from app.models.portal import Modulo

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/import", tags=["Importação de Módulos"])


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
    """Lê module.json de dentro de um .zip sem extrair."""
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            if "module.json" in zf.namelist():
                with zf.open("module.json") as f:
                    return json.loads(f.read().decode("utf-8"))
    except Exception as e:
        logger.warning("Erro ao ler %s: %s", zip_path, e)
    return None


@router.get("/scan", response_model=ScanResponse, summary="Escaneia zips disponíveis")
def scan_imports(
    db: Session = Depends(get_db),
    _: None = Depends(require_role(Role.ADMIN)),
):
    """Escaneia a pasta import/ e retorna lista de módulos disponíveis."""
    import_dir = _get_import_dir()
    if not import_dir.exists():
        return ScanResponse(modules=[])

    existing_slugs = {m.slug for m in db.query(Modulo).all()}
    modules = []

    for zip_path in sorted(import_dir.glob("*.zip")):
        manifest = _read_manifest_from_zip(zip_path)
        if not manifest:
            continue

        slug = manifest.get("module_name", zip_path.stem)
        modules.append(
            ModuleInfo(
                slug=slug,
                module_name=manifest.get("module_name", slug),
                entity_name=manifest.get("entity_name", ""),
                version=manifest.get("version", "0.0.0"),
                menu_label=manifest.get("menu_label", slug),
                schema_name=manifest.get("schema_name", "org"),
                ja_importado=slug in existing_slugs,
            )
        )

    return ScanResponse(modules=modules)


@router.post("/{module_name}", response_model=ImportResult, summary="Importa um módulo")
def import_module(
    module_name: str,
    force: bool = Query(False, description="Sobrescrever módulo existente"),
    db: Session = Depends(get_db),
    _: None = Depends(require_role(Role.ADMIN)),
):
    """Importa um módulo .zip para o sistema."""
    import_dir = _get_import_dir()

    # Find the zip
    zip_path = import_dir / f"{module_name}.zip"
    if not zip_path.exists():
        # Try glob for any zip containing the name
        matches = list(import_dir.glob(f"*{module_name}*.zip"))
        if not matches:
            raise HTTPException(404, f"Arquivo .zip não encontrado para o módulo: {module_name}")
        zip_path = matches[0]

    # Extract to temp dir
    try:
        tmp_dir = Path(tempfile.mkdtemp(prefix=f"grindx_import_{module_name}_"))
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_dir)

        logger.info("Zip extraído para %s", tmp_dir)

        # Validate manifest exists
        manifest_path = tmp_dir / "module.json"
        if not manifest_path.exists():
            raise HTTPException(422, f"module.json não encontrado dentro do .zip: {zip_path.name}")

        # Call executor script as subprocess
        script_path = Path(__file__).resolve().parent.parent.parent / "scripts" / "import_module.py"
        cmd = [
            sys.executable,
            str(script_path),
            module_name,
            f"--import-dir={tmp_dir}",
        ]
        if force:
            cmd.append("--force")

        logger.info("Executando subprocesso: %s", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # Parse result
        try:
            result_data = json.loads(result.stdout.strip())
        except (json.JSONDecodeError, ValueError):
            result_data = {"success": False, "steps": [], "error": result.stderr or result.stdout}

        # Log subprocess output
        if result.stderr:
            for line in result.stderr.strip().split("\n"):
                logger.warning("[import subprocess] %s", line)

        return ImportResult(
            success=result_data.get("success", False),
            message="Módulo importado com sucesso" if result_data.get("success") else "Falha na importação",
            steps=result_data.get("steps", []),
            error=result_data.get("error"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro ao importar módulo")
        raise HTTPException(500, f"Erro interno: {str(e)}")
    finally:
        # Cleanup temp dir
        if "tmp_dir" in dir() and tmp_dir and tmp_dir.exists():
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
```

- [ ] **Step 2: Register router in main.py**

Edit `packages/api-postgres/app/main.py`:

Add import:
```python
from app.routers.import_router import router as import_router
```

Add after `app.include_router(theme_router)`:
```python
app.include_router(import_router)
```

- [ ] **Step 3: Write unit test for import_router**

Create `packages/api-postgres/tests/unit/test_import_router.py`:

```python
"""Tests for the import router endpoints."""

import json
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


class TestScanEndpoint:
    def test_scan_sem_pasta_import_retorna_vazio(self, client: TestClient, auth_headers: dict):
        response = client.get("/v1/import/scan", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["modules"] == []

    def test_scan_sem_manifest_ignora_zip(self, client: TestClient, auth_headers: dict, tmp_path: Path, monkeypatch):
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("some_file.txt", "content")

        monkeypatch.setattr("app.routers.import_router._get_import_dir", lambda: tmp_path)
        response = client.get("/v1/import/scan", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["modules"] == []

    def test_scan_com_manifest_retorna_modulo(self, client: TestClient, auth_headers: dict, tmp_path: Path, monkeypatch):
        manifest = {
            "module_name": "projetos", "entity_name": "Projeto",
            "version": "1.0.0", "schema_name": "org", "menu_label": "Projetos",
        }
        zip_path = tmp_path / "projetos.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("module.json", json.dumps(manifest))

        monkeypatch.setattr("app.routers.import_router._get_import_dir", lambda: tmp_path)
        response = client.get("/v1/import/scan", headers=auth_headers)
        assert response.status_code == 200
        modules = response.json()["modules"]
        assert len(modules) == 1
        assert modules[0]["module_name"] == "projetos"
        assert modules[0]["ja_importado"] is False

    def test_scan_requer_autenticacao(self, client: TestClient):
        response = client.get("/v1/import/scan")
        assert response.status_code == 401


class TestImportEndpoint:
    def test_import_zip_inexistente_retorna_404(self, client: TestClient, auth_headers: dict):
        response = client.post("/v1/import/modulo_inexistente", headers=auth_headers)
        assert response.status_code == 404

    def test_import_zip_sem_manifest_retorna_422(self, client: TestClient, auth_headers: dict, tmp_path: Path, monkeypatch):
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("random.txt", "content")

        monkeypatch.setattr("app.routers.import_router._get_import_dir", lambda: tmp_path)
        response = client.post("/v1/import/test", headers=auth_headers)
        assert response.status_code == 422

    def test_import_requer_autenticacao(self, client: TestClient):
        response = client.post("/v1/import/test")
        assert response.status_code == 401
```

- [ ] **Step 4: Run unit tests to verify**

Run: `pytest packages/api-postgres/tests/unit/test_import_router.py -v`
Expected: tests PASS

- [ ] **Step 5: Commit**

```bash
git add packages/api-postgres/app/routers/import_router.py packages/api-postgres/app/main.py packages/api-postgres/tests/unit/test_import_router.py && git commit -m "feat(import): add import_router with scan and import endpoints"
```

---

### Task 4: Create frontend module `modules/importer/`

**Files:**
- Create: `packages/frontend-webapp/modules/importer/index.html`
- Create: `packages/frontend-webapp/modules/importer/script.js`
- Create: `packages/frontend-webapp/modules/importer/style.css`

- [ ] **Step 1: Write `index.html`**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Importar Módulos — GrindX</title>
    <link rel="stylesheet" href="../../shared/core.css">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="page-container">
        <div class="page-header">
            <h1 id="pageTitle">Importar Módulos</h1>
            <button class="btn btn-primary" id="btnRefresh">⟳ Atualizar</button>
        </div>
        <div id="dataTableContainer"></div>
    </div>

    <div class="modal-overlay hidden" id="importModal">
        <div class="modal">
            <div class="modal-header">
                <h2 id="modalTitle">Importar Módulo</h2>
                <button type="button" class="modal-close" id="btnModalClose">&times;</button>
            </div>
            <div class="modal-body" id="modalBody"></div>
            <div class="modal-footer">
                <button class="btn btn-secondary" id="btnCancel">Cancelar</button>
                <button class="btn btn-primary" id="btnConfirm">Importar</button>
            </div>
        </div>
    </div>

    <script src="../../shared/app.js"></script>
    <script src="../../shared/apiService.js"></script>
    <script src="../../shared/components/LoadingSpinner.js"></script>
    <script src="../../shared/components/DataTable.js"></script>
    <script src="../../shared/components/ReusableModal.js"></script>
    <script src="../../shared/baseController.js"></script>
    <script src="script.js"></script>
</body>
</html>
```

- [ ] **Step 2: Write `script.js`**

```javascript
class ImporterController extends window.grindx.controllers.BaseController {
    constructor() {
        super();
        this.dataTable = null;
        this.importModal = null;
        this.currentSlug = null;
        this.init();
    }

    async init() {
        if (!this.requireAuth()) return;
        this.importModal = new window.grindx.components.ReusableModal('importModal');
        this.dataTable = new window.grindx.components.DataTable('dataTableContainer', {
            columns: [
                { key: 'module_name', label: 'Módulo' },
                { key: 'version', label: 'Versão', width: '80px' },
                { key: 'schema_name', label: 'Schema', width: '100px' },
                { key: 'menu_label', label: 'Menu', width: '120px' },
                {
                    key: 'ja_importado', label: 'Status', width: '120px',
                    render: (v) => v ? '<span class="badge badge-success">Importado</span>' : '<span class="badge badge-info">Novo</span>'
                },
                {
                    key: 'acoes', label: 'Ações', width: '140px',
                    render: (v, row) => {
                        if (row.ja_importado) {
                            return `<button class="btn btn-sm btn-warning" data-action="reimport" data-slug="${row.slug}">Reimportar</button>`;
                        }
                        return `<button class="btn btn-sm btn-primary" data-action="import" data-slug="${row.slug}">Importar</button>`;
                    }
                }
            ],
        });
        this.bindEvents();
        await this.carregar();
    }

    bindEvents() {
        document.getElementById('btnRefresh').addEventListener('click', () => this.carregar());
        document.getElementById('btnConfirm').addEventListener('click', () => this.confirmarImport());
        document.getElementById('btnCancel').addEventListener('click', () => this.importModal.close());
        document.getElementById('btnModalClose').addEventListener('click', () => this.importModal.close());

        document.getElementById('dataTableContainer').addEventListener('click', (e) => {
            const btn = e.target.closest('[data-action]');
            if (!btn) return;
            const slug = btn.dataset.slug;
            const action = btn.dataset.action;
            if (action === 'import' || action === 'reimport') {
                this.abrirModal(slug, action === 'reimport');
            }
        });
    }

    async carregar() {
        try {
            const data = await window.grindx.api.get('/v1/import/scan');
            this.dataTable.render(data.modules || []);
        } catch (err) {
            this.toastError(err);
        }
    }

    abrirModal(slug, isReimport) {
        this.currentSlug = slug;
        const body = document.getElementById('modalBody');
        body.innerHTML = `
            <p><strong>Módulo:</strong> ${slug}</p>
            <p>${isReimport ? 'O módulo já existe. Reimportar sobrescreverá os arquivos atuais.' : 'Confirme para importar este módulo.'}</p>
            <div id="importLog" class="import-log hidden"></div>
        `;
        document.getElementById('modalTitle').textContent = isReimport ? 'Reimportar Módulo' : 'Importar Módulo';
        document.getElementById('btnConfirm').textContent = isReimport ? 'Reimportar' : 'Importar';
        this.importModal.open();
    }

    async confirmarImport() {
        const btn = document.getElementById('btnConfirm');
        const logDiv = document.getElementById('importLog');
        btn.disabled = true;
        btn.textContent = 'Importando...';
        logDiv.classList.remove('hidden');
        logDiv.innerHTML = '<div class="loading-spinner"></div>';

        try {
            const isReimport = btn.textContent === 'Reimportar';
            const result = await window.grindx.api.post(`/v1/import/${this.currentSlug}?force=${isReimport}`);

            logDiv.innerHTML = '';
            const steps = result.steps || [];
            steps.forEach(step => {
                const div = document.createElement('div');
                div.className = result.success ? 'log-step success' : 'log-step error';
                div.textContent = result.success ? `✓ ${step}` : `✗ ${step}`;
                logDiv.appendChild(div);
            });

            if (result.success) {
                logDiv.innerHTML += '<div class="log-step success" style="font-weight:bold">✅ Módulo importado com sucesso!</div>';
                setTimeout(() => {
                    this.importModal.close();
                    this.carregar();
                }, 1500);
            } else {
                logDiv.innerHTML += `<div class="log-step error" style="font-weight:bold">❌ ${result.error || 'Falha na importação'}</div>`;
                btn.disabled = false;
                btn.textContent = isReimport ? 'Reimportar' : 'Importar';
            }
        } catch (err) {
            logDiv.innerHTML = `<div class="log-step error" style="font-weight:bold">❌ ${err.message}</div>`;
            btn.disabled = false;
            btn.textContent = 'Importar';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ImporterController();
});
```

- [ ] **Step 3: Write `style.css`**

```css
@import url('../../shared/core.css');

.page-container { padding: var(--space-6); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-6); }

.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }
.badge-success { background: var(--color-success-bg, #d4edda); color: var(--color-success-text, #155724); }
.badge-info { background: var(--color-info-bg, #d1ecf1); color: var(--color-info-text, #0c5460); }

.modal-body { padding: var(--space-4) 0; }
.modal-footer { display: flex; justify-content: flex-end; gap: var(--space-2); padding-top: var(--space-4); border-top: 1px solid var(--color-border, #ddd); }

.import-log { margin-top: var(--space-4); max-height: 300px; overflow-y: auto; }
.log-step { padding: var(--space-1) var(--space-2); border-radius: 4px; margin-bottom: 4px; font-size: 0.9em; }
.log-step.success { background: var(--color-success-bg, #d4edda); color: var(--color-success-text, #155724); }
.log-step.error { background: var(--color-error-bg, #f8d7da); color: var(--color-error-text, #721c24); }
```

- [ ] **Step 4: Commit**

```bash
git add packages/frontend-webapp/modules/importer/ && git commit -m "feat(import): add frontend importer module with scan UI"
```

---

### Task 5: Update `create-standalone-module` skill to generate `module.json`

**Files:**
- Modify: `.opencode/skills/create-standalone-module/SKILL.md` (if editable as template)

Note: The `create-standalone-module` skill is referenced but the actual skill file is at `C:\Users\Alex\.config\opencode\skills\create-standalone-module\SKILL.md`. The templates are inline in the SKILL.md. We need to add:

1. A `module.json` template section
2. A `package` command in the `export.py` template

- [ ] **Step 1: Add module.json template to the skill**

Add new section after the Support Files section and before Registration Checklist:

````markdown
## 7. Manifesto (`module.json`)

Adicionar na raiz do standalone o arquivo `module.json` com os metadados do módulo:

```json
{
  "module_name": "{module_name}",
  "entity_name": "{entity_name}",
  "version": "1.0.0",
  "schema_name": "{schema_name}",
  "table_name": "{table_name}",
  "route_prefix": "{route_prefix}",
  "route_tag": "{route_tag}",
  "frontend_url": "{frontend_path}/index.html",
  "menu_label": "{menu_label}",
  "menu_icone": "folder",
  "role_minima": "operador",
  "dependencies": []
}
```

Incluir `module.json` no diretório standalone e no `.zip` gerado pelo comando `package`.
````

- [ ] **Step 2: Add `package` command to export.py template**

Edit the `export.py` section, adding before the `if __name__ == "__main__":` block:

```python
def package(dry_run: bool = False):
    """Empacota o módulo em um .zip com module.json para distribuição."""
    import zipfile

    module_dir = MODULE_SRC
    frontend_dir = FRONTEND_SRC
    migration_dir = MIGRATION_SRC
    dist_dir = module_dir.parent.parent.parent.parent.parent / "dist"
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
        # Add module.json from module root
        manifest_path = MODULE_SRC.parent / "module.json"
        if manifest_path.exists():
            zf.write(manifest_path, "module.json")

        # Add backend files
        for file in MODULE_SRC.rglob("*"):
            if file.is_file() and "__pycache__" not in file.parts and not file.name.endswith(".pyc"):
                arcname = file.relative_to(MODULE_SRC.parent.parent.parent.parent.parent)
                zf.write(file, arcname)

        # Add frontend files
        if frontend_dir.exists():
            for file in frontend_dir.rglob("*"):
                if file.is_file():
                    arcname = Path("frontend") / file.relative_to(frontend_dir)
                    zf.write(file, arcname)

        # Add migration files
        if migration_dir.exists():
            for file in migration_dir.glob("*.py"):
                zf.write(file, f"migration/{file.name}")

    logger.info("Pacote criado: %s", zip_path)
```

And update the CLI to add `package` as a subcommand:

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(...)
    subparsers = parser.add_subparsers(dest="command")

    # export command
    export_parser = subparsers.add_parser("export", help="Exporta para o GrindX")
    ...

    # package command
    pkg_parser = subparsers.add_parser("package", help="Empacota como .zip")

    args = parser.parse_args()
    if args.command == "package":
        package()
    elif args.command == "export":
        export(dry_run=args.dry_run)
```

- [ ] **Step 3: Commit**

```bash
git add .opencode/skills/create-standalone-module/SKILL.md && git commit -m "feat(skill): add module.json and package command to create-standalone-module"
```

---

### Self-Review

**1. Spec coverage:**
- Task 1: Config + import directory ✓
- Task 2: import_module.py (executor with backup, copy, register, migrate, rollback) ✓
- Task 3: import_router.py (scan + import endpoints) + main.py registration + tests ✓
- Task 4: Frontend modules/importer/ ✓
- Task 5: create-standalone-module skill updates (module.json + package) ✓

**2. Placeholder scan:** No "TBD", "TODO", or placeholder patterns found.

**3. Type consistency:** All method/function signatures match across tasks. `import_module()` in both `import_router.py` (endpoint) and `import_module.py` (script) have distinct contexts. `_get_import_dir()` used consistently.
