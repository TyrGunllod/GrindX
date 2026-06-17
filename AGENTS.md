## Monorepo Structure

- `apps/api-postgres/` — FastAPI principal (porta 8002), JWT + RBAC, PostgreSQL via Alembic
- `apps/api-sqlserver/` — FastAPI somente leitura (porta 8001), valida tokens do api-postgres
- `apps/frontend-webapp/` — Portal vanilla JS (porta 8101), módulos via iframe, zero frameworks
- `packages/shared/` — Pacote Python compartilhado (security, schemas, exceptions, error codes)
- `tests/` — Testes de integração do monorepo (raiz)
- `.opencode/skills/` — Skills customizadas (ex: `create-standalone-module`)

## Developer Commands

```powershell
# APIs (cada uma tem seu .venv próprio em apps/<api>/.venv)
make dev-postgres      # uvicorn porta 8002
make dev-sqlserver     # uvicorn porta 8001
make dev-frontend      # http.server porta 8101
make dev-all           # todos (abre terminais separados via pwsh)

# Banco
make migrate           # alembic upgrade head
make seed              # popula dados iniciais

# Testes
make test-postgres     # pytest apps/api-postgres/tests/
make test-sqlserver    # pytest apps/api-sqlserver/tests/
make test-shared       # pytest packages/shared/tests/
make test-root         # pytest tests/ (raiz)
make test-all          # todos acima

# Containers
make build             # podman-compose build
make up                # podman-compose up -d
make down              # podman-compose down
```

## PYTHONPATH — Crítico

O módulo `shared` não está instalado via pip. Todos os comandos de dev e teste precisam de PYTHONPATH apontando para `packages/`:

```powershell
# Exemplo manual (Windows)
set PYTHONPATH=..\..\packages && python -m pytest tests/ -v

# No Makefile já está configurado automaticamente
# No CI: PYTHONPATH=${{ github.workspace }}/packages
```

## Pre-commit Checklist

```powershell
ruff format packages/ apps/    # formata
ruff check --fix .             # corrige lint
ruff check .                   # verifica (sem erros)
```

Config Ruff (`apps/api-postgres/ruff.toml`): select E, F, I — ignore E501 — alembic/versions ignora I001.

## Commit Convention

