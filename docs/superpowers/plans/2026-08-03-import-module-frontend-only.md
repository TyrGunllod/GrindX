# Importação de Módulos Frontend-Only Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Permitir importação de módulos frontend-only (sem `app/`, sem `migration/`, sem rotas) marcados com `frontend_only: true` no `module.json`, dispensando `schema_name`/`route_prefix` e pulando migrações.

**Architecture:** O flag `frontend_only` é lido no `module.json`. Em `validate_manifest` ele remove `schema_name`/`route_prefix` da lista de campos obrigatórios. Em `import_module` ele faz o guard de migrações virar falso. No router POST, ele suprime o agendamento da thread de migração em background. Os demais passos (`copy_backend`, `merge_requirements`, `copy_migration`, `register_router`, `register_dependency`, `register_alembic_import`) já são tolerantes a ausência de backend (logam *warning* e continuam) — o "phantom dir" (`app/modules/{slug}/module.json`) copiado durante o import mantém o scan (`ja_importado`, `pode_remover`) e a remoção funcionando sem mudança de lógica.

**Tech Stack:** Python 3, FastAPI, pytest, `unittest.mock`, ruff.

---

## Divergência documentada com a spec

A seção 3.2 da spec afirma que o router POST não precisa de mudanças. **Porém o critério de aceite nº 2 exige que frontend-only "não execute `alembic upgrade head`"**, e o POST atual agenda `_run_migrations_background` (que roda `alembic upgrade head`) sempre que `target_api != "sqlserver"` — ou seja, para frontend-only com `target_api` default (`postgres`) a migração em background aconteceria. Para satisfazer o critério de aceite, o **Task 3** adiciona a mudança mínima no router (suprimir a thread quando `frontend_only: true`). Critérios de aceite prevalecem sobre a prosa da spec.

---

## File Structure

- **Modify:** `apps/api-postgres/scripts/import_module.py` — `validate_manifest` (linhas 94-118) e bloco de migrações de `import_module` (linhas 823-837).
- **Modify:** `apps/api-postgres/app/routers/import_router.py` — bloco de sucesso do POST (linhas 349-362), suprimindo a thread de migração para frontend-only.
- **Create:** `apps/api-postgres/tests/unit/test_import_module_frontend_only.py` — testes unitários do script.
- **Modify:** `apps/api-postgres/tests/unit/test_import_router.py` — testes de POST e scan para frontend-only.
- **Modify:** `docs/IMPORTACAO.md` — tabela de campos, exemplo frontend-only, nota de troubleshooting.
- **Modify:** `AGENTS.md` — nota na seção "New Modules".

---

## Task 1: `validate_manifest` — campos obrigatórios condicionais

**Files:**
- Create: `apps/api-postgres/tests/unit/test_import_module_frontend_only.py`
- Modify: `apps/api-postgres/scripts/import_module.py:102-108`

- [ ] **Step 1: Write the failing test**

Create `apps/api-postgres/tests/unit/test_import_module_frontend_only.py`:

```python
"""Tests for frontend-only module support in import_module.py."""

import json

import pytest

import scripts.import_module as import_module


def _write_manifest(tmp_path, **overrides):
    manifest = {
        "module_name": "pop_viz",
        "entity_name": "PopViz",
        "menu_label": "Visualizador POP",
        "frontend_tabs": [
            {"name": "Visualizador POP", "url": "modules/pop_viz/index.html"}
        ],
    }
    manifest.update(overrides)
    (tmp_path / "module.json").write_text(json.dumps(manifest), encoding="utf-8")


def test_validate_manifest_accepts_frontend_only_without_schema_route(tmp_path):
    _write_manifest(tmp_path, frontend_only=True)

    result = import_module.validate_manifest(tmp_path)

    assert result["module_name"] == "pop_viz"
    assert result["frontend_only"] is True


def test_validate_manifest_rejects_without_flag_and_without_schema_route(tmp_path):
    _write_manifest(tmp_path)

    with pytest.raises(ValueError) as exc:
        import_module.validate_manifest(tmp_path)

    message = str(exc.value)
    assert "schema_name" in message
    assert "route_prefix" in message
```

- [ ] **Step 2: Run test to verify it fails**

