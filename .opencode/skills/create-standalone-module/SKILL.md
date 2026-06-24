---
name: create-standalone-module
description: Use when creating new GrindX modules that must be developed and tested independently outside the monorepo, then exported via export.py. Covers backend (FastAPI/SQLAlchemy), frontend (vanilla JS), self-contained tests, Alembic migration, and self-registration.
---

# Create Standalone Module — GrindX

Desenvolver módulos GrindX **fora do monorepo** (ex: `Project_Management/modulo-{nome}/`),
testar isoladamente, exportar via `export.py` apenas após testes verdes.

## Tech Stack Questionnaire (Perguntar Primeiro)

Antes dos parâmetros do módulo, **sempre pergunte qual padrão de frontend e banco** o usuário deseja:

**"Qual padrão de frontend e banco de dados você quer usar para este módulo?"**

| Opção | Frontend | CSS | JS | Banco | Backend | GrindX API |
|-------|----------|-----|----|-------|---------|------------|
| **(A) Padrão GrindX** (Recomendado) | HTML puro | CSS puro (`var(--...)`, Grid, Flex) | Vanilla JS (fetch, template strings, delegated events) | PostgreSQL (via SQLAlchemy + Alembic) | FastAPI + SQLAlchemy | `api-postgres` |
| **(A2) GrindX + SQL Server** | HTML puro | CSS puro | Vanilla JS | SQL Server (via pyodbc, raw SQL) | FastAPI + SQLAlchemy | `api-sqlserver` |
| **(B) Outro padrão** | Especificar | Especificar | Especificar | Especificar | Especificar | Especificar |

- Se escolher **(A)**, siga os templates padrão (exporta para `api-postgres`).
- Se escolher **(A2)**, mesmo frontend, SQL Server com raw SQL (sem ORM/Alembic). Exporta para `api-sqlserver`.
- Se escolher **(B)**, pergunte detalhadamente e adapte os templates.

## Parameter Questionnaire

Após definir o padrão de tech stack, pergunte ao usuário cada parâmetro abaixo.

| # | Parâmetro | Pergunta | Exemplo | Padrão |
|---|-----------|----------|---------|--------|
| 1 | `module_name` | Nome em snake_case | `recurso` | — |
| 2 | `entity_name` | Nome da entidade em PascalCase | `Recurso` | — |
| 3 | `schema_name` | Schema PostgreSQL (`org`, `catalogo`, `portal`) | `org` | `org` |
| 4 | `table_name` | Nome da tabela (plural) | `recursos` | `{module_name}s` |
| 5 | `route_prefix` | Prefixo da URL com `/v1/` | `/v1/recursos` | `/v1/{module_name}s` |
| 6 | `route_api` | Caminho sem barra inicial | `v1/recursos` | `{route_prefix}` sem `/` |
| 7 | `route_tag` | Tag Swagger | `"Recursos"` | `"{entity_name}"` |
| 8 | `frontend_prefix` | Prefixo abreviado p/ sub-módulos | `gp` | Primeiras letras |
| 9 | `frontend_tabs` | Array de abas (name, url, menu_icone, order) | Ver abaixo | — |
| 10 | `menu_label` | Rótulo do menu lateral | `"Gestão de Projetos"` | `{entity_name}` |

**Exemplo de `frontend_tabs`:**
```json
{
  "frontend_tabs": [
    {"name": "Dashboard", "url": "modules/gp_dashboard/index.html", "menu_icone": "chart-bar", "order": 1},
    {"name": "Projetos", "url": "modules/gp_projeto/index.html", "menu_icone": "folder", "order": 2}
  ]
}
```

### Parâmetro extra: `{target_api}`

Baseado na escolha do Tech Stack:
- (A) → `target_api = "postgres"`, `api_dir = "api-postgres"`
- (A2) → `target_api = "sqlserver"`, `api_dir = "api-sqlserver"`

### Parameters Template (use em todos os placeholders)

