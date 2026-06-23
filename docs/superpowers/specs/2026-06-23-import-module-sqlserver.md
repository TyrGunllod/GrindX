# Importação de Módulos para api-sqlserver

## Data: 2026-06-23

## Problema

O sistema de importação atual (`import_module.py`) só suporta módulos para o **api-postgres**. Módulos read-only que consultam tabelas do Protheus via SQL Server (ex: custo, produtos, pedidos) precisam ser criados manualmente no **api-sqlserver** — sem script, sem UI, sem padronização.

## Solução

Estender o `import_module.py` e o `module.json` para suportar `target_api: "sqlserver"`, permitindo que um mesmo pipeline de importação (zip → scan → import) funcione para ambas as APIs.

## 1. Extensão do Manifesto (`module.json`)

Novo campo `target_api` (opcional, default `"postgres"`):

```json
{
  "module_name": "custo",
  "entity_name": "CustoProduto",
  "version": "1.0.0",
  "target_api": "sqlserver",
  "schema_name": "org",
  "route_prefix": "/v1/produtos/custos",
  "route_tag": "Custo Produto",
  "frontend_tabs": [
    {"name": "Custos", "url": "modules/custos/index.html"}
  ],
  "menu_label": "Custos",
  "menu_icone": "chart-bar",
  "role_minima": "operador",
  "dependencies": []
}
```

### Valores de `target_api`

| Valor | API alvo | Read-only | Migration | Models |
|-------|----------|-----------|-----------|--------|
| `"postgres"` (default) | api-postgres (8002) | Não | Sim | Sim |
| `"sqlserver"` | api-sqlserver (8001) | Sim | Não | Não |

## 2. Estrutura do `.zip` para sqlserver

```
modulo-{nome}.zip
├── module.json
├── app/modules/{module_name}/
│   ├── __init__.py
│   ├── exceptions.py            ← obrigatório (exceções específicas)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── {entity_name}.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── {entity_name}_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── {entity_name}_service.py
│   │   └── {entity_name}_pdf_service.py  ← opcional
│   └── routers/
│       ├── __init__.py
│       └── {entity_name}_router.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
└── migration/                    ← ignorado se target_api = sqlserver
    └── {revision}_{table_name}.py
```

### Diferenças da estrutura postgres

| Item | postgres | sqlserver |
|------|----------|-----------|
| `models/` | Obrigatório | **Não existe** (SQL raw via `text()`) |
| `migration/` | Obrigatório | **Ignorado** (sem schema p/ gerenciar) |
| `exceptions.py` | Opcional (usa shared) | **Obrigatório** (exceções específicas do domínio) |
| `base.py` | Obrigatório (SQLAlchemy Base) | **Não existe** |
| `dependencies` | Registra em `dependencies.py` | **Inline** via `_auth_dependency` |

## 3. Alterações no `scripts/import_module.py`

### 3.1. CLI — novo argumento `--target-api`

```bash
python scripts/import_module.py {module_name} --import-dir={tmp} --target-api=sqlserver
```

Se não informado, lê do `module.json` (`target_api`). Se nenhum dos dois, assume `"postgres"`.

### 3.2. Fluxo de importação condicional

```
import_module(module_name, import_dir, force, dry_run, skip_migrations, target_api)
                                              ┌─ "postgres" → fluxo atual
                                              └─ "sqlserver" → fluxo novo
```

### 3.3. Fluxo sqlserver (passo a passo)

1. **Valida manifesto** (module.json, incluindo `target_api`)
2. **Backup** dos arquivos que serão modificados (`api-sqlserver/app/main.py`)
3. **Copia backend** → `api-sqlserver/app/modules/{module_name}/`
4. **Copia frontend** → `frontend-webapp/modules/{module_name}/`
5. **Ignora migration** (pasta `migration/` nem é verificada)
6. **Edita `api-sqlserver/app/main.py`**: adiciona import + `app.include_router()`
   - Localiza o último `from app.modules.` import existente
   - Insere novo import após ele
   - Localiza o último `app.include_router(` existente
   - Insere novo include após ele
   - Mesma lógica do `register_router()` atual, porém no arquivo do sqlserver
