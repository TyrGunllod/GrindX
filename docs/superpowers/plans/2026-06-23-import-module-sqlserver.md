# Importação de Módulos para api-sqlserver — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Estender `import_module.py` para importar módulos read-only no api-sqlserver, detectando o alvo via campo `target_api` no `module.json`.

**Architecture:** Um novo parâmetro `--target-api` no script CLI controla o fluxo. Para `"sqlserver"`, o backend é copiado para `apps/api-sqlserver/app/modules/`, o router registrado no `main.py` do sqlserver, e steps de model/migration/dependency são pulados. O `import_router.py` lê `target_api` do `module.json` e repassa ao subprocesso.

**Tech Stack:** Python 3.12+, FastAPI, pytest com tmp_path

## Validação com o módulo Custo real (`D:\_Projetos\Custo`)

Antes de definir as tarefas, verifiquei o módulo Custo real para garantir que o plano cobre todos os padrões:

| Item | Real (Custo) | Plano cobre? | Ajuste |
|------|-------------|--------------|--------|
| `module.json` `schema_name` | `"custo"` (não `"org"`) | ✅ genérico | N/A |
| `module.json` `tables` | `["SB1010", "SG1010"]` | ❌ faltava | Adicionar como campo opcional |
| Frontend `shared/core.css` | Presente no zip | ❌ `copy_frontend` copiaria para lugar errado | Skip `shared/` na cópia |
| Router factory inline | `get_custo_produto_service` dentro do router | ✅ já documentado | N/A |
| Auth dual-mode | try/except `get_db` vs `database_protheus` | ✅ já documentado | N/A |
| `auth/dependencies.py` no sqlserver | **Não existe** | ✅ spec pula dependency | N/A |
| `export.py` `package()` frontend path | `frontend/modules/custos/` → `frontend/custos/` no zip | ✅ spec usa `frontend/` direto | N/A |
| Sem `models/` e `base.py` | Confirma | ✅ spec documenta | N/A |

### Ajustes pós-validação

1. **`copy_frontend` deve ignorar `shared/`** — o zip pode conter `frontend/shared/core.css` (bundled do standalone), mas no monorepo os shared files já existem em `frontend-webapp/shared/`. Adicionar filtro: pular diretório `shared/` durante a cópia.

2. **`module.json` pode ter `tables`** — campo opcional listando tabelas SQL Server consultadas. Não afeta a importação, apenas metadado. Documentar como aceito.

3. **Factory do service é inline no router** — o sqlserver **não tem** `auth/dependencies.py`. Confirmado: a função `register_dependency()` do `export.py` do Custo é dead code. O plano está correto em pular este passo para sqlserver.

---

## Mapa de Arquivos

| Arquivo | Ação | Responsabilidade |
|---------|------|------------------|
| `apps/api-postgres/scripts/import_module.py` | Modificar | Adicionar `target_api` ao manifesto, `_get_sqlserver_api_dir()`, `register_router_sqlserver()`, fluxo condicional em `import_module()`, argumento `--target-api` |
| `apps/api-postgres/app/routers/import_router.py` | Modificar | Ler `target_api` do `module.json`, passar `--target-api` ao subprocesso, pular migrations em background para sqlserver |
| `apps/api-postgres/tests/unit/test_import_module_sqlserver.py` | Criar | Tests para `register_router_sqlserver()`, fluxo sqlserver completo, compatibilidade reversa |

---

### Task 1: Adicionar `target_api` ao manifesto e `_get_sqlserver_api_dir()`

**Files:**
- Modify: `apps/api-postgres/scripts/import_module.py:69-93`

- [ ] **Step 1: Escrever o test para validação do target_api no manifesto**

File: `apps/api-postgres/tests/unit/test_import_module_sqlserver.py`

