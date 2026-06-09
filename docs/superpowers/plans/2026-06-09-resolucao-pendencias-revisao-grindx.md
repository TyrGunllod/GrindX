# Resolução de Pendências REVISAO-GRINDX — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir 9 pendências identificadas na revisão técnica v1.18.0: 3 bugs, 3 docs desatualizadas e 5 melhorias de qualidade.

**Architecture:** Correções pontuais em arquivos específicos sem alteração de arquitetura. Três fases independentes: bugs (funcional), docs (informacional), melhorias (qualidade). Itens sem dependência entre fases.

**Tech Stack:** Python/FastAPI, Vanilla JS, Alembic, pytest, semantic-release

---

### Task 1: B-01 — Remover slowapi duplicado

**Files:**
- Modify: `apps/api-postgres/requirements.txt:31`

- [ ] **Step 1: Remover a linha duplicada**

```txt
Linha 31: slowapi>=0.1.9  ← remover esta linha
```

- [ ] **Step 2: Verificar**

Run: `rg -n "slowapi" apps/api-postgres/requirements.txt`
Expected: exatamente 1 ocorrência (linha 21)

- [ ] **Step 3: Commit**

```bash
git add apps/api-postgres/requirements.txt
git commit -m "fix: remover slowapi duplicado no requirements.txt"
```

---

### Task 2: B-02 — Corrigir APP_VERSION

**Files:**
- Modify: `apps/api-postgres/app/core/config.py:16`
- Modify: `apps/api-sqlserver/app/core/config.py:14`

- [ ] **Step 1: Mudar APP_VERSION em api-postgres**

Editar linha 16 de `"1.15.0"` para `"1.18.0"`

- [ ] **Step 2: Mudar APP_VERSION em api-sqlserver**

Editar linha 14 de `"1.15.0"` para `"1.18.0"`

- [ ] **Step 3: Verificar tags git**

Run: `git log --oneline --tags`
Expected: tags `v1.16.0`, `v1.17.0`, `v1.18.0` existem

Se não existirem, criar manualmente apontando para os commits correspondentes conforme CHANGELOG.md:
```bash
git tag v1.16.0 <commit-hash>
git tag v1.17.0 <commit-hash>
git tag v1.18.0 <commit-hash>
```

- [ ] **Step 4: Commit**

```bash
git add apps/api-postgres/app/core/config.py apps/api-sqlserver/app/core/config.py
git commit -m "fix: atualizar APP_VERSION para 1.18.0"
```

---

### Task 3: B-03 — Corrigir contradição SEC-07 no STATE.md

**Files:**
- Modify: `.planning/STATE.md:99-101`

- [ ] **Step 1: Remover SEC-07 da tabela Deferred Items**

Remover a linha:
```md
| Security | Path traversal protection (SEC-07) | Deferred to v2 | Phase 1 discuss |
```

- [ ] **Step 2: Commit**

```bash
git add .planning/STATE.md
git commit -m "fix: remover SEC-07 dos itens adiados no STATE.md"
```

---

### Task 4: D-01 — Atualizar MAPA-ARQUIVOS.md

**Files:**
- Modify: `docs/MAPA-ARQUIVOS.md`

- [ ] **Step 1: Atualizar estrutura de diretórios**

Substituir referências de `packages/` por `apps/` em toda a seção de estrutura. Adicionar:
- Módulos frontend: `admin-skins`, `importer`
- `assets/` com favicon.ico, favicon.svg, favicon.png
- `shared/fonts/` (DM Sans, Barlow Condensed)
- `skins/` (grindx-default.json, royal-purple.json)

- [ ] **Step 2: Commit**

```bash
git add docs/MAPA-ARQUIVOS.md
git commit -m "docs: atualizar MAPA-ARQUIVOS com estrutura atual"
```

---

### Task 5: D-02 — Atualizar SETUP.md

**Files:**
- Modify: `docs/SETUP.md`

- [ ] **Step 1: Atualizar paths de instalação**

Substituir todos os caminhos:
- `packages/api-postgres/` → `apps/api-postgres/`
- `packages/api-sqlserver/` → `apps/api-sqlserver/`
- `packages/frontend-webapp/` → `apps/frontend-webapp/`

- [ ] **Step 2: Commit**

```bash
git add docs/SETUP.md
git commit -m "docs: atualizar SETUP com paths apps/"
```

---

### Task 6: D-03 — Atualizar API.md

**Files:**
- Modify: `docs/API.md`

- [ ] **Step 1: Remover endpoints obsoletos**

Remover documentação de:
- `GET /v1/produtos/`
- `POST /v1/produtos/`
- `PUT /v1/produtos/{id}`
- `DELETE /v1/produtos/{id}`

- [ ] **Step 2: Adicionar novos endpoints**

Adicionar documentação com schemas de request/response:
- `GET /v1/themes/` — listar temas
- `POST /v1/themes/` — criar tema
- `POST /v1/import/scan` — escanear ZIP de módulo
- `POST /v1/import/{slug}` — importar módulo

- [ ] **Step 3: Commit**

```bash
git add docs/API.md
git commit -m "docs: atualizar API.md com endpoints atuais"
```

---

### Task 7: M-01 — Separar requirements dev/prod

**Files:**
- Modify: `apps/api-postgres/requirements.txt`
- Create: `apps/api-postgres/requirements-dev.txt`

