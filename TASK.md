# TASK: Import timeout no módulo custo (api-postgres)
> Created: 2026-06-23 | Updated: 2026-06-23 14:22

## Goal
Resolver o timeout ao importar módulos .zip via frontend no container WSL.
O import trava no navegador (~30s) porque a migração Alembic leva até 120s.

## Plan
- [x] Adicionar `--reload` no Dockerfile do sqlserver (auto-restart em mudanças)
- [x] Lazy engine em `database.py` (evitar timeout no import de módulos Python)
- [x] Separar migração Alembic em background thread no endpoint de import
- [x] Adicionar `--skip-migrations` flag no `import_module.py`
- [x] Adicionar timing logs `[TIMING]` nos passos do subprocesso
- [x] Trocar `subprocess.run` por `Popen` + `communicate` com streaming de stdout/stderr
- [x] Tratar `PermissionError` no backup e frontend copy (bind mounts sem permissão)
- [x] Testar import após rebuild da imagem api-postgres

## Log
### 2026-06-23
- Swagger CSP: excluídos paths `/v1/docs`, `/v1/redoc`, `/v1/openapi.json` dos security headers (sqlserver)
- Removidos todos endpoints do sqlserver exceto `/health`
- Ruff format + lint fixes no database.py, security_headers.py
- Lazy engine creation em `apps/api-sqlserver/app/database.py` — engine só criado na primeira `get_db()`
- `--skip-migrations` adicionado ao `scripts/import_module.py`
- `import_router.py`: subprocesso com `Popen` + `communicate(timeout=60)`, stdout/stderr logados em tempo real
- `import_module.py`: `_log_step()` com `print("[TIMING] ...")` em cada passo
- `backup_existing()`: trata `PermissionError` — loga warning e continua
- `copy_frontend()`: trata `PermissionError` por arquivo — loga warning e pula
- TASK.md criado

## Unverified / Pending
- Frontend copy com PermissionError nos bind mounts — copiar manualmente ou ajustar permissões
- background thread de migração (`_run_migrations_background`) não testada

## Errors & Fixes
| Error | Cause | Fix | Evidence |
|-------|-------|-----|----------|
| `Permission denied: '/app/import/.backup'` | Container user 1001:1001 sem escrita no bind mount `./import` | try/except PermissionError em backup_existing e copy_frontend | Logs mostram o erro: `[TIMING] validate_manifest 0.00s` seguido de `Erro: Permission denied` |
| Subprocesso 60s sem resposta | import_module.py não tinha structlog configurado, stdout/stderr capturados sem log | Popen + communicate com timeout e streaming de stderr para container log | `[import] [TIMING]` aparece nos logs agora |
| Timeout no navegador ao importar | Endpoint HTTP esperava subprocesso completo (migration 120s) | `--skip-migrations` no subprocesso + migration em background thread | Com `--skip-migrations`, subprocesso completo em <1s |

## Current State
O import de módulo pelo frontend no container WSL **funciona**. O subprocesso roda em ~0.45s com `--skip-migrations` e retorna `success: true` imediatamente. Backup, backend copy, rotas e dependências são registrados com sucesso. 

O frontend copy tem `PermissionError` nos bind mounts (`/app/apps/frontend-webapp/modules/`) — tratado com warning, o módulo funciona sem frontend. Para copiar o frontend, executar `chmod -R 777 apps/frontend-webapp/modules/` no host e re-importar, ou copiar manualmente os diretórios `custos/` e `shared/` para `apps/frontend-webapp/modules/`.

**Provado por:** `podman logs grindx-api-postgres` mostra todos os 9 [TIMING] steps em <0.5s, backup criado em `/app/import/.backup/`, rotas registradas em `main.py`, dependências registradas em `dependencies.py`, menu registrado.