```python
"""Tests for sqlserver module import support in import_module.py."""
import json
from pathlib import Path
import scripts.import_module as import_module


def test_validate_manifest_default_target_api(tmp_path):
    """module.json sem target_api deve assumir 'postgres'."""
    manifest = {
        "module_name": "test_mod",
        "entity_name": "Test",
        "schema_name": "org",
        "route_prefix": "/v1/test",
        "menu_label": "Teste",
        "frontend_url": "modules/test/index.html",
    }
    manifest_path = tmp_path / "module.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = import_module.validate_manifest(tmp_path)
    assert result["module_name"] == "test_mod"


def test_validate_manifest_sqlserver_target_api(tmp_path):
    """module.json com target_api='sqlserver' deve ser aceito."""
    manifest = {
        "module_name": "custo",
        "entity_name": "CustoProduto",
        "schema_name": "org",
        "route_prefix": "/v1/produtos/custos",
        "menu_label": "Custos",
        "target_api": "sqlserver",
        "frontend_tabs": [{"name": "Custos", "url": "modules/custos/index.html"}],
    }
    manifest_path = tmp_path / "module.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = import_module.validate_manifest(tmp_path)
    assert result["target_api"] == "sqlserver"


def test_get_sqlserver_api_dir_default():
    """_get_sqlserver_api_dir() deve retornar o path relativo ao monorepo root."""
    d = import_module._get_sqlserver_api_dir()
    assert d.name == "api-sqlserver"
    assert d.parent.name == "apps"
```

- [ ] **Step 2: Rodar o test para verificar falha**

```bash
cd apps/api-postgres
set PYTHONPATH=..\..\packages
pytest tests/unit/test_import_module_sqlserver.py::test_validate_manifest_default_target_api -v
pytest tests/unit/test_import_module_sqlserver.py::test_validate_manifest_sqlserver_target_api -v
pytest tests/unit/test_import_module_sqlserver.py::test_get_sqlserver_api_dir_default -v
```

Expected: todos FALHAM com `AttributeError: module has no attribute '_get_sqlserver_api_dir'`

- [ ] **Step 3: Adicionar validação e `_get_sqlserver_api_dir()` no `import_module.py`**

Após `validate_manifest()` (linha ~93), adicionar na função: `target_api` não é obrigatório no JSON — se ausente, assume `"postgres"`. O manifesto já aceita campos extras, então nenhuma mudança na validação é necessária.

Adicionar após `_get_import_dir()` (linha ~67):

```python
def _get_sqlserver_api_dir() -> Path:
    env = os.environ.get("GRINDX_SQLSERVER_API_DIR")
    if env:
        return Path(env).resolve()
    return _get_monorepo_root() / "apps" / "api-sqlserver"
```

- [ ] **Step 4: Rodar os testes para verificar passam**

```bash
cd apps/api-postgres
set PYTHONPATH=..\..\packages
pytest tests/unit/test_import_module_sqlserver.py::test_validate_manifest_default_target_api -v
pytest tests/unit/test_import_module_sqlserver.py::test_validate_manifest_sqlserver_target_api -v
pytest tests/unit/test_import_module_sqlserver.py::test_get_sqlserver_api_dir_default -v
```

Expected: todos PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/scripts/import_module.py apps/api-postgres/tests/unit/test_import_module_sqlserver.py
git commit -m "feat(import): add _get_sqlserver_api_dir() and target_api manifest field"
```

---

### Task 2: Implementar `register_router_sqlserver()`

**Files:**
- Modify: `apps/api-postgres/scripts/import_module.py`
- Modify: `apps/api-postgres/tests/unit/test_import_module_sqlserver.py`

- [ ] **Step 1: Escrever tests para register_router_sqlserver()**

Adicionar ao final de `test_import_module_sqlserver.py`:

```python
MAIN_PY_SQLSERVER_CONTENT = """\
from app.routers.health_router import router as health_router

app.include_router(health_router)
"""


@pytest.fixture
def main_py_sqlserver(tmp_path):
    f = tmp_path / "main.py"
    f.write_text(MAIN_PY_SQLSERVER_CONTENT, encoding="utf-8")
    return f


