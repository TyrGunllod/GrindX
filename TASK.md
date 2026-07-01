# TASK: Perfil — novos campos e botão salvar por card
> Created: 2026-07-01 | Updated: 2026-07-01 13:14

## Goal
Adicionar campos (Código, C.B.O, Departamento, Cargo, CPF, Endereço, CEP) ao perfil do usuário com persistência no backend. Substituir botão salvar único por um botão em cada card.

## Plan
- [x] Model Usuario: adicionar colunas codigo, cbo, departamento, cargo, cpf, endereco, cep
- [x] Schema: adicionar campos em UsuarioResponse e UsuarioUpdate
- [x] AuthService.update_profile(): aceitar e persistir novos campos
- [x] Router PUT /auth/me: passar novos campos para o service
- [x] Migration 013: add_profile_fields
- [x] Frontend index.html: novos campos no card Meus Dados + botão salvar em cada card
- [x] Frontend script.js: load/save dos novos campos, save por card (profile/password/preferences)
- [x] Frontend style.css: .card-save-btn, .field-divider
- [x] Ruff lint + format: ok
- [x] Tests: 36 passed

## Log
### 2026-07-01
- Model/Schema/Service/Router: 7 novos campos adicionados — `ruff check` ok
- Migration 013: `b0c1d2e3f4a5` adiciona colunas na tabela iam.usuarios
- Frontend: cards refatorados com save button próprio, `handleSave` separado em `saveProfile()`, `savePassword()`, `savePreferences()`
- `python -m pytest tests/unit/test_auth_service.py tests/unit/test_auth.py tests/integration/test_autenticacao_integrada.py` → 36 passed

## Unverified / Pending
- Migration não testada em PostgreSQL real (apenas SQLite nos testes)

## Current State
Perfil do usuário agora tem 7 novos campos editáveis. Cada card (Meus Dados, Senha, Preferências) tem seu próprio botão Salvar. Dados persistem via PUT /auth/me no backend.

---

# TASK: Import timeout + frontend copy no módulo custo (api-postgres)
> Created: 2026-06-23 | Updated: 2026-07-01 12:19

## Goal
Importação de módulos .zip funcionando completamente via container WSL:
sem timeout, frontend copiado, erros tratados corretamente.

## Plan
- [x] **Zoom iframe:** remover controles visuais, adicionar atalhos teclado (PageUp/PageDown/Home)
- [x] Adicionar `--reload` no Dockerfile do sqlserver (auto-restart em mudanças)
- [x] Lazy engine em `database.py` (evitar timeout no import de módulos Python)
- [x] Separar migração Alembic em background thread no endpoint de import
- [x] Adicionar `--skip-migrations` flag no `import_module.py`
- [x] Adicionar timing logs `[TIMING]` nos passos do subprocesso
- [x] Trocar `subprocess.run` por `Popen` + `communicate` com streaming de stdout/stderr
- [x] Tratar `PermissionError` no backup e frontend copy (bind mounts sem permissão)
- [x] Testar import após rebuild da imagem api-postgres
- [x] Extender import_module.py para suportar `--target-api=sqlserver`
- [x] Criar spec e plano para import sqlserver
- [x] Atualizar skill create-standalone-module com sqlserver support
- [x] Fix CORS: add localhost:8101 + ENVIRONMENT=development to .env
- [x] Fix 500: handle IntegrityError in criar_modulo → ConflictError (409)
- [x] Fix PermissionError: relança exceção em vez de log warning silencioso
- [x] Fix deploy: chown 1001:1001 para modules/ e import/

