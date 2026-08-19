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

> **Pasta `shared` do frontend**: o módulo referencia `/shared/core.css`, `/shared/config.js` e `/shared/app.js` (caminho absoluto a partir da raiz da webapp). No GrindX isso usa a **`shared` padrão**; a pasta `shared/` dentro do frontend é **apenas fallback standalone** (para `make dev-frontend`) e **não é copiada** no export/package. O `version.js` é específico do módulo e fica na **raiz** de cada frontend (carregado como `version.js`).

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
| 11 | `menu_description` | Subtítulo do header da página | `"Gerencie projetos e tarefas"` | `"Gerencie {entity_name_lower} do sistema"` |
| 12 | `migration_start_number` | Número inicial da migration (3 dígitos, evita colisão) | `"100"` | `"100"` |

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
- `{menu_description}` — subtítulo do header
- `{migration_start_number}` — número inicial da migration (3 dígitos, padrão 100)
- `{module_upper}` — `{module_name}` em MAIÚSCULAS (ex: pop_viz → POP_VIZ); usado no global JS de versão (`window.{module_upper}_VERSION`)

## Directory Structure

### Padrão PostgreSQL (opção A)

```
Project_Management/modulo-{module_name}/
├── module.json                                 # Templates/postgres/module.json
├── app/
│   ├── __init__.py                             # Templates/shared/standalone/app_init.py
│   ├── main.py                                 # Templates/shared/standalone/main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                           # Templates/shared/standalone/config.py
│   │   ├── database_protheus.py                # Templates/shared/standalone/database_protheus.py
│   │   └── auth.py                             # Templates/shared/standalone/auth.py
│   └── modules/
│       ├── iam/
│       │   ├── __init__.py
│       │   └── base.py                         # Templates/shared/standalone/iam_base.py
│       └── {module_name}/
│           ├── __init__.py
│           ├── base.py                         # Templates/postgres/base.py
│           ├── models/
│           │   ├── __init__.py
│           │   └── {entity_name_lower}.py                   # Templates/postgres/model.py
│           ├── schemas/
│           │   ├── __init__.py                 # Templates/shared/backend/init_schemas.py
│           │   └── {module_name}.py            # Templates/shared/backend/schema.py
│           ├── repositories/
│           │   ├── __init__.py                 # Templates/shared/backend/init_repositories.py
│           │   └── {module_name}_repository.py # Templates/shared/backend/repository.py
│           ├── services/
│           │   ├── __init__.py                 # Templates/shared/backend/init_services.py
│           │   └── {module_name}_service.py    # Templates/shared/backend/service.py
│           ├── routers/
│           │   ├── __init__.py                 # Templates/shared/backend/init_routers.py
│           │   └── {module_name}_router.py     # Templates/shared/backend/router.py
│           ├── tests/
│           │   ├── __init__.py
│           │   ├── conftest.py                 # Templates/shared/tests/conftest.py
│           │   ├── test_{module_name}_unit.py  # Templates/shared/tests/test_unit.py
│           │   └── test_{module_name}_integration.py  # Templates/shared/tests/test_integration.py
│           ├── export.py                       # Templates/shared/export.py
│           └── README.md
├── shared/
│   ├── __init__.py
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── base.py                             # Templates/shared/standalone/shared_exceptions.py
│   └── schemas/
│       ├── __init__.py
│       └── base.py                             # Templates/shared/standalone/shared_schemas.py
├── frontend/
│   ├── {frontend_prefix}_{tab1}/
│   │   ├── index.html, script.js, style.css    # Templates/shared/frontend/*
│   │   ├── version.js                           # Templates/shared/frontend/version.js (raiz do frontend)
│   │   ├── shared/                              # fallback APENAS standalone — NÃO copiado no export/package
│   │   │   ├── core.css                         # Templates/shared/frontend/shared/core.css
│   │   │   └── app.js                           # Templates/shared/frontend/shared/app.js
│   │   └── (style.css importa /shared/core.css)
│   └── ...
├── scripts/
│   └── version.py                               # Templates/shared/scripts/version.py
├── CHANGELOG.md                                 # Gerado por scripts/version.py
├── migration/
│   └── {revision}_{table_name}.py              # Templates/postgres/migration.py
├── AGENTS.md                                   # Templates/shared/AGENTS.md
├── .env.example                                # Templates/shared/standalone/env_example
├── .gitignore                                  # Templates/shared/standalone/gitignore
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

## 1.0 Standalone Prerequisites

Antes de criar o módulo, crie os arquivos de suporte standalone que permitem rodar sem o GrindX:

### `app/__init__.py` → `templates/shared/standalone/app_init.py`
Pacote `app` (vazio).

### `app/main.py` → `templates/shared/standalone/main.py`
FastAPI app que importa e registra o router do módulo. Substitua `{module_name}`.

### `app/core/config.py` → `templates/shared/standalone/config.py`
Carrega `.env` via `python-dotenv`, expõe `DATABASE_URL`.

### `app/core/database_protheus.py` → `templates/shared/standalone/database_protheus.py`
Engine SQLAlchemy + `get_db_protheus()`. Usa `DATABASE_URL` do config.

### `app/core/auth.py` → `templates/shared/standalone/auth.py`
`verify_api_key()` stub — aceita qualquer `X-API-Key` header.

### `app/modules/iam/base.py` → `templates/shared/standalone/iam_base.py`
Stub local: `metadata`, `reg`, `IamBase`. Substitui dependência do GrindX.

### `shared/exceptions/base.py` → `templates/shared/standalone/shared_exceptions.py`
`NotFoundError(resource, identifier)` e `ConflictError`.

### `shared/schemas/base.py` → `templates/shared/standalone/shared_schemas.py`
`ErrorResponse`, `MessageResponse`, `PaginatedResponse[T]`.

### `.env.example` → `templates/shared/standalone/env_example`
Template com `DATABASE_URL`. Substitua `{module_name}` no nome do banco.

### `.gitignore` → `templates/shared/standalone/gitignore`
Exclui `__pycache__/`, `.env`, `.pytest_cache/`, `dist/`, `*.db`, IDEs.

### `frontend/shared/core.css` → `templates/shared/frontend/shared/core.css`
Variáveis CSS (`--primary`, `--bg-card`, `--border-color`, etc.) para standalone sem o monorepo. **Apenas fallback standalone** — no GrindX o módulo usa a `shared` padrão em `/shared/core.css` e a `shared/` do módulo **não é copiada** no export.

### `frontend/shared/app.js` → `templates/shared/frontend/shared/app.js`
Stub vazio — no GrindX fornece `window.grindx.session`, no standalone é vazio. **Apenas fallback standalone**, não é copiada no export.

**Fluxo de import no router (dual-context):**
- GrindX: `app.database.get_db` + `app.auth.dependencies.get_current_user`
- Standalone: `app.core.database_protheus.get_db_protheus` + `app.core.auth.verify_api_key`
- `shared.*` e `app.modules.iam.*` resolvidos localmente no standalone

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
- `templates/shared/frontend/style.css` — estilos do módulo
- `templates/shared/frontend/version.js` — global `window.{module_upper}_VERSION` (badge de versão; substitua `{module_upper}`)

**Estrutura padrão do header da página (obrigatória em todo módulo):**
```html
<header class="page-header mb-8">
    <div>
        <div class="page-header-container">
            <h1>{menu_label}</h1>
            <span class="viz-version" id="viz-version" aria-label="Versao do modulo"></span>
        </div>
        <p class="text-muted">{menu_description}</p>
    </div>
    <div class="actions-group" style="margin-top: var(--space-4);">
        <button class="btn btn-primary" id="btn-novo">+ Novo {entity_name}</button>
    </div>
