# Atualizar Módulo sem Desinstalar — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Permitir atualizar um módulo importado pelo Importador preservando aba, ordem, permissões e dados, com falha de migration visível e restart automático opcional em produção.

**Architecture:** O reimport com `force=True` já preserva o portal; o plano adiciona validação de pacote, limpeza/regeneração de registros gerados, integridade da cadeia de migrations, migrations inline na atualização e auto-restart via `SIGTERM` atrás de flag. O frontend troca o botão "Remover" da lista de zips por "Atualizar" quando o módulo já está instalado.

**Tech Stack:** Python 3.12, FastAPI, pytest, Alembic, Vanilla JS (módulo `importer`), pydantic-settings, Podman Compose.

**Spec:** `docs/superpowers/specs/2026-11-24-atualizar-modulo-design.md`

## Global Constraints

- Configurações novas em `app/core/config.py` seguem o padrão UPPERCASE do `BaseSettings` (ex.: `IMPORT_AUTO_RESTART: bool = False`).
- `shared` não é instalado via pip: qualquer comando manual precisa de `PYTHONPATH` para `packages/`; os alvos `make test-*` já fazem isso.
- Nada pode escrever em `portal.modulos` ou `usuario_modulo` no fluxo de atualização.
- Nenhuma migration do módulo pode ser apagada ou carimbada sem aplicação.
- Commits em conventional commits, título em inglês, referência `Refs #7`.
- Ruff: `select = ["E", "F", "I"]`, `ignore = ["E501"]`; rodar `ruff check` e `ruff format` antes do commit final.
- Branch de trabalho: `feat/atualizar-modulo`.

## Review Focus

1. Zip de atualização que remove ou renomeia um service: `dependencies.py` não pode ficar com import/factory apontando para classe inexistente (Task 2).
2. Banco em revisão órfã ou migration extra não aplicada: nunca carimbar o head nem apagar arquivo; recusar ou arquivar (Task 4).
3. Migration com SQL inválido durante a atualização: resposta precisa ser `success: false` com stderr, não sucesso silencioso (Task 3).
4. Zip cujo `module_name` não bate com o slug da URL (fuzzy match): falhar antes de copiar ou registrar qualquer coisa (Task 1).
5. Flag de restart ligada num fluxo que não é atualização bem-sucedida (instalação nova, frontend-only, falha): a API não pode ser derrubada (Task 6).

---

### Task 1: Validar `module_name` do zip contra o slug da URL

**Files:**
- Modify: `apps/api-postgres/scripts/import_module.py:938-963` (início de `import_module()`)
- Test: `apps/api-postgres/tests/unit/test_import_module.py` (nova classe no fim do arquivo)

**Interfaces:**
- Consumes: `validate_manifest(import_dir) -> dict` (existente).
- Produces: `import_module()` passa a levantar `ValueError` com a mensagem `Zip pertence ao módulo '<manifest>', não '<slug>'`; o `except` externo devolve `{"success": False, "steps": [...], "error": "..."}`.

- [ ] **Step 1: Write the failing test**

Adicionar ao fim de `tests/unit/test_import_module.py`:

```python
class TestSlugValidation:
    def test_zip_de_outro_modulo_falha_antes_da_copia(self, tmp_path):
        import_dir = tmp_path / "zip"
        import_dir.mkdir()
        (import_dir / "module.json").write_text(
            json.dumps(
                {
                    "module_name": "custos",
                    "entity_name": "Custo",
                    "menu_label": "Custos",
                    "schema_name": "org",
                    "route_prefix": "/v1/custos",
                    "frontend_url": "modules/custos/index.html",
                }
            ),
            encoding="utf-8",
        )

        result = import_module.import_module("custo", import_dir, dry_run=True)

        assert result["success"] is False
        assert "custos" in result["error"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `make test-postgres`
Expected: FAIL em `TestSlugValidation` — hoje o import segue adiante e devolve `success: True`.

- [ ] **Step 3: Implement the validation**

Em `import_module()`, logo após `manifest = validate_manifest(import_dir)`:

```python
if manifest["module_name"] != module_name:
    raise ValueError(
        f"Zip pertence ao módulo '{manifest['module_name']}', não '{module_name}'"
    )
