# Importação de Módulos Frontend-Only

## Data: 2026-08-03

## Problema

O sistema de importação atual (`import_module.py`) trata todo módulo como backend-first: o `validate_manifest` exige `schema_name` e `route_prefix` incondicionalmente, e o `import_module()` executa `alembic upgrade head` mesmo quando o módulo não possui diretório `migration/`. Isso impede a importação de módulos **frontend-only** (somente HTML/CSS/JS, sem `app/`, sem `migration/`, sem rotas) — como o módulo `pop_viz` (Visualizador POP), que reutiliza os endpoints de leitura de `pop_docs`.

## Solução

Adicionar um campo `frontend_only: true` no `module.json` que marca o módulo como **sem backend**. Quando presente, o import:

1. **Não exige** `schema_name`/`route_prefix` na validação (campos "ignorados").
2. **Pula** a execução de migrações (`run_migrations`).
3. Os demais passos já são tolerantes a ausência de backend (logam *warning* e continuam): `copy_backend`, `merge_requirements`, `copy_migration`, `register_router`, `register_dependency`, `register_alembic_import`.

## 1. Extensão do Manifesto (`module.json`)

Novo campo `frontend_only` (opcional, default `false`):

```json
{
  "module_name": "pop_viz",
  "entity_name": "PopViz",
  "version": "1.0.0",
  "frontend_only": true,
  "schema_name": "portal",
  "route_prefix": "/v1/pop-docs",
  "frontend_tabs": [
    {"name": "Visualizador POP", "url": "modules/pop_viz/index.html"}
  ],
  "menu_label": "Visualizador POP",
  "menu_icone": "folder",
  "role_minima": "leitura",
  "dependencies": ["pop_docs"]
}
```

> O exemplo mantém `schema_name`/`route_prefix` para compatibilidade com o import atual; com a implementação desta spec, eles **deixam de ser exigidos** quando `frontend_only: true`.

### Semântica por tipo de módulo

| Tipo | `frontend_only` | `schema_name`/`route_prefix` | Migration | Models/Routers |
|------|----------------|------------------------------|-----------|----------------|
| Backend postgres (default) | `false` / ausente | Obrigatórios | Sim | Sim |
| Backend sqlserver | `false` (usa `target_api: "sqlserver"`) | Obrigatórios | Ignorado | Não |
| **Frontend-only** | `true` | **Opcionais** | **Ignorado** | **Não existe** |

## 2. Mudanças no `import_module.py`

### 2.1 `validate_manifest` — campos obrigatórios condicionais

`apps/api-postgres/scripts/import_module.py`, função `validate_manifest` (atualmente linhas 94-118):

- Se `manifest.get("frontend_only")` for `true`, `schema_name` e `route_prefix` **saem da lista** `required`.
- A lista `required` passa a ser condicional:

```python
def validate_manifest(import_dir: Path) -> dict:
    ...
    required = ["module_name", "entity_name", "menu_label"]
    if not manifest.get("frontend_only"):
        required += ["schema_name", "route_prefix"]
    ...
```

### 2.2 `import_module` — pular migrações para frontend-only

Bloco atual (linhas 823-835):

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
            logger.warning("Migration falhou ...")
            steps.append(...)
```

Nova condição: adicionar `manifest.get("frontend_only")` no guard — módulo frontend-only não roda migrações:

```python
is_frontend_only = manifest.get("frontend_only", False)
...
if target_api != "sqlserver" and not is_frontend_only:
    ...  # bloco atual inalterado
else:
    steps.append("Módulo frontend-only — sem migrações")
```

Nota: o bloco `else` já existe para `sqlserver`; o `steps.append` deve refletir o tipo (mensagem genérica "sem migrações" ou específica por tipo).

## 3. Mudanças no `import_router.py`

### 3.1 Scan — sem mudança de lógica obrigatória

O scan (`/v1/import/scan`) já cobre frontend-only:

- `ja_importado` (linhas 127-152): `in_backend_fs or in_frontend_fs` — o import copia o `module.json` para `app/modules/{slug}/module.json` mesmo sem backend (linhas 767-778 do script), criando o "phantom dir" que torna `in_backend_fs` verdadeiro.
- `pode_remover` (linha 220): `= tem_backend` — com o phantom dir, permanece `True`, então a remoção continua funcionando.

**Requisito de nomenclatura (sem normalização de `_`↔`-`)**: o nome da pasta de frontend no módulo deve ser **idêntico** ao `module_name` (ex: `pop_viz`, não `pop-viz`). O `in_frontend_fs` (linhas 130-141) casa por `startswith(slug)` e o fallback de remoção (`startswith(module_name)`) usa o mesmo padrão — nome idêntico garante detecção e remoção corretas. Este é um requisito documental para o autor do módulo, não uma mudança de código.

### 3.2 Sem alteração no POST/DELETE

O router de import/remoção não precisa de mudanças: chama `run_import`/`remove_module` que já são tolerantes a ausência de backend.

## 4. Documentação

`apps/api-postgres/../docs/IMPORTACAO.md` (tabela de campos, linhas 222-239):

- `schema_name`: de "Sim" para "Sim, exceto frontend-only (`frontend_only: true`)".
- `route_prefix`: idem.
- Novo campo `frontend_only` na tabela: "Não | Marca o módulo como frontend-only — dispensa `schema_name`/`route_prefix` e pula migrações (default: `false`)".
- Seção de troubleshooting: manter a mensagem atual (o erro "Campos obrigatórios ausentes" agora só ocorre sem o flag e sem os campos).

## 5. Testes

Adicionar testes unitários em `apps/api-postgres/tests/unit/` (padrão dos existentes `test_import_router.py`, `test_import_module_sqlserver.py`):

- `validate_manifest` aceita manifesto frontend-only **sem** `schema_name`/`route_prefix`.
- `validate_manifest` rejeita manifesto sem o flag e sem esses campos (comportamento atual preservado).
- `import_module` com `frontend_only: true` não executa `run_migrations` (mock do subprocess/alembic).
- Scan: módulo frontend-only importado aparece como `ja_importado` e com `pode_remover` `true`.

## 6. Critérios de aceite

- Um zip de módulo frontend-only (ex: `pop_viz`) com `frontend_only: true` e sem `schema_name`/`route_prefix` é importado com sucesso pelo `/v1/import/{slug}` e pelo CLI.
- O log de import de frontend-only indica "sem migrações" e não executa `alembic upgrade head`.
- Módulos backend existentes (postgres/sqlserver) continuam importando sem regressão.
- O módulo frontend-only aparece no scan como importado e pode ser removido pela UI.

## 7. Fora de escopo

- Normalização de `_`↔`-` no scan (`in_frontend_fs`) — decidido manter o requisito de nome idêntico no módulo.
- Alterações no `pop_viz` em si (o flag já é adicionado no módulo, em paralelo a esta spec).