- [ ] **Step 1: Remover deps de desenvolvimento do requirements.txt**

Remover as linhas:
```
# === Testes ===
pytest>=8.0.0
pytest-asyncio>=0.23.5
httpx>=0.27.0
pytest-cov>=6.0.0

# === Qualidade ===
ruff>=0.3.0
```

- [ ] **Step 2: Criar requirements-dev.txt**

```
-r requirements.txt

# === Testes ===
pytest>=8.0.0
pytest-asyncio>=0.23.5
httpx>=0.27.0
pytest-cov>=6.0.0

# === Qualidade ===
ruff>=0.3.0
```

- [ ] **Step 3: Commit**

```bash
git add apps/api-postgres/requirements.txt apps/api-postgres/requirements-dev.txt
git commit -m "refactor: separar dependencias dev/prod no api-postgres"
```

---

### Task 8: M-02 — Adicionar coverage threshold ao Jenkinsfile

**Files:**
- Modify: `Jenkinsfile:44,52,60,67`

- [ ] **Step 1: Adicionar --cov-fail-under=70 aos comandos pytest**

Em cada `dir()` block (api-postgres, api-sqlserver, shared, root), adicionar `--cov=app --cov-fail-under=70`:

```
sh 'PYTHONPATH=../../packages python3 -m pytest tests/ -v --tb=short --strict-markers --cov=app --cov-fail-under=70'
```

- [ ] **Step 2: Commit**

```bash
git add Jenkinsfile
git commit -m "ci: adicionar coverage threshold 70% ao Jenkinsfile"
```

---

### Task 9: M-03 — Tornar config.js injetável

**Files:**
- Modify: `apps/frontend-webapp/shared/config.js`

- [ ] **Step 1: Modificar config.js para aceitar injeção**

```js
window.GRINDX_CONFIG = {
  // URL base da API — usa variavel injetada ou fallback para dev
  API_BASE_URL: window.__GRINDX_API_URL || "http://localhost:8002/v1",
};
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/shared/config.js
git commit -m "feat: tornar API_BASE_URL injetavel via window.__GRINDX_API_URL"
```

---

### Task 10: M-04 — Renomear migrações inconsistentes

**Files:**
- Rename: `apps/api-postgres/alembic/versions/02_add_org_schema_tables.py` → `apps/api-postgres/alembic/versions/007_add_org_schema_tables.py`
- Rename: `apps/api-postgres/alembic/versions/2026_06_02_add_temp_password_fields.py` → `apps/api-postgres/alembic/versions/008_add_temp_password_fields.py`
- Read (no modify): conteúdo interno das migrações para verificar `revision` e `down_revision`

- [ ] **Step 1: Verificar identities das migrações**

```bash
head -5 apps/api-postgres/alembic/versions/02_add_org_schema_tables.py
head -5 apps/api-postgres/alembic/versions/2026_06_02_add_temp_password_fields.py
```

Confirmar que `down_revision` está correto (aponta para `006_add_performance_indexes` e `007_...` respectivamente). Não alterar `revision` interna — apenas nome do arquivo.

- [ ] **Step 2: Renomear arquivos**

```bash
git mv apps/api-postgres/alembic/versions/02_add_org_schema_tables.py apps/api-postgres/alembic/versions/007_add_org_schema_tables.py
git mv apps/api-postgres/alembic/versions/2026_06_02_add_temp_password_fields.py apps/api-postgres/alembic/versions/008_add_temp_password_fields.py
```

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor: renomear migracoes para padrao sequencial"
```

---

### Task 11: M-05 — Sincronizar version.json automaticamente

**Files:**
- Modify: `apps/frontend-webapp/version.json`
- Modify: `.github/workflows/release.yml`
- Verify (no modify): `pyproject.toml` (build_command já configurado)
- Verify (no modify): `scripts/update_frontend_version.py`

- [ ] **Step 1: Validar que update_frontend_version.py funciona**

```bash
cd D:\_Projetos\GrindX
python scripts/update_frontend_version.py
type apps/frontend-webapp/version.json
```

Expected: `{"version": "v1.18.0"}` (deve refletir o APP_VERSION corrigido na Task 2)

- [ ] **Step 2: Adicionar step explícito no CI após semantic-release**

No `.github/workflows/release.yml`, no job `release`, após o step `Run semantic release`:

```yaml
      - name: Gerar version.json
        run: python scripts/update_frontend_version.py

      - name: Commit version.json
        run: |
          git add apps/frontend-webapp/version.json
          git commit -m "chore(release): update version.json" || true
```

- [ ] **Step 3: Verificar resultado final**

```bash
python scripts/update_frontend_version.py
cat apps/frontend-webapp/version.json
```

Expected: version.json com o mesmo valor de APP_VERSION nos config.py

- [ ] **Step 4: Commit**

```bash
git add apps/frontend-webapp/version.json .github/workflows/release.yml
git commit -m "fix: sincronizar version.json automaticamente no release"
```

---

### Task 12: Verificação final

- [ ] **Step 1: Ruff check**

```bash
ruff check packages/ apps/ --select E,F,I --ignore E501
```
Expected: sem erros

- [ ] **Step 2: Ruff format**

```bash
ruff format packages/ apps/ --check
```
Expected: sem diferenças

- [ ] **Step 3: Rodar testes**

```bash
cd apps/api-postgres
set PYTHONPATH=..\..\packages
.\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short
```
Expected: todos passando