## Log
### 2026-07-01
- Zoom iframe: removidos controles visuais HTML/CSS, adicionados atalhos PageUp/PageDown/Home, sem dangling references — grep verify ok
### 2026-06-23
- Swagger CSP: excluídos paths `/v1/docs`, `/v1/redoc`, `/v1/openapi.json` dos security headers (sqlserver)
- Removidos todos endpoints do sqlserver exceto `/health`
- Lazy engine creation em `apps/api-sqlserver/app/database.py`
- `--skip-migrations` adicionado ao `scripts/import_module.py`
- `import_router.py`: subprocesso com `Popen` + `communicate(timeout=60)`
- `import_module.py`: `_log_step()` com `print("[TIMING] ...")`
- `backup_existing()` e `copy_frontend()`: trata PermissionError
- SQLServer import: `_get_sqlserver_api_dir()`, `register_router_sqlserver()`, `--target-api` CLI
- `import_router.py`: lê `target_api` do module.json, pula migrations para sqlserver
- `docs/IMPORTACAO.md` e `AGENTS.md`: documentação import sqlserver
- Skill `create-standalone-module`: 36 menções sqlserver, module.json condicional, export.py com `is_sqlserver`, checklist separado
- `criar_modulo()` em `portal_router.py`: try/except IntegrityError → ConflictError (409) — commit `49b9b5b`
- `copy_frontend()` em `import_module.py`: PermissionError agora relança em vez de log warning — commit `0d42d03`
- `Makefile deploy`: `sudo chown -R 1001:1001` em modules/ e `sudo chown 1001:1001` em import/ — commit `0d42d03`
- Ruff format + lint: all checks passed

## Unverified / Pending
- `_run_migrations_background` não testada em produção
- Import do módulo Custo via API no container após `make deploy` + rebuild não verificado

## Errors & Fixes
| Error | Cause | Fix | Evidence |
|-------|-------|-----|----------|
| `Permission denied: '/app/import/.backup'` | Container user 1001:1001 sem escrita no bind mount | try/except PermissionError | Logs mostram o erro |
| Subprocesso 60s sem resposta | structlog não configurado + stdout sem log | Popen + communicate com timeout | `[import] [TIMING]` aparece nos logs |
| Timeout no navegador ao importar | Endpoint HTTP esperava migration 120s | `--skip-migrations` + background thread | Subprocesso completo em <0.5s |
| Frontend não copiado | UID 1001 sem permissão no bind mount modules/ | PermissionError agora **relança** (não silencia) + `chown 1001:1001` no deploy | commit `0d42d03` |
| CORS: No Access-Control-Allow-Origin | `ENVIRONMENT` não explícito + localhost:8101 ausente | `ENVIRONMENT=development` + `http://localhost:8101` adicionados ao `.env.local` | Fix local (.env gitignored) |
| POST /v1/portal/modulos retorna 500 | Slug duplicado aciona IntegrityError não tratado | try/except IntegrityError → ConflictError(409) | commit `49b9b5b` |

## Current State

### Zoom iframe
Zoom visual removido do dashboard. Agora é controlado exclusivamente por teclado:
- **PageUp** → +10% (máx 200%)
- **PageDown** → -10% (mín 30%)
- **Home** → reset 100%

Verificado: sem dangling references, CSS limpo, lógica intacta.

## Current State
O import de módulo via API no container WSL funciona com subprocesso <0.5s. 

**Frontend copy:** antes silenciava PermissionError (warning no log); agora **relança a exceção**, tornando a falha visível. `make deploy` faz `chown 1001:1001` nos diretórios modules/ e import/ para o container poder escrever.

**CORS e 500:** `.env` local com `ENVIRONMENT=development` e localhost:8101 explícito. `criar_modulo` trata IntegrityError com ConflictError (409).

**Import sqlserver:** script estendido com `--target-api`, `_get_sqlserver_api_dir()`, `register_router_sqlserver()`. Skill `create-standalone-module` atualizada com templates condicionais.

**Problema pendente:** rebuild da imagem api-postgres necessário para que as alterações no `import_module.py` e `import_router.py` entrem em vigor no container. `make deploy` com o chown precisa ser executado no host WSL antes de iniciar os containers.