```

Antes do `backup_existing()`, para não tocar em nada quando divergir.

- [ ] **Step 4: Run test to verify it passes**

Run: `make test-postgres`
Expected: PASS em `TestSlugValidation`.

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/scripts/import_module.py apps/api-postgres/tests/unit/test_import_module.py
git commit -m "fix: rejeita zip de outro modulo no import" -m "Refs #7"
```

---

### Task 2: `_clean_registrations` e limpeza/regeneração de registros na atualização

**Files:**
- Modify: `apps/api-postgres/scripts/import_module.py` (nova função perto de `_clean_requirements_txt`; `remove_module()` linhas 1206-1255; `import_module()` linhas 950-1030)
- Test: `apps/api-postgres/tests/unit/test_import_module.py`

**Interfaces:**
- Produces: `_clean_registrations(module_name: str, steps: list[str]) -> None` — limpa `app/auth/dependencies.py`, `alembic/env.py` e `requirements.txt` do `api-postgres`.
- Produces: resultado de `import_module()` ganha a chave `updated: bool`.
- Consumes: `_clean_main_py(main_py, module_name, steps)` e `_clean_requirements_txt(module_name, api_dir)` (existentes).

- [ ] **Step 1: Write the failing tests**

```python
class TestCleanRegistrations:
    def test_limpa_dependencies_env_e_requirements(self, tmp_path, monkeypatch):
        api = tmp_path / "apps" / "api-postgres"
        (api / "app" / "auth").mkdir(parents=True)
        (api / "app" / "auth" / "dependencies.py").write_text(
            "from app.modules.mod_x.services.x_service import XService\n"
            "def get_mod_x_service(db=Depends(get_db)) -> XService:\n"
            '    """Factory."""\n'
            "    return XService(db)\n",
            encoding="utf-8",
        )
        (api / "alembic").mkdir(parents=True)
        (api / "alembic" / "env.py").write_text(
            "from app.modules.mod_x.models.x import X  # noqa: F401\n",
            encoding="utf-8",
        )
        (api / "requirements.txt").write_text(
            "# === Módulo mod_x ===\nfoo==1.0\n", encoding="utf-8"
        )
        monkeypatch.setattr(import_module, "_get_monorepo_root", lambda: tmp_path)

        steps = []
        import_module._clean_registrations("mod_x", steps)

        assert "mod_x" not in (api / "app" / "auth" / "dependencies.py").read_text(
            encoding="utf-8"
        )
        assert "mod_x" not in (api / "alembic" / "env.py").read_text(encoding="utf-8")
        assert "mod_x" not in (api / "requirements.txt").read_text(encoding="utf-8")
        assert steps


class TestUpdateDetection:
    # Use o mesmo bloco de patches de
    # tests/unit/test_import_module_sqlserver.py:160-204 (copy_*, register_*,
    # register_menu, validate_manifest) e acrescente: _clean_registrations,
    # backup_existing, run_migrations (MagicMock) e _get_db_current_revision
    # (retorno None) — sem isso o teste escreve no import/ e no banco reais.
    def test_atualizacao_limpa_registros_antes_de_registrar(
        self,
        mock_clean,
        mock_validate,
        tmp_path,
    ):
        api = tmp_path / "api"
        (api / "app" / "modules" / "mod_x").mkdir(parents=True)
        (api / "app" / "main.py").write_text("", encoding="utf-8")
        mock_validate.return_value = {"module_name": "mod_x", "frontend_url": "x"}
        import_dir = tmp_path / "zip"
        import_dir.mkdir()

        with patch("scripts.import_module._get_api_dir", return_value=api):
            result = import_module.import_module("mod_x", import_dir, force=True)

        mock_clean.assert_called_once()
        assert result["updated"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `make test-postgres`
Expected: FAIL — `_clean_registrations` não existe e `result["updated"]` gera `KeyError`.

- [ ] **Step 3: Implement**

1. Mover o bloco de `remove_module()` (limpeza de `dependencies.py`, `alembic/env.py` e `requirements.txt`) para:

```python
def _clean_registrations(module_name: str, steps: list[str]) -> None:
```

usando `_get_monorepo_root()` internamente e mantendo os mesmos textos de step (`"Dependencies limpas em auth/dependencies.py"`, etc.). `remove_module()` chama a função no lugar do bloco.
2. Em `import_module()`, calcular `is_update = (api_dir / "app" / "modules" / module_name).exists()` antes do `copy_backend` (`api_dir` = `_get_api_dir()` ou `_get_sqlserver_api_dir()` conforme `target_api`).
3. Depois do `copy_backend` e antes do `merge_requirements`:

```python
if is_update:
    _clean_main_py(api_dir / "app" / "main.py", module_name, steps)
    if target_api != "sqlserver":
        _clean_registrations(module_name, steps)