- `{module_name}` — snake_case
- `{entity_name}` — PascalCase
- `{entity_name_lower}` — lowercase
- `{schema_name}` — org/catalogo/portal
- `{schema|pascal}` — PascalCase schema: org→Org, catalogo→Catalogo
- `{base_class}` — `{schema|pascal}Base`
- `{table_name}` — plural snake_case
- `{route_prefix}` — URL prefix
- `{route_tag}` — Swagger tag
- `{menu_label}` — menu display name
- `{route_api}` — API path
- `{frontend_prefix}` — prefixo abreviado (ex: gp)
- `{frontend_tabs}` — array de abas

## Directory Structure

### Padrão PostgreSQL (opção A)

```
Project_Management/modulo-{module_name}/
├── module.json                                 # Templates/postgres/module.json
├── app/modules/{module_name}/
│   ├── __init__.py
│   ├── base.py                                 # Templates/postgres/base.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── {module_name}.py                    # Templates/postgres/model.py
│   ├── schemas/
│   │   ├── __init__.py                         # Templates/shared/backend/init_schemas.py
│   │   └── {module_name}.py                    # Templates/shared/backend/schema.py
│   ├── repositories/
│   │   ├── __init__.py                         # Templates/shared/backend/init_repositories.py
│   │   └── {module_name}_repository.py         # Templates/shared/backend/repository.py
│   ├── services/
│   │   ├── __init__.py                         # Templates/shared/backend/init_services.py
│   │   └── {module_name}_service.py            # Templates/shared/backend/service.py
│   ├── routers/
│   │   ├── __init__.py                         # Templates/shared/backend/init_routers.py
│   │   └── {module_name}_router.py             # Templates/shared/backend/router.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                         # Templates/shared/tests/conftest.py
│   │   ├── test_{module_name}_unit.py          # Templates/shared/tests/test_unit.py
│   │   └── test_{module_name}_integration.py   # Templates/shared/tests/test_integration.py
│   ├── export.py                               # Templates/shared/export.py
│   └── README.md
├── frontend/
│   ├── {frontend_prefix}_{tab1}/
│   │   ├── index.html, script.js, style.css    # Templates/shared/frontend/*
│   └── shared/
│       └── core.css
├── migration/
│   └── {revision}_{table_name}.py              # Templates/postgres/migration.py
├── Makefile, requirements.txt, pytest.ini, run_tests.ps1  # Templates/shared/support/*
```

### Padrão SQL Server (opção A2) — Diferenças

- ❌ **Sem** `base.py`, `models/`, `migration/` (sem ORM, sem schema para gerenciar)
- ❌ **Sem** `conftest.py`, `test_integration.py` (mock do Protheus em vez de SQLite)
- ✏️ `module.json` — adiciona `target_api: "sqlserver"` → `templates/sqlserver/module.json`
- ✏️ `export.py` — aponta para `api-sqlserver`, pula migration/dependency/alembic
- ✏️ `routers/{module_name}_router.py` — factory inline (padrão atual)
- ✏️ `repositories/` — usa `text()` da SQLAlchemy, não models
- 🆕 `exceptions.py` — exceções específicas do domínio

## 1. Backend — Criar Todos os Arquivos

> **Se `target_api == "sqlserver"`: PULE os itens 1.1 (base.py) e 1.2 (Model). Crie `exceptions.py` (item 1.8) em vez disso.**

### 1.1 base.py
Use template: `templates/postgres/base.py`
Substitua `{entity_name}`, `{schema_name}`.

### 1.2 Model — `models/{module_name}.py`
Use template: `templates/postgres/model.py`
Substitua `{module_name}`, `{entity_name}`, `{table_name}`.
- Adicione FKs com `ForeignKey("schema.tabela.id")` conforme necessário
- Adicione `UniqueConstraint` no `__table_args__` conforme necessário

### 1.3 Schemas — `schemas/{module_name}.py`
Use template: `templates/shared/backend/schema.py`
Substitua `{entity_name}`, `{module_name}`.
- Adicione `field_validator` para validações customizadas conforme necessário