Run (repo root):
```powershell
$env:PYTHONPATH = "packages"; python -m pytest apps/api-postgres/tests/unit/test_import_module_frontend_only.py -v
```
Expected: `test_validate_manifest_accepts_frontend_only_without_schema_route` FAILS com `ValueError: Campos obrigatórios ausentes ... ['schema_name', 'route_prefix']`. O segundo teste passa.

- [ ] **Step 3: Write minimal implementation**

Em `apps/api-postgres/scripts/import_module.py`, dentro de `validate_manifest`, substituir:

```python
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
```

por:

```python
    required = ["module_name", "entity_name", "menu_label"]
    if not manifest.get("frontend_only"):
        required += ["schema_name", "route_prefix"]
    missing = [k for k in required if k not in manifest]
    if missing:
        raise ValueError(f"Campos obrigatórios ausentes no module.json: {missing}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `$env:PYTHONPATH = "packages"; python -m pytest apps/api-postgres/tests/unit/test_import_module_frontend_only.py -v`
Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/scripts/import_module.py apps/api-postgres/tests/unit/test_import_module_frontend_only.py
git commit -m "feat(import): accept frontend-only manifest without schema/route"
```

---

## Task 2: `import_module` — pular migrações para frontend-only

**Files:**
- Modify: `apps/api-postgres/tests/unit/test_import_module_frontend_only.py` (adicionar teste)
- Modify: `apps/api-postgres/scripts/import_module.py:823-837`

- [ ] **Step 1: Write the failing test**

Adicionar ao final de `apps/api-postgres/tests/unit/test_import_module_frontend_only.py` e adicionar `from unittest.mock import patch` no bloco de imports do topo do arquivo:

```python
@patch("scripts.import_module._get_monorepo_root")
@patch("scripts.import_module.validate_manifest")
@patch("scripts.import_module.copy_backend")
@patch("scripts.import_module.copy_frontend")
@patch("scripts.import_module.copy_migration")
@patch("scripts.import_module.register_router")
@patch("scripts.import_module.register_dependency")
@patch("scripts.import_module.register_alembic_import")
@patch("scripts.import_module.register_menu")
@patch("scripts.import_module.run_migrations")
def test_import_module_frontend_only_nao_roda_migrations(
    mock_run_migrations,
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
    """Fluxo frontend-only deve pular run_migrations mesmo com skip_migrations=False."""
    mock_get_monorepo_root.return_value = tmp_path
    mock_validate_manifest.return_value = {
        "module_name": "pop_viz",
        "frontend_only": True,
    }

    import_dir = tmp_path / "import_src"
    import_dir.mkdir()

    result = import_module.import_module(
        "pop_viz", import_dir, force=True, dry_run=False, skip_migrations=False
    )

    assert result["success"] is True
    mock_run_migrations.assert_not_called()
    assert any("sem migrações" in step for step in result["steps"])
```

Nota: `@patch` é decorator de módulo, avaliado no import do arquivo — por isso `from unittest.mock import patch` deve ir no topo (junto de `import json` e `import pytest`), não dentro da função. Os decorators são aplicados de baixo para cima, então os argumentos da função vão na ordem inversa (como no `test_import_module_sqlserver.py` existente).

- [ ] **Step 2: Run test to verify it fails**

Run: `$env:PYTHONPATH = "packages"; python -m pytest apps/api-postgres/tests/unit/test_import_module_frontend_only.py -v`
Expected: `test_import_module_frontend_only_nao_roda_migrations` FAILS — `mock_run_migrations.assert_not_called()` falha porque `run_migrations` foi chamado.

- [ ] **Step 3: Write minimal implementation**

Em `apps/api-postgres/scripts/import_module.py`, dentro de `import_module`, substituir o bloco:

```python
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
            steps.append("Módulo sqlserver — sem migrações necessárias")
```

por:

```python
        is_frontend_only = manifest.get("frontend_only", False)
        if target_api != "sqlserver" and not is_frontend_only:
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
        elif is_frontend_only:
            steps.append("Módulo frontend-only — sem migrações")
        else:
            steps.append("Módulo sqlserver — sem migrações necessárias")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `$env:PYTHONPATH = "packages"; python -m pytest apps/api-postgres/tests/unit/test_import_module_frontend_only.py -v`
Expected: `3 passed` (2 do Task 1 + este)

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/scripts/import_module.py apps/api-postgres/tests/unit/test_import_module_frontend_only.py
git commit -m "feat(import): skip migrations for frontend-only modules"
```