```

4. Retorno de sucesso inclui `"updated": is_update` e, quando verdadeiro, step `"Atualização concluída — reinicie a API para carregar o novo código"`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `make test-postgres`
Expected: PASS. Os testes de `remove_module` e do fluxo de import existentes continuam verdes.

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/scripts/import_module.py apps/api-postgres/tests/unit/test_import_module.py
git commit -m "feat: limpa registros gerados ao atualizar modulo" -m "Refs #7"
```

---

### Task 3: Falha de migration bloqueia a atualização e revisão é reportada

**Files:**
- Modify: `apps/api-postgres/scripts/import_module.py:1033-1049`
- Test: `apps/api-postgres/tests/unit/test_import_module.py`

**Interfaces:**
- Consumes: `run_migrations() -> None` (levanta `RuntimeError`), `_get_db_current_revision() -> str | None`.
- Produces: `import_module()` devolve `success: False` e `error` com o texto da exceção de migration; no sucesso adiciona step `"Schema na revisão <rev>"`.

- [ ] **Step 1: Write the failing test**

```python
class TestMigrationFailure:
    # Mesmo bloco de patches de test_import_module_sqlserver.py:160-204 +
    # backup_existing, copy_backend/merge_requirements/copy_frontend/
    # copy_migration e run_migrations (side_effect RuntimeError).
    def test_falha_de_migration_retorna_erro(
        self, mock_run_migrations, mock_validate, tmp_path
    ):
        mock_validate.return_value = {"module_name": "mod_x", "frontend_url": "x"}
        mock_run_migrations.side_effect = RuntimeError("migration boom")
        import_dir = tmp_path / "zip"
        import_dir.mkdir()

        with patch("scripts.import_module._get_api_dir", return_value=tmp_path):
            result = import_module.import_module("mod_x", import_dir, force=True)

        assert result["success"] is False
        assert "migration boom" in result["error"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `make test-postgres`
Expected: FAIL — hoje a exceção é capturada com warning e o resultado é `success: True`.

- [ ] **Step 3: Implement**

Substituir o `try/except` do bloco de migrations por chamada direta; em caso de sucesso, ler `_get_db_current_revision()` e acrescentar `steps.append(f"Schema na revisão {rev or 'desconhecida'}")`. A exceção sobe para o `except` externo, que já devolve `success: False`.

- [ ] **Step 4: Run test to verify it passes**

Run: `make test-postgres`
Expected: PASS em `TestMigrationFailure`.

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/scripts/import_module.py apps/api-postgres/tests/unit/test_import_module.py
git commit -m "fix: propaga falha de migration na importacao" -m "Refs #7"
```

---

### Task 4: Integridade da cadeia de migrations em `copy_migration()`

**Files:**
- Modify: `apps/api-postgres/scripts/import_module.py:534-578` e nova `_archive_unapplied_migration()` perto de `copy_migration()`
- Test: `apps/api-postgres/tests/unit/test_import_module.py:575-677`

**Interfaces:**
- Produces: `_archive_unapplied_migration(filepath: Path) -> Path` — move o arquivo para `_get_import_dir() / BACKUP_DIRNAME / "unapplied_migrations"` e devolve o destino; `PermissionError` vira `RuntimeError`.
- Produces: `copy_migration()` levanta `RuntimeError` quando `current_rev` não existe em nenhum arquivo (revisão órfã) nem na cadeia do módulo.

- [ ] **Step 1: Write the failing tests**