### 1.4 Repository — `repositories/{module_name}_repository.py`
Use template: `templates/shared/backend/repository.py`
Substitua `{module_name}`, `{entity_name}`.
- Adicione métodos de busca customizada (ex: `buscar_por_nome`) conforme necessário

### 1.5 Service — `services/{module_name}_service.py`
Use template: `templates/shared/backend/service.py`
Substitua `{module_name}`, `{entity_name}`.
- `NotFoundError` recebe dois argumentos posicionais `(resource, identifier)`, NÃO string
- Adicione validação de conflito no `criar()` conforme necessário (ex: checar duplicata por nome)

### 1.6 Router — `routers/{module_name}_router.py`
Use template: `templates/shared/backend/router.py`
Substitua `{module_name}`, `{entity_name}`, `{route_prefix}`, `{route_tag}`.

**Dual-context authentication:**
- **GrindX**: usa `app.database.get_db` (SQLAlchemy session) + JWT auth (`get_current_user`)
- **Standalone**: usa `app.core.database_protheus.get_db_protheus` + API key auth (`verify_api_key`)
- Ambos injetados via `Depends()` — FastAPI resolve automaticamente via try/except

### 1.7 `__init__.py` files
Use templates:
- `schemas/__init__.py` → `templates/shared/backend/init_schemas.py`
- `repositories/__init__.py` → `templates/shared/backend/init_repositories.py`
- `services/__init__.py` → `templates/shared/backend/init_services.py`
- `routers/__init__.py` → `templates/shared/backend/init_routers.py`

Substitua `{module_name}`, `{entity_name}`.

### 1.8 `exceptions.py` (sqlserver apenas)
Se `target_api == "sqlserver"`, crie `app/modules/{module_name}/exceptions.py` com exceções específicas do domínio (ex: `ProtheusConnectionError`, `{entity_name}NotFoundError`).

## 2. Tests

> **Se `target_api == "sqlserver"`: PULE conftest.py e test_integration.py. Módulos sqlserver não têm banco local para testar (usam mock do Protheus).**

### 2.1 `tests/conftest.py`
Use template: `templates/shared/tests/conftest.py`
Substitua `{module_name}`, `{entity_name}`.
- Requer `GRINDX_PACKAGES` apontando para `packages/` do GrindX
- Usa `importlib.util` para injetar módulo local no namespace `app.modules.*`
- SQLite in-memory com `schema_translate_map` para simular schemas PostgreSQL

### 2.2 `tests/test_{module_name}_unit.py`
Use template: `templates/shared/tests/test_unit.py`
Substitua `{module_name}`, `{entity_name}`.
- Testes com `MagicMock` para mockar repository
- Cobre: buscar (encontrado/não encontrado), criar, atualizar, desativar

### 2.3 `tests/test_{module_name}_integration.py`
Use template: `templates/shared/tests/test_integration.py`
Substitua `{module_name}`, `{entity_name}`.
- Testes com SQLite real via fixtures do conftest
- Cobre: repository CRUD, service buscar/listar

## 3. Frontend

> **Mobile-first:** CSS base para telas pequenas, `@media (min-width: 768px)` para desktop. Elementos interativos: mínimo 44px de altura.
>
> **Siga o padrão escolhido no Tech Stack Questionnaire.**
>
> Se **(A) Padrão GrindX**, use templates abaixo. Se **(B)**, adapte.

### 3.1 `style.css` — Mobile-first, herda skins
Use template: `templates/shared/frontend/style.css`

**Regras:**
- Usar exclusivamente `var(--...)` para cores, fontes, espaçamentos — nunca cores fixas
- CSS base = mobile; `@media (min-width: 768px)` para desktop
- Tabelas viram cards no mobile: use `data-label` nos `<td>` para `::before`
- Modal usa `modal-overlay` + `modal-card` (NÃO `<dialog>` nativo)
- Testar visualmente com pelo menos 2 skins antes de exportar

### 3.2 `index.html` e `script.js`
Use templates:
- `templates/shared/frontend/index.html` — estrutura HTML
- `templates/shared/frontend/script.js` — JS com API calls + dual-context auth