---

## Task 3: Router POST — não agendar migrações em background para frontend-only

**Files:**
- Modify: `apps/api-postgres/tests/unit/test_import_router.py` (adicionar `TestImportFrontendOnly`)
- Modify: `apps/api-postgres/app/routers/import_router.py:349-362`

- [ ] **Step 1: Write the failing test**

Adicionar ao final de `apps/api-postgres/tests/unit/test_import_router.py` (usando o helper `_criar_zip_manifest` já definido no arquivo):

```python
class TestImportFrontendOnly:
    def test_import_frontend_only_nao_agenda_migracoes(
        self, client, auth_headers, tmp_path, monkeypatch
    ):
        from unittest.mock import patch

        _criar_zip_manifest(
            tmp_path,
            "pop_viz",
            {
                "module_name": "pop_viz",
                "entity_name": "PopViz",
                "frontend_only": True,
                "menu_label": "Visualizador POP",
                "frontend_tabs": [
                    {
                        "name": "Visualizador POP",
                        "url": "modules/pop_viz/index.html",
                    }
                ],
            },
        )
        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )

        with patch("scripts.import_module.import_module") as mock_import, patch(
            "app.routers.import_router._run_migrations_background"
        ) as mock_bg:
            mock_import.return_value = {"success": True, "steps": ["ok"]}
            response = client.post(
                "/v1/import/pop_viz?force=true", headers=auth_headers
            )

        assert response.status_code == 200, response.text
        steps = response.json()["steps"]
        assert "Módulo frontend-only importado — sem migrações" in steps
        assert "Migrações agendadas em segundo plano" not in steps
        mock_bg.assert_not_called()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `$env:PYTHONPATH = "packages"; python -m pytest apps/api-postgres/tests/unit/test_import_router.py::TestImportFrontendOnly -v`
Expected: FAILS — `assert "Módulo frontend-only importado — sem migrações" in steps` falha porque o fluxo atual agenda a migração.

- [ ] **Step 3: Write minimal implementation**

Em `apps/api-postgres/app/routers/import_router.py`, no bloco de sucesso do POST, substituir:

```python
        if result_data.get("success"):
            zip_path.unlink(missing_ok=True)
            logger.info("Zip removido após importação: %s", zip_path.name)
            steps = result_data.get("steps", [])
            if target_api != "sqlserver":
                threading.Thread(
                    target=_run_migrations_background,
                    args=(module_name,),
                    daemon=True,
                ).start()
                steps.append("Migrações agendadas em segundo plano")
            else:
                steps.append("Módulo sqlserver importado — sem migrações")
            logger.info("Import de '%s' concluído", module_name)
```

por:

```python
        if result_data.get("success"):
            zip_path.unlink(missing_ok=True)
            logger.info("Zip removido após importação: %s", zip_path.name)
            steps = result_data.get("steps", [])
            frontend_only = manifest_data.get("frontend_only", False)
            if target_api != "sqlserver" and not frontend_only:
                threading.Thread(
                    target=_run_migrations_background,
                    args=(module_name,),
                    daemon=True,
                ).start()
                steps.append("Migrações agendadas em segundo plano")
            elif frontend_only:
                steps.append("Módulo frontend-only importado — sem migrações")
            else:
                steps.append("Módulo sqlserver importado — sem migrações")
            logger.info("Import de '%s' concluído", module_name)
```

`manifest_data` já existe no escopo (lido do `module.json` extraído, linhas 309-310 do router).

- [ ] **Step 4: Run test to verify it passes**

Run: `$env:PYTHONPATH = "packages"; python -m pytest apps/api-postgres/tests/unit/test_import_router.py -v`
Expected: `4 passed` (3 existentes de TestImportEndpoint + 1 de TestImportFrontendOnly) — na prática o arquivo tem mais testes, todos PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/app/routers/import_router.py apps/api-postgres/tests/unit/test_import_router.py
git commit -m "feat(import): skip background migrations for frontend-only in router"
```