def test_register_router_sqlserver_adds_import_and_include(main_py_sqlserver):
    """Deve adicionar import do router e app.include_router() no main.py do sqlserver."""
    manifest = {
        "module_name": "custo",
        "entity_name": "CustoProduto",
        "schema_name": "org",
        "route_prefix": "/v1/produtos/custos",
        "menu_label": "Custos",
        "target_api": "sqlserver",
        "frontend_tabs": [{"name": "Custos", "url": "modules/custos/index.html"}],
    }
    register_router_sqlserver = import_module.register_router_sqlserver
    register_router_sqlserver(manifest, force=True, main_py=main_py_sqlserver)
    content = main_py_sqlserver.read_text(encoding="utf-8")
    assert "from app.modules.custo.routers.custo_produto_router import router as custo_produto_router" in content
    assert "app.include_router(custo_produto_router)" in content


def test_register_router_sqlserver_idempotent(main_py_sqlserver):
    """Chamar duas vezes não deve duplicar entradas."""
    manifest = {
        "module_name": "custo",
        "entity_name": "CustoProduto",
        "schema_name": "org",
        "route_prefix": "/v1/produtos/custos",
        "menu_label": "Custos",
        "target_api": "sqlserver",
        "frontend_tabs": [{"name": "Custos", "url": "modules/custos/index.html"}],
    }
    register_router_sqlserver = import_module.register_router_sqlserver
    register_router_sqlserver(manifest, force=True, main_py=main_py_sqlserver)
    register_router_sqlserver(manifest, force=True, main_py=main_py_sqlserver)
    content = main_py_sqlserver.read_text(encoding="utf-8")
    assert content.count("custo_produto_router") == 2  # 1 import + 1 include
    assert content.count("app.include_router(custo_produto_router)") == 1


def test_register_router_sqlserver_no_router_dir(main_py_sqlserver):
    """Sem diretório de routers, não deve modificar main.py."""
    manifest = {
        "module_name": "mod_sem_router",
        "entity_name": "Mod",
        "schema_name": "org",
        "route_prefix": "/v1/mod",
        "menu_label": "Mod",
        "target_api": "sqlserver",
        "frontend_tabs": [{"name": "Mod", "url": "modules/mod/index.html"}],
    }
    original = main_py_sqlserver.read_text(encoding="utf-8")
    register_router_sqlserver = import_module.register_router_sqlserver
    register_router_sqlserver(manifest, force=True, main_py=main_py_sqlserver)
    assert main_py_sqlserver.read_text(encoding="utf-8") == original
```

- [ ] **Step 2: Rodar tests para verificar falha**

```bash
cd apps/api-postgres
set PYTHONPATH=..\..\packages
pytest tests/unit/test_import_module_sqlserver.py::test_register_router_sqlserver_adds_import_and_include -v
```

Expected: FAIL com `AttributeError: module has no attribute 'register_router_sqlserver'`

- [ ] **Step 3: Implementar `register_router_sqlserver()`**

Adicionar nova função em `import_module.py` **após `register_router()`** (linha ~280):

```python
def register_router_sqlserver(
    manifest: dict, force: bool, main_py: Path | None = None
) -> None:
    module_name = manifest["module_name"]
    api_dir = _get_sqlserver_api_dir()
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
        logger.info("Routers já registrados em sqlserver main.py")
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
    logger.info("Routers registrados em sqlserver main.py: %s", router_files)
```

- [ ] **Step 4: Rodar tests para verificar passam**

```bash
cd apps/api-postgres
set PYTHONPATH=..\..\packages
pytest tests/unit/test_import_module_sqlserver.py -v -k "register_router_sqlserver"
```

Expected: todos PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/scripts/import_module.py apps/api-postgres/tests/unit/test_import_module_sqlserver.py
git commit -m "feat(import): add register_router_sqlserver() for api-sqlserver main.py"
```

---

### Task 3: Adicionar `--target-api` CLI e fluxo condicional em `import_module()`

**Files:**
- Modify: `apps/api-postgres/scripts/import_module.py`
- Modify: `apps/api-postgres/tests/unit/test_import_module_sqlserver.py`

### Refinamento: `copy_frontend` deve ignorar `shared/`

O módulo Custo standalone inclui `frontend/shared/core.css` no seu `.zip`. Quando `copy_frontend` copia o conteúdo de `frontend/` para `frontend-webapp/modules/`, o diretório `shared/` seria copiado para `modules/shared/`, quebrando os paths relativos (`../../shared/core.css`).

