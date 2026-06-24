## Monorepo Structure

- `apps/api-postgres/` — FastAPI principal (porta 8002), JWT + RBAC, PostgreSQL via Alembic
- `apps/api-sqlserver/` — FastAPI somente leitura (porta 8001), valida tokens do api-postgres
- `apps/frontend-webapp/` — Portal vanilla JS (porta 8101), módulos via iframe, zero frameworks
- `packages/shared/` — Pacote Python compartilhado (security, schemas, exceptions, error codes)
- `tests/` — Testes de integração do monorepo (raiz)
- `.opencode/skills/create-standalone-module/` — Skill para criar novos módulos

## Developer Commands

```powershell
make venv              # cria .venv e instala requirements das duas APIs
make dev-postgres      # uvicorn porta 8002 (Win: scripts/dev-postgres.ps1)
make dev-sqlserver     # uvicorn porta 8001 (Win: scripts/dev-sqlserver.ps1)
make dev-frontend      # http.server porta 8101 (Win: scripts/dev-frontend.ps1)
make dev-all           # todos (terminais separados via pwsh no Windows)
make dev-kill-port     # Win: remove portproxy rules nas portas dev (req admin)
make migrate           # alembic upgrade head
make seed              # popula dados iniciais
make test-all          # pytest de todas as APIs + shared + raiz
make lint              # ruff check --fix . && ruff check .
make format            # ruff format packages/ apps/
make build             # podman-compose build
make up / down / logs  # podman-compose
make images            # podman build + exporta .tar para Containers/images/
make volumes           # cria Containers/volumes/ para runtime
make clean             # remove __pycache__ e .pytest_cache
make deploy DEST=...   # copia configs para diretório externo
```

**Windows portproxy:** `svchost.exe (iphlpsvc)` pode ocupar portas via `netsh interface portproxy`. Os scripts `.ps1` tentam remover o conflito automaticamente. Se falhar, execute `make dev-kill-port` como Administrador uma vez.

## PYTHONPATH — Crítico

`shared` não é instalado via pip. Todos os comandos precisam de PYTHONPATH apontando para `packages/`:
- **Makefile** já configura automaticamente (`PP_APP`, `PP_ROOT`, `PP_SHARED`)
- **CI** usa `PYTHONPATH=${{ github.workspace }}/packages`
- **Manual (Windows):** `set PYTHONPATH=..\..\packages && python -m pytest tests/ -v`

## Pre-commit

```powershell
ruff format packages/ apps/
ruff check --fix .
ruff check .                   # sem erros
```

**Antes de todo `git push`, obrigatório:**

```powershell
ruff format packages/ apps/ && ruff check --fix . && ruff check .
```

Config ruff em `apps/api-postgres/ruff.toml`: select E, F, I — ignore E501 — alembic/versions ignora I001.

## Testing

- pytest com markers `unit`, `integration`, `slow` (definidos em `pytest.ini` raiz)
- Testes de integração usam SQLite in-memory com `schema_translate_map` para simular schemas PostgreSQL
- **api-sqlserver** usa `DB_URL_OVERRIDE=sqlite:///:memory:` nos testes (CI usa SQLite)
- Cobertura mínima: 70% (enforced no CI via `--cov-fail-under=70`)
- Testes raiz (`make test-root`) precisam de PYTHONPATH com todos os pacotes

## Commit & Release

- Formato: [conventional commits](https://www.conventionalcommits.org/) (parser angular)
- Título em inglês, descrição em português
- `feat` → minor, `fix`/`perf` → patch
- CI em `.github/workflows/release.yml`: push para `main` → lint + testes + semantic-release
- `python-semantic-release` v10 gerenciado via `version_variables` em `pyproject.toml`
- **Fonte canônica**: `apps/api-postgres/app/core/config.py:APP_VERSION`
- `version_variables` sincroniza 3 arquivos: ambos `config.py` + `apps/frontend-webapp/version.json`
- CI usa SQLite (sem PostgreSQL real) — env vars como `DATABASE_URL: "sqlite:///:memory:"`

## Architecture — Non-obvious

- **api-sqlserver** é read-only (`allow_methods=["GET"]` no CORS); só tem `health_router` e `cliente_router`
- **Schemas PostgreSQL**: `iam`, `portal`, `org` — definidos em testes/seed. Módulos implementados: `iam`, `org`, `portal` (em `app/modules/`)
- **Frontend**: `shared/core.css` (tokens CSS), `shared/app.js` (UIFactory), `shared/skinLoader.js` (temas); módulos standalone em `modules/` com `index.html`, `script.js`, `style.css`
- **Design system**: Glassmorphism, `var(--...)` para tudo, nunca cores/fontes fixas
- **compose.yaml**: ambas as APIs usam `network_mode: "container:grindx-frontend"` (compartilham rede do nginx)
- **Containerização**: Podman (não Docker), `podman-compose.yml` — no Windows requer `podman machine` com conexão rootful
- **Volumes no WSL**: `compose.yaml` usa `${PWD}` para paths de volume (não `./` relativo). Projeto deve estar clonado dentro do filesystem WSL (`~/...`), não em `/mnt/c/...`
- **Ordem de scripts nos módulos**: `config.js` → `app.js` → `apiService.js` → `baseController.js` → `script.js`. `config.js` deve ser incluído em TODO `index.html` de módulo
- **CSP no nginx**: `style-src` inclui `https://fonts.googleapis.com` (Google Fonts); `connect-src` inclui `http://localhost:8002 http://127.0.0.1:8002`

## Error Codes

Registro centralizado em `packages/shared/exceptions/codes.py`. Use `ErrorCode.CONSTANT` em vez de strings:
```python
from shared.exceptions.codes import ErrorCode
raise CredenciaisInvalidasError()
```

## Security Gotchas

- **SECRET_KEY**: validada com entropia Shannon (mín. 3.5 bits/caractere) via Pydantic
- **CORS**: modo strict em produção (nunca `*`); `CORS_ORIGINS` lida como string JSON
- **DEV_NETWORK_IP**: adiciona IP local ao CORS dev e CSP `connect-src`
- **Rate limiting**: SlowAPI com chaves duplas (IP anônimo / user_id autenticado)

## Performance Gotchas

- **Cache**: cachetools TTLCache (15 min TTL) para temas, usuários e portal
- **Índices**: 5 B-tree via migração Alembic (company_themes composite, usuarios role/ativo/empresa_id, portal_modulos aba_id)

## New Modules

Usar `.opencode/skills/create-standalone-module/SKILL.md` — cobre backend + frontend + testes + migration + export.

### Import para api-sqlserver

Módulos read-only (consultas a tabelas do Protheus) usam `target_api: "sqlserver"` no `module.json`:

- Backend copiado para `apps/api-sqlserver/app/modules/{nome}/` (sem models, sem base.py)
- Router registrado no `main.py` do api-sqlserver
- Migration, dependency factory e alembic import são **pulados**
- O campo `target_api` pode ser sobrescrito via CLI: `--target-api=sqlserver`
- `--target-api` pode ser passado via CLI: `--target-api=sqlserver`
- `frontend/shared/` é ignorado durante a cópia (já existe no monorepo)
- `python scripts/import_module.py {nome} --import-dir={tmp} --target-api=sqlserver`

## Docs Sync

Sempre atualizar `README.md`, `docs/API.md`, `docs/DATABASE.md`, `docs/SETUP.md`, `docs/README.md` e este `AGENTS.md` ao alterar código relevante.