---

## Task 4: Scan — teste de regressão para frontend-only importado

**Files:**
- Modify: `apps/api-postgres/tests/unit/test_import_router.py` (adicionar teste em `TestImportFrontendOnly`)

> Este teste é de **caracterização/regressão**: o comportamento já funciona sem mudança de código (a spec seção 3.1 confirma). Ele trava o critério de aceite nº 4. Esperado que passe já na primeira execução.

- [ ] **Step 1: Write the test**

Adicionar dentro de `TestImportFrontendOnly` em `apps/api-postgres/tests/unit/test_import_router.py`:

```python
    def test_scan_frontend_only_importado_como_ja_importado(
        self, client, auth_headers, tmp_path, monkeypatch
    ):
        import pathlib

        _criar_zip_manifest(
            tmp_path,
            "pop_viz",
            {
                "module_name": "pop_viz",
                "entity_name": "PopViz",
                "frontend_only": True,
                "menu_label": "Visualizador POP",
            },
        )
        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )

        # Simula o "phantom dir" (module.json copiado) + pasta de frontend
        phantom_backend = (
            tmp_path / "apps" / "api-postgres" / "app" / "modules" / "pop_viz"
        )
        phantom_backend.mkdir(parents=True)
        (phantom_backend / "module.json").write_text(
            json.dumps({"module_name": "pop_viz", "frontend_only": True}),
            encoding="utf-8",
        )
        frontend_mod = (
            tmp_path / "apps" / "frontend-webapp" / "modules" / "pop_viz"
        )
        frontend_mod.mkdir(parents=True)
        (frontend_mod / "index.html").write_text("<html></html>", encoding="utf-8")

        # Redireciona Path(__file__).resolve() do scan para tmp_path
        real_resolve = pathlib.Path.resolve

        def _fake_resolve(path_obj, strict=False):
            if "import_router.py" in str(path_obj):
                return pathlib.Path(
                    tmp_path
                    / "apps"
                    / "api-postgres"
                    / "app"
                    / "routers"
                    / "import_router.py"
                )
            return real_resolve(path_obj, strict=strict)

        monkeypatch.setattr(pathlib.Path, "resolve", _fake_resolve)

        response = client.get("/v1/import/scan", headers=auth_headers)
        assert response.status_code == 200
        modules = response.json()["modules"]
        found = [m for m in modules if m["slug"] == "pop_viz"]
        assert len(found) == 1
        assert found[0]["ja_importado"] is True
        assert found[0]["pode_remover"] is True
```

- [ ] **Step 2: Run test to verify it passes (caracterização)**

Run: `$env:PYTHONPATH = "packages"; python -m pytest apps/api-postgres/tests/unit/test_import_router.py::TestImportFrontendOnly -v`
Expected: `2 passed` — o novo teste já passa com o comportamento existente do scan.

- [ ] **Step 3: Commit**

```bash
git add apps/api-postgres/tests/unit/test_import_router.py
git commit -m "test(import): guard scan detection for frontend-only modules"
```

---

## Task 5: Documentação

**Files:**
- Modify: `docs/IMPORTACAO.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Adicionar exemplo frontend-only em `docs/IMPORTACAO.md`**

Logo após o bloco de exemplo SQL Server (que termina na linha 220, antes da tabela), inserir:

```markdown
Para módulos **frontend-only** (sem backend — só HTML/CSS/JS, reutilizando endpoints de outro módulo), adicione `frontend_only: true`:

```json
{
  "module_name": "pop_viz",
  "entity_name": "PopViz",
  "version": "1.0.0",
  "frontend_only": true,
  "frontend_tabs": [
    {"name": "Visualizador POP", "url": "modules/pop_viz/index.html"}
  ],
  "menu_label": "Visualizador POP",
  "menu_icone": "folder",
  "role_minima": "leitura",
  "dependencies": ["pop_docs"]
}
```