</header>
```
- `h1` e o badge `viz-version` ficam lado a lado dentro de `.page-header-container`
- A descrição (`{menu_description}`) fica abaixo do container, dentro do mesmo `<div>`
- A área de botões usa `class="actions-group"` com `style="margin-top: var(--space-4);"` — nunca `header-actions` (não existe no monorepo)
- `.page-header-container` é definido no `core.css` e usa `justify-content: space-between` (h1 à esquerda, badge à direita), `width: 100%` e `gap: var(--space-3, 0.75rem)` — responsivo, sem `gap` fixo; não duplicar no style.css do módulo
- `.viz-version` também é definido no `core.css` com `white-space: nowrap` — o número da versão nunca quebra internamente e o badge permanece visível quando a página é reduzida
- Como `.page-header` usa `flex-direction: column; align-items: flex-start`, o primeiro `<div>` filho precisa de `width: 100%` (regra `.page-header > div { width: 100%; }` no `style.css`) para o `.page-header-container` ocupar a largura total e o badge ir ao **extremo direito**

**Regras HTML:**
- HTML5 semântico, zero dependências externas (sem CDN, sem bibliotecas)
- `<meta name="viewport" content="width=device-width, initial-scale=1.0">` obrigatório
- Incluir no `<head>` (caminho **absoluto** `/shared/...` = `shared` padrão do GrindX; `version.js` fica na **raiz** do frontend):
  ```html
  <link rel="stylesheet" href="/shared/core.css">
  <link rel="stylesheet" href="style.css">
  <script src="/shared/config.js"></script>
  <script src="/shared/app.js"></script>
  <script src="version.js"></script>
  <script src="script.js" defer></script>
  ```
- Ordem: `config.js` → `app.js` → `version.js` → `script.js` (o `config.js` define `window.GRINDX_CONFIG.API_BASE_URL`; `version.js` define `window.{module_upper}_VERSION`)
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
- `API_BASE`: relativa no GrindX (`/{route_api}`), absoluta no standalone (`http://localhost:7000/{route_api}`)
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
- **`requirements.txt`** → `templates/shared/support/requirements.txt` — pytest, sqlalchemy, pydantic, structlog, fastapi, uvicorn, alembic, python-dotenv
- **`pytest.ini`** → `templates/shared/support/pytest.ini` — config testpaths
- **`Makefile`** → `templates/shared/support/Makefile` — targets: test, test-unit, test-integration, dev-backend, dev-frontend, package, export, dry-run, import, clean, version, version-dry-run, help