**Regras HTML:**
- HTML5 semântico, zero dependências externas (sem CDN, sem bibliotecas)
- `<meta name="viewport" content="width=device-width, initial-scale=1.0">` obrigatório
- Incluir `<script src="../../shared/app.js"></script>` no `<head>` para `window.grindx.session`
- Modais com `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
- `data-label` em `<td>` para CSS mobile

**Estrutura padrão do modal:**
```html
<div class="modal-overlay" id="modal-id" role="dialog" aria-modal="true" aria-labelledby="modal-title" style="display: none;">
  <div class="modal-card">
    <header class="modal-header flex justify-between">
      <h3 id="modal-title">Título</h3>
      <button class="btn-icon" id="close-modal" aria-label="Fechar">&times;</button>
    </header>
    <form id="form-id" class="grid grid-md-2">
      <!-- campos do formulário -->
    </form>
    <footer class="modal-footer flex justify-end gap-2">
      <button type="button" class="btn" id="btn-cancel">Cancelar</button>
      <button type="button" class="btn btn-primary" id="btn-save">Salvar</button>
    </footer>
  </div>
</div>
```

**Regras JS:**
- NUNCA importar bibliotecas externas (React, Vue, jQuery, Axios)
- NUNCA usar TypeScript — apenas JS puro
- `_fetch()` com detecção de contexto: `window.grindx.session` (JWT) vs `API_KEY`
- `downloadFromUrl()` para PDF/binários com fallback para `?api_key=` (standalone)
- Eventos via delegated event bubbling no container pai
- Ciclo de vida: `DOMContentLoaded` → `init()` → carregar dados → renderizar

**Dual-context auth:**
- **GrindX**: `window.grindx.session.getToken()` → `Authorization: Bearer {token}`
- **Standalone**: `X-API-Key` header; PDFs usam `?api_key=` query param
- **NÃO usar `window.grindx.api`** — aponta para api-postgres (porta 8002), não api-sqlserver

## 4. Migration

> **Se `target_api == "sqlserver"`: PULE esta seção inteira.**

Use template: `templates/postgres/migration.py`
Substitua `{table_name}`, `{schema_name}`.
- Gere revision ID único (ex: via `alembic revision --autogenerate` ou timestamp manual)
- Ajuste `down_revision` conforme o histórico do Alembic

## 5. Support Files

Use templates em `templates/shared/support/`:
- **`run_tests.ps1`** → `templates/shared/support/run_tests.ps1` — script para rodar testes com `GRINDX_PACKAGES`
- **`requirements.txt`** → `templates/shared/support/requirements.txt` — pytest, sqlalchemy, pydantic, structlog, fastapi
- **`pytest.ini`** → `templates/shared/support/pytest.ini` — config testpaths
- **`Makefile`** → `templates/shared/support/Makefile` — targets: test, test-unit, test-integration, package, export, dry-run, import, clean, help

Substitua `{module_name}`, `{entity_name}`.

## 6. Manifesto (`module.json`)

**Se `target_api == "postgres"`:**
Use template: `templates/postgres/module.json`

**Se `target_api == "sqlserver"`:**
Use template: `templates/sqlserver/module.json` (inclui `target_api: "sqlserver"` e `role_minima: "leitura"`)

**Campos do `frontend_tabs`:**
- `name`: Nome exibido no menu
- `url`: Caminho relativo a `frontend-webapp/modules/`
- `menu_icone`: Nome do ícone (Font Awesome sem `fa-`)
- `order`: Ordem de exibição

**Nota:** O `register_menu` apenas loga informações. Associar abas manualmente no Portal → Estrutura após importação.

## 7. export.py

Use template: `templates/shared/export.py`
Substitua `{module_name}`, `{entity_name}`.

### Adaptação para `target_api`

| Configuração | `postgres` (padrão) | `sqlserver` |
|---|---|---|
| `GRINDX_API` | `apps/api-postgres` | `apps/api-sqlserver` |
| Chamar `register_dependency()`? | Sim | **Não** |
| Chamar `register_alembic_import()`? | Sim | **Não** |
| Chamar `copy_migration()`? | Sim | **Não** |
| Chamar `run_migrations()`? | Sim | **Não** |
| Incluir `migration/` no zip? | Sim | **Não** |

No template, altere: `GRINDX_API = GRINDX_ROOT / "apps" / "api-postgres"` → `GRINDX_ROOT / "apps" / "api-sqlserver"` (sqlserver). O método `export()` já usa `is_sqlserver` para pular condicionalmente.

## 8. Execution / Test Workflow

### PostgreSQL (opção A)

```powershell
# 1. Criar estrutura do módulo (seguir templates acima)
# 2. Rodar testes
make test
$env:GRINDX_PACKAGES = "D:\\_Projetos\\GrindX\\packages"
python -m pytest app/modules/{module_name}/tests/ -v
# Esperado: 10+ testes PASS