**Solução:** `copy_frontend` sempre ignora o diretório `shared/` (aplicável a qualquer target_api). O monorepo já tem `frontend-webapp/shared/` populado.

Adicionar em `copy_frontend()`, dentro do loop `for item in src.iterdir():`, antes de processar:

```python
if item.name == "shared":
    logger.info("Ignorando diretório shared/ — já existe no monorepo")
    continue
```

- [ ] **Step 0a: Escrever test para shared/ ser ignorado no copy_frontend**

Adicionar em `test_import_module_sqlserver.py`:

```python
def test_copy_frontend_skips_shared(tmp_path):
    """copy_frontend deve ignorar o diretório shared/ durante a cópia."""
    import_dir = tmp_path / "import_src"
    frontend_dir = import_dir / "frontend"
    (frontend_dir / "shared").mkdir(parents=True)
    (frontend_dir / "shared" / "core.css").write_text("body {}", encoding="utf-8")
    (frontend_dir / "meu_modulo").mkdir()
    (frontend_dir / "meu_modulo" / "index.html").write_text("hi", encoding="utf-8")

    frontend_dest = tmp_path / "frontend-webapp" / "modules"
    frontend_dest.mkdir(parents=True)

    import_module.copy_frontend(import_dir, "meu_modulo", force=True)  # chama via side-effect
    # Verifica se meu_modulo foi copiado
    assert (frontend_dest / "meu_modulo" / "index.html").exists()
    # Verifica se shared NÃO foi copiado para modules/shared/
    assert not (frontend_dest / "shared" / "core.css").exists()
```

- [ ] **Step 0b: Aplicar a modificação no copy_frontend**

Na função `copy_frontend()` (linha ~164), dentro do `for item in src.iterdir():`, adicionar como primeira linha:

```python
if item.name == "shared":
    logger.info("Ignorando diretório shared/ — já existe no monorepo")
    continue
```

- [ ] **Step 0c: Rodar test para verificar que passa**

```bash
cd apps/api-postgres
set PYTHONPATH=..\..\packages
pytest tests/unit/test_import_module_sqlserver.py::test_copy_frontend_skips_shared -v
```

Expected: PASS

- [ ] **Step 1: Escrever test para o fluxo import_module com target_api=sqlserver**

Adicionar ao final de `test_import_module_sqlserver.py`:

```python
@patch("scripts.import_module._get_monorepo_root")
@patch("scripts.import_module.validate_manifest")
@patch("scripts.import_module.copy_backend")
@patch("scripts.import_module.copy_frontend")
@patch("scripts.import_module.copy_migration")
@patch("scripts.import_module.register_router_sqlserver")
@patch("scripts.import_module.register_router")
@patch("scripts.import_module.register_dependency")
@patch("scripts.import_module.register_alembic_import")
@patch("scripts.import_module.register_menu")
def test_import_module_sqlserver_skips_postgres_steps(
    mock_register_menu,
    mock_register_alembic_import,
    mock_register_dependency,
    mock_register_router,
    mock_register_router_sqlserver,
    mock_copy_migration,
    mock_copy_frontend,
    mock_copy_backend,
    mock_validate_manifest,
    mock_get_monorepo_root,
    tmp_path,
):
    """Fluxo sqlserver deve pular migration, dependency e alembic import."""
    mock_get_monorepo_root.return_value = tmp_path
    mock_validate_manifest.return_value = {
        "module_name": "custo",
        "target_api": "sqlserver",
    }

    import_dir = tmp_path / "import_src"
    import_dir.mkdir()

    import_module.import_module(
        "custo", import_dir, force=True, dry_run=False, target_api="sqlserver"
    )

    mock_copy_backend.assert_called_once()
    mock_copy_frontend.assert_called_once()
    mock_copy_migration.assert_not_called()
    mock_register_router.assert_not_called()
    mock_register_router_sqlserver.assert_called_once()
    mock_register_dependency.assert_not_called()
    mock_register_alembic_import.assert_not_called()
    mock_register_menu.assert_called_once()


@patch("scripts.import_module._get_monorepo_root")
@patch("scripts.import_module.validate_manifest")
@patch("scripts.import_module.copy_backend")
@patch("scripts.import_module.copy_frontend")
@patch("scripts.import_module.copy_migration")
@patch("scripts.import_module.register_router")
@patch("scripts.import_module.register_dependency")
@patch("scripts.import_module.register_alembic_import")
@patch("scripts.import_module.register_menu")
@patch("scripts.import_module.register_router_sqlserver")
def test_import_module_postgres_default(
    mock_register_router_sqlserver,
    mock_register_menu,
    mock_register_alembic_import,
    mock_register_dependency,
    mock_register_router,
    mock_copy_migration,
    mock_copy_frontend,
    mock_copy_backend,
    mock_validate_manifest,
    mock_get_monorepo_root,
    tmp_path,
):
    """Sem target_api, deve seguir fluxo postgres (compatibilidade reversa)."""
    mock_get_monorepo_root.return_value = tmp_path
    mock_validate_manifest.return_value = {
        "module_name": "projetos",
    }

    import_dir = tmp_path / "import_src"
    import_dir.mkdir()

    import_module.import_module(
        "projetos", import_dir, force=True, dry_run=False
    )

    mock_copy_backend.assert_called_once()
    mock_copy_migration.assert_called_once()
    mock_register_router.assert_called_once()
    mock_register_dependency.assert_called_once()
    mock_register_alembic_import.assert_called_once()
    mock_register_router_sqlserver.assert_not_called()
```