Alterar `_run_copy_migration` para também patchar `_get_import_dir` (retornando o `import_dir` da fixture) e substituir `test_banco_fora_da_cadeia_reconcilia_para_head_do_modulo` por:

```python
    def test_banco_em_revisao_orfa_levanta_erro(self, migration_env):
        api_dir, versions, import_dir = migration_env
        _write_migration(
            versions / "100_create.py", "100", "023a4c5d6e7f", marker="pop_docs"
        )
        _write_source_migration(import_dir, "100_create.py")

        with (
            patch("scripts.import_module._get_api_dir", return_value=api_dir),
            patch(
                "scripts.import_module._get_db_current_revision", return_value="999"
            ),
        ):
            with pytest.raises(RuntimeError, match="999"):
                copy_migration(import_dir)

    def test_reimport_arquiva_migration_nao_aplicada(self, migration_env):
        api_dir, versions, import_dir = migration_env
        _write_migration(
            versions / "100_create.py", "100", "023a4c5d6e7f", marker="pop_docs"
        )
        _write_migration(versions / "101_add.py", "101", "100", marker="pop_docs")
        _write_source_migration(import_dir, "100_create.py")
        _write_source_migration(import_dir, "106_add.py")

        _run_copy_migration(api_dir, import_dir, current_rev="100")

        assert sorted(p.name for p in versions.glob("1*.py")) == [
            "100_create.py",
            "101_add.py",
        ]
        archived = list((import_dir / ".backup" / "unapplied_migrations").glob("*.py"))
        assert [p.name for p in archived] == ["101_add.py"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `make test-postgres`
Expected: FAIL — o caso órfão hoje faz `stamp_revision("100")` sem levantar, e o arquivo 101 é apagado.

- [ ] **Step 3: Implement**

1. No branch "reimport: banco na cadeia", trocar `stale.unlink()` por `_archive_unapplied_migration(stale)` (com log do destino).
2. No branch de revisão órfã, trocar `_stamp_revision(head_rev)` por:

```python
raise RuntimeError(
    f"Banco na revisão '{current_rev}', que não existe mais nos arquivos. "
    f"Head do módulo '{module_name}': '{head_rev}'. "
    "Resolva o alembic_version antes de atualizar."
)
```

3. `_archive_unapplied_migration`: `dest_dir.mkdir(parents=True, exist_ok=True)`, `shutil.move(str(filepath), str(dest))`; em `PermissionError`, levantar `RuntimeError` citando o arquivo.
4. Remover `_stamp_revision()` (ficou sem uso) e o import/uso correspondente em `_run_copy_migration` no teste.

- [ ] **Step 4: Run tests to verify they pass**

Run: `make test-postgres`
Expected: PASS nos quatro testes de `TestCopyMigration`.

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/scripts/import_module.py apps/api-postgres/tests/unit/test_import_module.py
git commit -m "fix: preserva integridade da cadeia de migrations no reimport" -m "Refs #7"
```

---

### Task 5: Rota de import distingue atualização (migrations inline, sem background)

**Files:**
- Modify: `apps/api-postgres/app/routers/import_router.py:28-60` e `264-391`
- Test: `apps/api-postgres/tests/unit/test_import_router.py`

**Interfaces:**
- Produces: `_is_update(module_name: str) -> bool` — verdadeiro quando `app/modules/{module_name}` existe no `api-postgres`.
- Consumes: `run_import(..., skip_migrations=..., ...)` e o campo `updated` do resultado (Task 2).

- [ ] **Step 1: Write the failing tests**