# 3. Gerar pacote .zip
make package

# 4. Importar no GrindX
make import
# Via API: POST /v1/import/{module_name}
# Via frontend: Gestão → Importar Módulos
```

### SQL Server (opção A2)

```powershell
# Steps 1-3: idênticos
# 4. Importar especificando target_api
python D:\_Projetos\GrindX\apps\api-postgres\scripts\import_module.py {module_name} --target-api=sqlserver --import-dir=D:\_Projetos\GrindX\import

# 5. Verificar no api-sqlserver
cd D:\\_Projetos\\GrindX\\packages\\api-sqlserver
pytest tests/ -k {module_name} -v
```

## Registration Checklist

### PostgreSQL (opção A)

- [ ] **Tech Stack definido**: Padrão GrindX (HTML puro + CSS puro + Vanilla JS + PostgreSQL)
- [ ] **Frontend prefix definido**: Prefixo abreviado para sub-módulos (ex: `gp`)
- [ ] **Frontend tabs definido**: Array de abas com name, url, menu_icone, order
- [ ] Backend: base, model, schemas, repository, service, router + __init__.py
- [ ] **Router dual-context**: try/except para `get_db`/`get_current_user` (GrindX) vs `get_db_protheus`/`verify_api_key` (standalone)
- [ ] **Frontend dual-context**: `_fetch()` e `downloadFromUrl()` com detecção `window.grindx.session` + `index.html` inclui `app.js`
- [ ] **PDF opcional**: se módulo gera PDF, instalar `xhtml2pdf` no venv do GrindX
- [ ] Tests: conftest.py, unit tests (mocked repo), integration tests (SQLite)
- [ ] Migration: Alembic migration file (PostgreSQL)
- [ ] Support: requirements.txt, pytest.ini, run_tests.ps1, Makefile
- [ ] Testes passam: `pytest app/modules/{module_name}/tests/ -v`
- [ ] `module.json` criado na raiz do standalone com `frontend_tabs` array
- [ ] `export.py`: usa `STANDALONE_ROOT` para paths de frontend, migration e dist
- [ ] `export.py`: `--dry-run` simula sem alterar GrindX

### SQL Server (opção A2) — Diferenças

- [ ] **Sem** `base.py`, `models/`, `migration/`
- [ ] **Adicionar** `exceptions.py` com exceções específicas do domínio
- [ ] **`module.json`**: incluir `"target_api": "sqlserver"` e `"role_minima": "leitura"`
- [ ] **`export.py`**: `GRINDX_API` aponta para `apps/api-sqlserver`; pula migration/dependency/alembic
- [ ] **Router**: factory inline (já é o padrão); não usa `auth/dependencies.py`
- [ ] **Repository**: SQL raw via `text()`, sem models SQLAlchemy
- [ ] **Tests**: sem `conftest.py` (mock do Protheus); sem `test_integration.py`
- [ ] **Pós-importação**: Associar abas manualmente no Portal → Estrutura

---

> **Nota de manutenção:** Templates extraídos para `templates/`. Cada template usa `{placeholders}` para substituição. Mantenha este SKILL.md focado em workflow + lógica condicional (~300-400 linhas). Ao adicionar novo template, crie o arquivo em `templates/` e referencie-o aqui com uma linha.