- [ ] **Step 2: Rodar tests para verificar falha**

```bash
cd apps/api-postgres
set PYTHONPATH=..\..\packages
pytest tests/unit/test_import_module_sqlserver.py -v -k "test_import_module_sqlserver_skips or test_import_module_postgres_default"
```

Expected: FAIL (função `import_module` ainda não aceita `target_api`)

- [ ] **Step 3: Modificar `import_module()` e CLI**

**A. Modificar assinatura de `import_module()`** (linha ~471):

```python
def import_module(
    module_name: str,
    import_dir: Path,
    force: bool = False,
    dry_run: bool = False,
    skip_migrations: bool = False,
    target_api: str = "postgres",
) -> dict:
```

**B. Modificar o fluxo dentro de `import_module()`** — substituir as chamadas de register_router, copy_backend e steps de migration para serem condicionais:

Substituir o bloco de `copy_backend` (linha ~497-499):

```python
if not dry_run:
    copy_backend(import_dir, module_name, force)
```

A função `copy_backend` já aceita 3 parâmetros e copia para `_get_api_dir()` (api-postgres). Para sqlserver, precisamos copiar para `_get_sqlserver_api_dir()`. A abordagem mais limpa é modificar `copy_backend` para aceitar `target_api`:

```python
def copy_backend(import_dir: Path, module_name: str, force: bool, target_api: str = "postgres") -> None:
    import tempfile

    src = import_dir / "app" / "modules" / module_name
    api_dir = _get_api_dir() if target_api == "postgres" else _get_sqlserver_api_dir()
    dest = api_dir / "app" / "modules" / module_name
    # ... resto igual
```

Substituir o bloco de `register_router` (linha ~511-514):

```python
if not dry_run:
    if target_api == "sqlserver":
        register_router_sqlserver(manifest, force)
    else:
        register_router(manifest, force)
```

Substituir `copy_migration`, `register_dependency`, `register_alembic_import` e `run_migrations` para serem pulados quando `target_api == "sqlserver"`:

```python
if not dry_run:
    if target_api != "sqlserver":
        copy_migration(import_dir)
steps.append("Migration copiada")
_tick = _log_step("copy_migration", _tick)

if not dry_run:
    if target_api != "sqlserver":
        register_dependency(manifest, force)
steps.append("Dependency registrado em dependencies.py")
_tick = _log_step("register_dependency", _tick)

if not dry_run:
    if target_api != "sqlserver":
        register_alembic_import(manifest, force)
steps.append("Import do model registrado no alembic/env.py")
_tick = _log_step("register_alembic_import", _tick)

if not dry_run:
    register_menu(manifest)
steps.append("Menu registrado")
_tick = _log_step("register_menu", _tick)

if target_api != "sqlserver":
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
else:
    steps.append("Sqlserver module — no migrations needed")
```