```python
class TestImportUpdate:
    def test_atualizacao_roda_migrations_inline(
        self, client, auth_headers, tmp_path, monkeypatch
    ):
        from unittest.mock import patch

        _criar_zip_manifest(
            tmp_path,
            "projetos",
            {
                "module_name": "projetos",
                "entity_name": "Projeto",
                "schema_name": "org",
                "route_prefix": "/v1/projetos",
                "menu_label": "Projetos",
                "frontend_tabs": [
                    {"name": "Projetos", "url": "modules/projetos/index.html"}
                ],
            },
        )
        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )

        with (
            patch("scripts.import_module.import_module") as mock_import,
            patch("app.routers.import_router._is_update", return_value=True),
            patch("app.routers.import_router._run_migrations_background") as mock_bg,
        ):
            mock_import.return_value = {
                "success": True,
                "steps": ["ok"],
                "updated": True,
            }
            response = client.post("/v1/import/projetos", headers=auth_headers)

        assert response.status_code == 200, response.text
        _, _, call_kwargs = mock_import.mock_calls[0]
        assert call_kwargs["skip_migrations"] is False
        mock_bg.assert_not_called()
        assert "Módulo atualizado com sucesso." in response.json()["message"]

    def test_instalacao_nova_mantem_migrations_em_background(
        self, client, auth_headers, tmp_path, monkeypatch
    ):
        from unittest.mock import patch

        _criar_zip_manifest(
            tmp_path,
            "projetos",
            {
                "module_name": "projetos",
                "entity_name": "Projeto",
                "schema_name": "org",
                "route_prefix": "/v1/projetos",
                "menu_label": "Projetos",
                "frontend_tabs": [
                    {"name": "Projetos", "url": "modules/projetos/index.html"}
                ],
            },
        )
        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )

        with (
            patch("scripts.import_module.import_module") as mock_import,
            patch("app.routers.import_router._is_update", return_value=False),
            patch("app.routers.import_router._run_migrations_background") as mock_bg,
        ):
            mock_import.return_value = {"success": True, "steps": ["ok"]}
            response = client.post("/v1/import/projetos", headers=auth_headers)

        assert response.status_code == 200, response.text
        _, _, call_kwargs = mock_import.mock_calls[0]
        assert call_kwargs["skip_migrations"] is True
        mock_bg.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `make test-postgres`
Expected: FAIL — `_is_update` não existe e `skip_migrations` é sempre `True`.

- [ ] **Step 3: Implement**

1. `_is_update(module_name)` usando `Path(__file__).resolve().parent.parent.parent / "app" / "modules" / module_name`.
2. No endpoint: `update = _is_update(module_name)`; `skip_migrations=not update` na chamada de `run_import`; agendar `_run_migrations_background` somente quando `not update`.
3. Mensagem: `"Módulo atualizado com sucesso."` se `result_data.get("updated")`, senão manter a atual.

- [ ] **Step 4: Run tests to verify they pass**

Run: `make test-postgres`
Expected: PASS nos dois testes novos e nos existentes de `TestImportSqlServer` / `TestImportFrontendOnly`.

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/app/routers/import_router.py apps/api-postgres/tests/unit/test_import_router.py
git commit -m "feat: atualiza modulo com migrations sincronas na rota de import" -m "Refs #7"
```

---

### Task 6: Auto-restart opt-in após atualização bem-sucedida

**Files:**
- Modify: `apps/api-postgres/app/core/config.py:76-77` (seção Import de Módulos)
- Modify: `apps/api-postgres/app/routers/import_router.py` (imports, `_restart_api`, assinatura do endpoint)
- Modify: `compose.yaml:52-53`
- Test: `apps/api-postgres/tests/unit/test_import_router.py`

**Interfaces:**
- Produces: `settings.IMPORT_AUTO_RESTART: bool` (default `False`).
- Produces: `_restart_api() -> None` em `import_router` — `time.sleep(2)` e `os.kill(os.getpid(), signal.SIGTERM)`.
- Consumes: `BackgroundTasks` do FastAPI e `_is_update()` (Task 5).

- [ ] **Step 1: Write the failing tests**

Pré-requisito: `from unittest.mock import patch` no topo do arquivo de teste.