## 5.5 Versionamento (obrigatório)

> Gerado por `templates/shared/scripts/version.py` — mesmo padrão do `pop_viz`.

> **Version badge: padrão vs standalone** — módulos **padrão** do monorepo (criados direto em `apps/frontend-webapp/modules/`) **não** geram versão própria: exibem a versão do sistema via `window.grindx.version.get()` (vinda de `version.json`), igual à tela de login. Apenas módulos **standalone/importados** geram a própria versão (`window.{module_upper}_VERSION` via `scripts/version.py`). Esta seção 5.5 aplica-se apenas a módulos standalone.

- **`scripts/version.py`** → `templates/shared/scripts/version.py` — gera a próxima versão semver a partir de conventional commits (`BREAKING`/`feat!:` → MAJOR, `feat:` → MINOR, demais → PATCH). Atualiza `module.json` + `CHANGELOG.md` + **todas** as `frontend/*/version.js` (glob por aba, `version.js` na **raiz** de cada frontend). Flags: `--dry-run`, `--no-tag`; exit 2 em erro de git. Ignora commits de release (`docs: registrar changelog`).
- **`scripts/version.py`** usa o placeholder `{module_upper}` para o global JS (`window.{module_upper}_VERSION`).
- **`CHANGELOG.md`** — criado na primeira execução; formatação por tipo de commit.
- **Frontend badge**: cada `frontend/*/index.html` carrega `version.js` (antes de `script.js`), inclui `<span id="viz-version">` no header e `script.js` chama `setBadgeVersao()` (`templates/shared/frontend/*` já contém esses trechos). `style.css` esconde o badge em `@media print`.