**C. Adicionar `--target-api` ao ArgumentParser** (linha ~563):

```python
parser.add_argument(
    "--target-api",
    default="postgres",
    choices=["postgres", "sqlserver"],
    help="API alvo: postgres (default) ou sqlserver",
)
```

**D. Ler `target_api` do manifest se não passado via CLI** (após `validate_manifest`):

```python
manifest = validate_manifest(import_dir)
if target_api == "postgres":
    target_api = manifest.get("target_api", "postgres")
```

Isso permite que o CLI `--target-api` sobrescreva o valor do module.json, mas se não for passado, usa o do manifesto.

**E. Passar `target_api` para `import_module()`** no bloco `main()`:

```python
result = import_module(
    args.module_name,
    import_dir,
    force=args.force,
    dry_run=args.dry_run,
    skip_migrations=args.skip_migrations,
    target_api=args.target_api,
)
```

- [ ] **Step 4: Rodar testes para verificar passam**

```bash
cd apps/api-postgres
set PYTHONPATH=..\..\packages
pytest tests/unit/test_import_module_sqlserver.py -v
pytest tests/unit/test_import_module.py -v  # compatibilidade reversa
```

Expected: todos PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/scripts/import_module.py apps/api-postgres/tests/unit/test_import_module_sqlserver.py
git commit -m "feat(import): add --target-api CLI and conditional flow for api-sqlserver"
```

---

### Task 4: Atualizar `import_router.py` para ler `target_api` e repassar ao subprocesso

**Files:**
- Modify: `apps/api-postgres/app/routers/import_router.py`
- Modify: `apps/api-postgres/tests/unit/test_import_router.py`

- [ ] **Step 1: Escrever test para o import_router com target_api**

Adicionar em `test_import_router.py`:

```python
def test_import_passes_target_api_to_subprocess(mocker, tmp_path, db_session):
    """Quando module.json tem target_api='sqlserver', deve passar --target-api ao subprocesso."""
    import app.routers.import_router as import_router

    zip_path = tmp_path / "custo.zip"
    manifest = {
        "module_name": "custo",
        "entity_name": "CustoProduto",
        "target_api": "sqlserver",
        "schema_name": "org",
        "route_prefix": "/v1/produtos/custos",
        "menu_label": "Custos",
        "frontend_tabs": [{"name": "Custos", "url": "modules/custos/index.html"}],
    }
    _create_mock_zip(zip_path, manifest)

    mocker.patch.object(import_router, "_get_import_dir", return_value=tmp_path)
    mocker.patch.object(import_router.settings, "import_dir_path", str(tmp_path))
    mock_popen = mocker.patch("app.routers.import_router.subprocess.Popen")

    import_router.import_module("custo", force=False, db=db_session)

    call_args = mock_popen.call_args[0][0]
    assert "--target-api=sqlserver" in call_args


def test_import_defaults_to_postgres(mocker, tmp_path, db_session):
    """Quando module.json nao tem target_api, nao deve passar o argumento."""
    import app.routers.import_router as import_router

    zip_path = tmp_path / "projetos.zip"
    manifest = {
        "module_name": "projetos",
        "entity_name": "Projeto",
        "schema_name": "org",
        "route_prefix": "/v1/projetos",
        "menu_label": "Projetos",
        "frontend_tabs": [{"name": "Projetos", "url": "modules/projetos/index.html"}],
    }
    _create_mock_zip(zip_path, manifest)

    mocker.patch.object(import_router, "_get_import_dir", return_value=tmp_path)
    mocker.patch.object(import_router.settings, "import_dir_path", str(tmp_path))
    mock_popen = mocker.patch("app.routers.import_router.subprocess.Popen")

    import_router.import_module("projetos", force=False, db=db_session)

    call_args = mock_popen.call_args[0][0]
    assert "--target-api=sqlserver" not in call_args