```python
class TestAutoRestart:
    def test_restart_agendado_quando_flag_ligada_e_update(
        self, client, auth_headers, tmp_path, monkeypatch
    ):
        from unittest.mock import patch

        _criar_zip_manifest(
            tmp_path,
            "projetos",
            {
                "module_name": "projetos",
                "entity_name": "Projeto",
                "schema_name": "org",
                "route_prefix": "/v1/projetos",
                "menu_label": "Projetos",
                "frontend_tabs": [
                    {"name": "Projetos", "url": "modules/projetos/index.html"}
                ],
            },
        )
        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )
        from app.core.config import settings

        monkeypatch.setattr(settings, "IMPORT_AUTO_RESTART", True)

        with (
            patch("scripts.import_module.import_module") as mock_import,
            patch("app.routers.import_router._is_update", return_value=True),
            patch("app.routers.import_router._restart_api") as mock_restart,
        ):
            mock_import.return_value = {
                "success": True,
                "steps": ["ok"],
                "updated": True,
            }
            response = client.post("/v1/import/projetos", headers=auth_headers)

        assert response.status_code == 200, response.text
        mock_restart.assert_called_once()

    def test_restart_nao_agendado_em_instalacao(
        self, client, auth_headers, tmp_path, monkeypatch
    ):
        # Mesma preparação do teste anterior (zip "projetos",
        # monkeypatch de _get_import_dir e IMPORT_AUTO_RESTART=True).
        _criar_zip_manifest(
            tmp_path,
            "projetos",
            {
                "module_name": "projetos",
                "entity_name": "Projeto",
                "schema_name": "org",
                "route_prefix": "/v1/projetos",
                "menu_label": "Projetos",
                "frontend_tabs": [
                    {"name": "Projetos", "url": "modules/projetos/index.html"}
                ],
            },
        )
        monkeypatch.setattr(
            "app.routers.import_router._get_import_dir", lambda: tmp_path
        )
        from app.core.config import settings

        monkeypatch.setattr(settings, "IMPORT_AUTO_RESTART", True)

        with (
            patch("scripts.import_module.import_module") as mock_import,
            patch("app.routers.import_router._is_update", return_value=False),
            patch("app.routers.import_router._restart_api") as mock_restart,
            patch("app.routers.import_router._run_migrations_background"),
        ):
            mock_import.return_value = {"success": True, "steps": ["ok"]}
            client.post("/v1/import/projetos", headers=auth_headers)

        mock_restart.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `make test-postgres`
Expected: FAIL — `IMPORT_AUTO_RESTART` não existe em `Settings` e `_restart_api` não existe.

- [ ] **Step 3: Implement**

1. `config.py`, seção `# --- Import de Módulos ---`: `IMPORT_AUTO_RESTART: bool = False`.
2. `import_router.py`: `_restart_api()` como descrito; endpoint recebe `background_tasks: BackgroundTasks`; após `result_data` de sucesso, `if settings.IMPORT_AUTO_RESTART and result_data.get("updated"): background_tasks.add_task(_restart_api)` e acrescentar aos steps `"API vai reiniciar para carregar o novo código"`.
3. `compose.yaml`, `api-postgres.environment`: adicionar `- IMPORT_AUTO_RESTART=true`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `make test-postgres`
Expected: PASS em `TestAutoRestart`. Nenhum teste pode enviar `SIGTERM` de verdade — `_restart_api` sempre patchado.

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/app/core/config.py apps/api-postgres/app/routers/import_router.py compose.yaml apps/api-postgres/tests/unit/test_import_router.py
git commit -m "feat: reinicia a api apos atualizar modulo" -m "Refs #7"
```

---

### Task 7: Botão "Atualizar" no Importador

**Files:**
- Modify: `apps/frontend-webapp/modules/importer/script.js:26-35`, `44-60`, `111-190`

**Interfaces:**
- Consumes: `POST /v1/import/{slug}` (Task 5) e o campo `version` de `GET /v1/import/scan`.
- Produces: `this.currentAction` (`'import' | 'update' | 'remove'`) e `abrirModalAtualizar(slug)`.

- [ ] **Step 1: Write the failing check**

Não há harness de testes JS no repo. Verificação por sintaxe + inspeção:

Run: `node --check apps/frontend-webapp/modules/importer/script.js`
Expected: sai com código 0 (hoje também passa — o teste real é a inspeção descrita abaixo).

- [ ] **Step 2: Implementar**

1. Coluna de ações da tabela de zips (`script.js:26-35`): quando `row.ja_importado`, renderizar
   `'<button class="btn btn-sm btn-primary" data-action="update" data-slug="..."><i class="fas fa-sync"></i> <span class="hide-mobile">Atualizar</span></button>'`
   no lugar do botão `remove`.
2. `handleActionClick`: `else if (action === 'update') this.abrirModalAtualizar(slug);`
3. `abrirModalAtualizar(slug)`: seta `this.currentAction = 'update'`, busca a versão em `this.modules` (`find(m => m.slug === slug)`), título `Atualizar Módulo`, corpo
   `Atualizar para a versão <version>? A aba, a ordem, as permissões e os dados serão preservados.`, botão `Atualizar`, e abre o modal (mesmo padrão de `abrirModalImportar`).
4. `abrirModalImportar` e `abrirModalRemover` passam a setar `this.currentAction` para `'import'` e `'remove'`.
5. `confirmarImport()`: trocar a detecção `isRemove` baseada no título por `var action = this.currentAction; var isRemove = action === 'remove';`; textos do botão `Removendo.../Importando.../Atualizando...`; mensagem final por action (`Módulo atualizado com sucesso!`); a chamada HTTP já é `delete` para remove e `post` para os demais.

- [ ] **Step 3: Verify**

Run: `node --check apps/frontend-webapp/modules/importer/script.js`
Expected: código 0. Conferir por leitura que nenhuma referência a `data-action="remove"` sobrou na tabela de zips (o remover continua na tabela de instalados).

- [ ] **Step 4: Commit**

```bash
git add apps/frontend-webapp/modules/importer/script.js
git commit -m "feat: botao atualizar no importador" -m "Refs #7"
```

---

### Task 8: Documentação

**Files:**
- Modify: `docs/IMPORTACAO.md` (nova seção "Atualizar módulo")
- Modify: `docs/API.md` (endpoint de import: comportamento de atualização)
- Modify: `AGENTS.md` (linha do import: mencionar atualização e `IMPORT_AUTO_RESTART`)

**Interfaces:** nenhuma; apenas texto.

- [ ] **Step 1: Escrever a seção em `docs/IMPORTACAO.md`**

Cobrir: botão "Atualizar" na lista de zips; o que é preservado (aba, ordem, role mínima, permissões, dados, migrations aplicadas); o que muda (arquivos, versão, migrations novas); falha de migration devolve erro e não altera o que já estava aplicado; `IMPORT_AUTO_RESTART=true` reinicia o container após atualização (fora do container é restart manual).

- [ ] **Step 2: Atualizar `docs/API.md`**

No endpoint `POST /v1/import/{module}`: quando o módulo já existe, a resposta traz `message: "Módulo atualizado com sucesso."`, migrations rodam antes da resposta e falha retorna `success: false` com o erro do alembic.

- [ ] **Step 3: Atualizar `AGENTS.md`**

Na seção de import/módulos, uma linha: atualização reaproveita `POST /v1/import/{module}` preservando `portal.modulos`/`usuario_modulo`, e `IMPORT_AUTO_RESTART` controla o restart no container.

- [ ] **Step 4: Commit**

```bash
git add docs/IMPORTACAO.md docs/API.md AGENTS.md
git commit -m "docs: atualizacao de modulo e restart automatico" -m "Refs #7"
```

---

### Task 9: Verificação final da branch

**Files:** nenhum (só verificação).

- [ ] **Step 1: Rodar a suíte completa**

Run: `make test-all`
Expected: todos os testes passam (inclui postgres, sqlserver, shared, raiz e agente).

- [ ] **Step 2: Formatar e lintar**

Run: `ruff format packages/ apps/` e depois `ruff check --fix . && ruff check .`
Expected: `All checks passed!`

- [ ] **Step 3: Conferir que nada escreve no portal**

Run: `git diff main -- apps/api-postgres/scripts/import_module.py apps/api-postgres/app/routers/import_router.py | rg "Modulo|UsuarioModulo|portal"` (no Windows: `git diff main -- ... | Select-String "Modulo|UsuarioModulo|portal"`)
Expected: nenhuma ocorrência nova de escrita em `Modulo`/`UsuarioModulo`.

- [ ] **Step 4: Commit de formatação, se houver mudanças**

```bash
git add -A
git commit -m "style: ruff format" -m "Refs #7"
```