Módulos frontend-only **dispensam** `schema_name`/`route_prefix` e **não rodam migrações**. A pasta de frontend deve ter o **mesmo nome** do `module_name` (ex: `pop_viz`, não `pop-viz`) — o scan e a remoção dependem desse nome idêntico.
```

- [ ] **Step 2: Atualizar a tabela de campos em `docs/IMPORTACAO.md`**

Linha 226 — `schema_name`:
```markdown
| `schema_name` | Sim* | Schema do banco (`org`, `catalogo`, `portal`, `custo`) — exceto frontend-only (`frontend_only: true`) |
```

Linha 227 — `route_prefix`:
```markdown
| `route_prefix` | Sim* | Prefixo da URL da API — exceto frontend-only (`frontend_only: true`) |
```

Adicionar nova linha `frontend_only` após a linha `target_api` (linha 231):
```markdown
| `frontend_only` | Não | Marca o módulo como frontend-only — dispensa `schema_name`/`route_prefix` e pula migrações (default: `false`) |
```

- [ ] **Step 3: Nota na seção Troubleshooting de `docs/IMPORTACAO.md`**

Em `### "Campos obrigatórios ausentes no module.json"` (linha 400-402), manter a mensagem atual e acrescentar:

```markdown
O `module.json` não contém todos os campos obrigatórios. Verifique se o zip foi gerado com `make package` (não manualmente). Para módulos frontend-only, o erro só ocorre se `frontend_only: true` estiver ausente.
```

- [ ] **Step 4: Atualizar `AGENTS.md` (seção "New Modules")**

Após o bloco `### Import para api-sqlserver`, adicionar:

```markdown
### Módulos frontend-only

Módulos sem backend (reutilizam endpoints de outros módulos) usam `frontend_only: true` no `module.json`:
- Dispensam `schema_name`/`route_prefix` na validação
- Não executam migrações (nem o agendamento em background no router POST)
- Pasta de frontend com nome idêntico ao `module_name`
```

- [ ] **Step 5: Commit**

```bash
git add docs/IMPORTACAO.md AGENTS.md
git commit -m "docs(import): document frontend_only flag"
```

---

## Task 6: Verificação final

- [ ] **Step 1: Rodar suíte unitária completa da api-postgres**

Run: `$env:PYTHONPATH = "packages"; python -m pytest apps/api-postgres/tests/ -v --tb=short`
Expected: todos PASS (sem regressões nos testes de import existentes).

- [ ] **Step 2: Rodar `make test-all` (gate de pre-push do AGENTS.md)**

Run: `make test-all`
Expected: todos PASS.

- [ ] **Step 3: Ruff format + check**

Run:
```powershell
ruff format apps/api-postgres/scripts/import_module.py apps/api-postgres/app/routers/import_router.py apps/api-postgres/tests/unit/
ruff check --fix apps/api-postgres/scripts/import_module.py apps/api-postgres/app/routers/import_router.py apps/api-postgres/tests/unit/
ruff check apps/api-postgres/scripts/import_module.py apps/api-postgres/app/routers/import_router.py apps/api-postgres/tests/unit/
```
Expected: sem erros (ruff.toml ignora E501; seleciona E, F, I).

- [ ] **Step 4: Commit (se houver mudanças de formato)**

```bash
git add apps/api-postgres/scripts/import_module.py apps/api-postgres/app/routers/import_router.py apps/api-postgres/tests/unit/
git commit -m "style(import): ruff format"
```

---

## Self-Review

**Spec coverage:**
- §1 (manifiesto `frontend_only`) → Task 1, Task 5.
- §2.1 (`validate_manifest` condicional) → Task 1.
- §2.2 (pular migrações) → Task 2.
- §3.1 (scan sem mudança de lógica + requisito de nome idêntico) → Task 4 (regressão) + Task 5 (documento o requisito de nomenclatura).
- §3.2 (router sem mudança) → Task 3 (divergência documentada: mudança mínima para cumprir critério de aceite nº 2).
- §4 (documentação) → Task 5.
- §5 (testes) → Tasks 1, 2, 3, 4.
- Critérios de aceite 1-4 → Tasks 1, 2, 3, 4.

**Placeholder scan:** nenhum "TBD"/"TODO"; todo passo de código tem código completo.

**Type consistency:** `frontend_only` usado consistentemente como `manifest.get("frontend_only", False)`/`manifest_data.get("frontend_only", False)`; mensagens de steps estáveis: "Módulo frontend-only — sem migrações" (script) e "Módulo frontend-only importado — sem migrações" (router).