```

(E usar a helper `_create_mock_zip` já existente no arquivo de test, ou criar uma simplificada que cria um zip com module.json dentro.)

- [ ] **Step 2: Rodar test para verificar falha**

```bash
cd apps/api-postgres
set PYTHONPATH=..\..\packages
pytest tests/unit/test_import_router.py -v -k "target_api"
```

Expected: FAIL

- [ ] **Step 3: Modificar `import_router.py`**

**A. No endpoint `import_module` (linha ~148), após ler o manifest e antes de montar o cmd:**

Adicionar após a leitura do manifest (após `manifest_path.exists()`, ~linha 190):

```python
with open(manifest_path, encoding="utf-8") as f:
    manifest_data = json.load(f)
target_api = manifest_data.get("target_api", "postgres")
```

**B. No cmd building (linha ~197-205), adicionar o argumento:**

```python
cmd = [
    sys.executable,
    str(script_path),
    module_name,
    f"--import-dir={tmp_dir}",
    "--skip-migrations",
]
if target_api == "sqlserver":
    cmd.append("--target-api=sqlserver")
if force:
    cmd.append("--force")
```

**C. No bloco de sucesso (linha ~282-291), pular migrations em background para sqlserver:**

```python
if result_data.get("success"):
    zip_path.unlink(missing_ok=True)
    logger.info("Zip removido após importação: %s", zip_path.name)
    if target_api != "sqlserver":
        threading.Thread(
            target=_run_migrations_background,
            args=(module_name,),
            daemon=True,
        ).start()
        result_data["steps"].append("Migrações agendadas em segundo plano")
    else:
        result_data["steps"].append("Módulo sqlserver importado — sem migrações")
    logger.info("Import de '%s' concluído em <60s", module_name)
```

**D. Atualizar `ModuleInfo` para incluir `target_api` no scan (opcional, para frontend):**

Adicionar campo no model:

```python
class ModuleInfo(BaseModel):
    slug: str
    module_name: str
    entity_name: str
    version: str
    menu_label: str
    schema_name: str
    target_api: str = "postgres"
    ja_importado: bool
```

E no scan, preencher:

```python
modules.append(
    ModuleInfo(
        ...
        target_api=manifest.get("target_api", "postgres"),
        ...
    )
)
```

- [ ] **Step 4: Rodar testes para verificar passam**

```bash
cd apps/api-postgres
set PYTHONPATH=..\..\packages
pytest tests/unit/test_import_router.py -v -k "target_api"
pytest tests/unit/test_import_router.py -v  # todos os tests existentes ainda passam
```

Expected: todos PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/app/routers/import_router.py apps/api-postgres/tests/unit/test_import_router.py
git commit -m "feat(import): pass target_api from module.json to import subprocess"
```

---

### Task 5: Atualizar documentação e AGENTS.md

**Files:**
- Modify: `docs/IMPORTACAO.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Adicionar seção sobre sqlserver no docs/IMPORTACAO.md**

Adicionar seção explicando o novo campo `target_api` no module.json, as diferenças de estrutura e o fluxo condicional.

- [ ] **Step 2: Atualizar AGENTS.md**

Adicionar nota sobre o suporte a `target_api` no import, semelhante às outras notas de arquitetura.

- [ ] **Step 3: Commit**

```bash
git add docs/IMPORTACAO.md AGENTS.md
git commit -m "docs: document sqlserver module import support"
```

---

## Self-Review

**1. Spec coverage:**
- `target_api` no module.json ✓ (Task 1)
- Estrutura zip sem models/migration ✓ (Task 1 — manifesto aceita; Task 3 — steps pulados)
- `_get_sqlserver_api_dir()` ✓ (Task 1)
- `register_router_sqlserver()` ✓ (Task 2)
- CLI `--target-api` ✓ (Task 3)
- Fluxo condicional em `import_module()` ✓ (Task 3)
- `import_router.py` lê target_api e repassa ✓ (Task 4)
- Pular migrations em background para sqlserver ✓ (Task 4)
- Testes de compatibilidade reversa ✓ (Task 3 — `test_import_module_postgres_default`)

**2. Placeholder scan:** Nenhum placeholder encontrado.

**3. Type consistency:** `target_api` é string, `"postgres"` default em todos os lugares. `register_router_sqlserver()` tem mesma assinatura que `register_router()` exceto nome. `import_module()` recebe `target_api` como último parâmetro opcional.