**Fluxo de release em duas etapas** (a tag deve ficar no commit que contém o CHANGELOG):
1. `python scripts/version.py --no-tag` — atualiza `module.json` + `version.js` + `CHANGELOG.md`
2. Commitar esses artefatos e então criar a tag `git tag vX.Y.Z`
⚠️ O padrão `make version` cria a tag no commit atual, ANTES do commit dos artefatos — `git checkout vX.Y.Z` não conteria o changelog.

Arquivos standalone (ver seção 1.0):
- **`.env.example`** → `templates/shared/standalone/env_example` — template DATABASE_URL
- **`.gitignore`** → `templates/shared/standalone/gitignore` — exclui __pycache__, .env, .pytest_cache, dist

Documentacao:
- **`AGENTS.md`** → `templates/shared/AGENTS.md` — regras padrao para agentes de IA (preencher com detalhes do modulo)

Substitua `{module_name}`, `{entity_name}`, `{frontend_prefix}`.

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

**Nomenclatura do zip** — o `package()` nomeia o zip com a versão lida do `module.json`: `dist/modulo-{pasta_do_modulo}-v{version}.zip` (ex: `modulo-pop_docs-v1.0.0.zip`); sem versão no manifest → `modulo-{pasta_do_modulo}.zip`. Mesmo padrão do `pop_docs` (`_zip_filename`). A importação no GrindX usa o `module_name` do manifest (o fallback fuzzy `*{module_name}*.zip` aceita o nome com versão).

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

# 3. Rodar standalone (sem GrindX)
make dev-backend      # FastAPI em http://localhost:7000
make dev-frontend     # Frontend estatico em http://localhost:7080

# 4. Gerar pacote .zip
make package

# 5. Importar no GrindX
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
- [ ] **Standalone prerequisites**: `app/__init__.py`, `app/main.py`, `app/core/` (config, database_protheus, auth), `app/modules/iam/base.py`, `shared/` (exceptions, schemas), `.env.example`, `.gitignore`
- [ ] Backend: base, model, schemas, repository, service, router + __init__.py
- [ ] **Router dual-context**: try/except para `get_db`/`get_current_user` (GrindX) vs `get_db_protheus`/`verify_api_key` (standalone)
- [ ] **Frontend dual-context**: `_fetch()` e `downloadFromUrl()` com detecção `window.grindx.session` + `index.html` inclui `app.js`
- [ ] **PDF opcional**: se módulo gera PDF, instalar `xhtml2pdf` no venv do GrindX
- [ ] Tests: conftest.py, unit tests (mocked repo), integration tests (SQLite)
- [ ] Migration: Alembic migration file (PostgreSQL)
- [ ] Support: requirements.txt (com python-dotenv), pytest.ini, run_tests.ps1, Makefile (com dev-backend/dev-frontend)
- [ ] Versionamento: `scripts/version.py` + targets `version`/`version-dry-run` no Makefile
- [ ] Badge de versão: `version.js` na raiz de cada aba frontend, `<span id="viz-version">` no header, `setBadgeVersao()` em `script.js` (`.viz-version` e `.page-header-container` vêm do `core.css` — não duplicar no `style.css`)
- [ ] `AGENTS.md` criado na raiz do modulo com regras para agentes de IA
- [ ] `AGENTS.md` documenta o fluxo de release em duas etapas (`--no-tag` → commit → `git tag vX.Y.Z`)
- [ ] Testes passam: `pytest app/modules/{module_name}/tests/ -v`
- [ ] Dev server funciona: `make dev-backend` sobe em http://localhost:7000
- [ ] `module.json` criado na raiz do standalone com `frontend_tabs` array
- [ ] `export.py`: usa `STANDALONE_ROOT` para paths de frontend, migration e dist
- [ ] `export.py`: `--dry-run` simula sem alterar GrindX
- [ ] `export.py`: **exclui a pasta `shared/` do módulo** da cópia e do zip (no GrindX usa-se a `shared` padrão em `/shared`)

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