7. **Ignora `dependencies.py`** (api-sqlserver usa `_auth_dependency` inline — sem fábricas)
8. **Ignora `alembic/env.py`** (sqlserver não tem models nem Alembic)
9. **Ignora migração** (sem `alembic upgrade`)
10. **Registra em `portal_modulos`** (igual ao fluxo postgres — a tabela fica no postgres)

### 3.4. Funções novas

```python
def _get_sqlserver_api_dir() -> Path:
    """Retorna o diretório raiz do api-sqlserver."""
    env = os.environ.get("GRINDX_SQLSERVER_API_DIR")
    if env:
        return Path(env).resolve()
    return _get_monorepo_root() / "apps" / "api-sqlserver"


def register_router_sqlserver(manifest: dict, force: bool) -> None:
    """Edita api-sqlserver/app/main.py — adiciona import + include_router.

    Diferenças do register_router() do postgres:
    - Alvo é api-sqlserver/app/main.py
    - Não verifica diretório de routers (já deve existir)
    - Mais simples: só adiciona import + include
    """
```

### 3.5. Funções modificadas

```python
def copy_backend(import_dir, module_name, force, target_api="postgres"):
    """Copia backend para a API correta baseada em target_api."""

def import_module(module_name, import_dir, force=False, dry_run=False,
                  skip_migrations=False, target_api="postgres"):
    """Fluxo condicional baseado em target_api."""
```

### 3.6. Mapa de steps por target_api

| Step | postgres | sqlserver |
|------|----------|-----------|
| validate_manifest | Sim | Sim |
| backup_existing | Sim | Sim (só main.py) |
| copy_backend | `api-postgres/app/modules/` | `api-sqlserver/app/modules/` |
| copy_frontend | Sim | Sim |
| copy_migration | Sim | **Pulado** |
| register_router | `api-postgres/app/main.py` | `api-sqlserver/app/main.py` |
| register_dependency | Sim (dependencies.py) | **Pulado** |
| register_alembic_import | Sim (env.py) | **Pulado** |
| run_migrations | Sim (alembic) | **Pulado** |
| register_menu | Sim | Sim |

## 4. Alterações no `import_router.py`

### 4.1. Scan (`GET /v1/import/scan`)

- Já lê `module.json` → agora inclui `target_api` na resposta
- Frontend pode mostrar um badge "SQL Server" / "PostgreSQL"

### 4.2. Import (`POST /v1/import/{module_name}`)

- Lê `target_api` do `module.json`
- Passa `--target-api` para o subprocesso `import_module.py`

## 5. Backend — api-sqlserver `main.py` editável

O `main.py` do api-sqlserver precisa de marcadores para edição previsível:

```python
# --- imports-modules ---
from app.modules.custo.routers.custo_produto_router import router as custo_router
# --- end-imports-modules ---

# --- include-modules ---
app.include_router(custo_router)
# --- end-include-modules ---
```

Sem marcadores, o `register_router_sqlserver()` usa a mesma heurística do postgres:
- Localiza último `from app.modules.` → insere depois
- Localiza último `app.include_router(` → insere depois

## 6. Segurança

- **Read-only**: módulos sqlserver só expõem GET (validado pelo CORS da API e pela própria natureza do SQL Server)
- **Inline auth**: cada router define `_auth_dependency` localmente, sem depender de `dependencies.py`
- **Sem models**: não há tabelas gerenciadas pelo Alembic — consultas raw SQL contra o banco Protheus

## 7. Testes

- Teste do `import_module.py` com `--target-api=sqlserver` e diretório mockado (sem models, sem migration)
- Teste de `register_router_sqlserver()` com `main.py` mockado
- Teste de rollback para sqlserver (restaurar `main.py` original)
- Teste de detecção: módulo sem `target_api` assume `"postgres"` (compatibilidade reversa)

## 8. Observações

- O módulo **custo** existente no api-sqlserver servirá como referência de implementação para novos módulos sqlserver. Seu código fonte (removido do repositório) deve ser preservado como template em `.opencode/skills/create-standalone-module/templates/sqlserver/`.
- O `create-standalone-module` skill deve ser atualizado para gerar módulos sqlserver quando `--target-api=sqlserver` for passado.
- `dependencies` no `module.json` para sqlserver é sempre vazio (não há fábricas de dependência).