- Formato: [conventional commits](https://www.conventionalcommits.org/)
- Título: inglês (apenas o prefixo `tipo(escopo):`)
- Descrição: português (BR)
- Exemplo:
  ```
  feat(auth): adicionar validacao de login

  Adiciona validação de campos obrigatórios no formulário de login.
  ```

## Push Policy

- **Commit:** sempre após concluir uma alteração (automático)
- **Push:** somente quando o usuário solicitar explicitamente (ex: "push", "subir", "enviar")

## Semantic Release

- Config em `pyproject.toml` (python-semantic-release, parser angular)
- Versão definida em `apps/api-postgres/app/core/config.py` e `apps/api-sqlserver/app/core/config.py` (variável `APP_VERSION`)
- Build command roda `scripts/update_frontend_version.py` que sincroniza `apps/frontend-webapp/version.json`
- CI: único workflow `release.yml` (push para `main`) — testa lint + todos os testes + semantic release
- CI usa SQLite in-memory (sem PostgreSQL real)

## Arquitetura — Detalhes Não Óbvios

- **api-postgres** schemas de banco: `iam`, `portal`, `catalogo`, `org` — módulos em `app/modules/`
- **api-sqlserver** é read-only; nunca emite JWT, apenas valida tokens do api-postgres
- **Frontend** usa `shared/core.css` (tokens CSS), `shared/app.js` (`UIFactory`), `skinLoader.js` para temas
- **Módulos frontend** são standalone: cada um tem `index.html`, `script.js`, `style.css` próprio
- **Design system**: Glassmorphism, `var(--...)` para tudo, nunca cores/fontes fixas no CSS dos módulos
- **Containerização**: Podman (não Docker), `podman-compose.yml`

## Segurança (implementada)

- **SECRET_KEY**: Validação de entropia Shannon (mínimo 3.5 bits/caractere) via Pydantic field_validator
- **Senhas temporárias**: 16 caracteres alfanuméricos via `secrets` module, expiração de 15 minutos
- **Rate limiting**: SlowAPI com chaves duplas (IP para não-autenticados, user_id para autenticados)
- **File upload**: Validação de magic bytes via `filetype` library
- **CORS**: Modo strict em produção (nunca `*`), configuração via env var `CORS_ORIGINS`
- **DEV_NETWORK_IP**: IP da rede local para acesso externo em dev (ex: `192.168.0.62`). Adiciona automaticamente a origem no CORS dev fallback e as URLs no CSP `connect-src`. Definir no `.env` de cada API.
- **Health checks**: Verificação profunda de conectividade + schema validation

## Performance (implementada)

- **Cache**: cachetools TTLCache (15 min TTL) para temas, usuários e portal
- **Índices**: 5 índices B-tree via migração Alembic (company_themes composite, usuarios role/ativo/empresa_id, portal_modulos aba_id)
- **Health checks**: Verificação de conectividade + schema validation para PostgreSQL e SQL Server

## Infraestrutura (implementada)

- **pytest-cov**: Threshold mínimo de 70%, enforcement no CI
- **Migrações**: Cadeia linear com único head (consolidação de migrações órfãs)
- **Schema validation**: Testes que verificam `_SCHEMA_TRANSLATE` cobre todos os schemas

## API Versioning

- Todas as rotas usam prefixo `/v1/` padronizado
- Arquivo `apps/api-postgres/app/core/versioning.py` documenta a estratégia
- Para nova versão: criar rotas com `/v2/`, manter `/v1/` por 6 meses

## Error Codes

- Registro centralizado em `packages/shared/exceptions/codes.py`
- Use `ErrorCode.CONSTANT` em vez de hardcoding de strings
- Exemplo: `from shared.exceptions.codes import ErrorCode; raise CredenciaisInvalidasError()`

## Criando Novos Módulos

Usar a skill `.opencode/skills/create-standalone-module/SKILL.md` — cobre backend FastAPI + frontend vanilla JS + testes + migration + export.py. Seguir o checklist de registro ao final da skill.

## Testes

- pytest com markers: `unit`, `integration`, `slow` (definidos no `pytest.ini` raiz)
- Cada API tem seu próprio `tests/` com `conftest.py` e fixtures
- Testes de integração usam SQLite in-memory com `schema_translate_map` para simular schemas PostgreSQL
- `test-root` precisa de PYTHONPATH com todos os pacotes: `apps/api-postgres;apps/api-sqlserver;packages`
- Fixtures globais em `tests/conftest.py` adicionam `packages/` ao sys.path

## Documentação

- Manter `README.md`, `docs/API.md`, `docs/DATABASE.md`, `docs/SETUP.md` e `docs/README.md` **sempre atualizados** após qualquer alteração no código.
- Atualizar contagem de testes, novos endpoints, campos em schemas, migrations e mudanças de fluxo.
- O `AGENTS.md` também deve ser mantido atualizado (comandos, estrutura, políticas).

## Arquivos de Config Importantes

- `pyproject.toml` — semantic release config
- `pytest.ini` — config pytest (raiz) com `--cov=app --cov-fail-under=70`
- `apps/api-postgres/ruff.toml` — rules do ruff
- `podman-compose.yml` — orquestração de containers
- `Makefile` — automação de tasks (Windows/PowerShell)
- `apps/api-postgres/app/core/versioning.py` — estratégia de versionamento de API
- `packages/shared/exceptions/codes.py` — registro centralizado de error codes
- `apps/api-postgres/.env.dev` / `apps/api-sqlserver/.env.dev` — exemplos com `DEV_NETWORK_IP` para acesso em rede local
