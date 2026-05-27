# Importação de Módulos via UI

## Data: 2026-05-27

## Problema

Atualmente, adicionar um novo módulo no GrindX exige criar manualmente 10+ arquivos (model, schema, repository, service, router, frontend, migração) e modificar `main.py`, `dependencies.py` e `alembic/env.py` — tudo via CLI ou edição manual. Não há uma interface visual para detectar, visualizar e importar módulos empacotados.

## Solução

Um sistema de importação onde módulos desenvolvidos fora do monorepo (via `create-standalone-module`) são empacotados em `.zip` com um manifesto (`module.json`), colocados em uma pasta `import/` na raiz do projeto, e importados com um clique via nova interface no frontend.

## Abordagem Escolhida

**Abordagem 1 — API de Importação Server-Side** (recomendada):
- Backend escaneia a pasta `import/` e lê os manifestos
- Importação executada via subprocesso separado que reusa a lógica do `export.py`
- Frontend chama endpoints REST para listar e importar
- Ferramenta de desenvolvimento local, não de produção em container

### Descartadas

**Abordagem 2 — Scanner + CLI Assistido:** o admin precisaria ir ao terminal, o que quebra a experiência "um botão".

**Abordagem 3 — Pipeline Híbrido com Worker:** complexidade desnecessária para um monorepo on-premise.

## 1. Manifesto (`module.json`)

Arquivo JSON na raiz do `.zip` com metadados do módulo:

```json
{
  "module_name": "projetos",
  "entity_name": "Projeto",
  "version": "1.0.0",
  "schema_name": "org",
  "table_name": "projetos",
  "route_prefix": "/v1/projetos",
  "route_tag": "Projetos",
  "frontend_url": "modules/projetos/index.html",
  "menu_label": "Projetos",
  "menu_icone": "folder",
  "role_minima": "operador",
  "migration_revision": "abc123def",
  "dependencies": []
}
```

O `module.json` é gerado automaticamente pelo `create-standalone-module` ao criar o módulo, e incluído no `.zip` pelo comando `package`.

## 2. Estrutura do `.zip`

```
modulo-{nome}.zip
├── module.json
├── app/modules/{module_name}/
│   ├── __init__.py
│   ├── base.py
│   ├── models/...
│   ├── schemas/...
│   ├── repositories/...
│   ├── services/...
│   ├── routers/...
│   └── tests/...
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
└── migration/
    └── {revision}_{table_name}.py
```

## 3. Backend — Endpoints

### `import_router.py`

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/v1/import/scan` | Escaneia `import/*.zip`, lê `module.json`, retorna lista com status (novo/importado) |
| `POST` | `/v1/import/{module_name}` | Importa o módulo: extrai zip, copia arquivos, edita registros, roda migração |

**`GET /v1/import/scan`**:
- Varre `import/*.zip` no diretório raiz do monorepo
- Para cada zip, extrai e lê `module.json`
- Compara com `portal_modulos` (pelo slug) para determinar se já foi importado
- Retorna: `[{ slug, module_name, entity_name, version, menu_label, schema_name, ja_importado }]`

**`POST /v1/import/{module_name}?force=false`**:
- Valida se o zip existe e contém `module.json` válido
- Extrai para diretório temporário
- Chama subprocesso: `python scripts/import_module.py {module_name} --import-dir={tmp}`
- Aguarda conclusão e retorna stdout/stderr como log

### `scripts/import_module.py`

Script executor que realiza a importação de fato:

1. **Backup**: Cria `import/.backup/{timestamp}/` com cópia dos arquivos que serão modificados (`main.py`, `dependencies.py`, `env.py`)
2. **Copia backend**: `app/modules/{module_name}/` → `packages/api-postgres/app/modules/{module_name}/`
3. **Copia frontend**: `frontend/` → `packages/frontend-webapp/modules/{module_name}/`
4. **Copia migração**: `migration/*.py` → `packages/api-postgres/alembic/versions/`
5. **Edita `main.py`**: adiciona `import router` + `app.include_router()`
6. **Edita `dependencies.py`**: adiciona factory do service
7. **Edita `alembic/env.py`**: adiciona import do model
8. **Roda migração**: `alembic upgrade head` (subprocesso)
9. **Registra no menu**: insere/atualiza `portal_modulos` via SQL direto

Em caso de erro em qualquer etapa, reverte usando o backup.

## 4. Frontend — Módulo `modules/importer/`

### index.html

Segue o padrão dos demais módulos: page-header com título + container de lista + modal de confirmação.

### script.js — `ImporterController`

| Funcionalidade | Detalhe |
|----------------|---------|
| `carregar()` | `GET /v1/import/scan` → renderiza tabela |
| Botão "Importar" | Abre modal com dados do `module.json` e log |
| Confirmar | `POST /v1/import/{slug}` → exibe resultado |
| Reimportar | Se já importado, `POST /v1/import/{slug}?force=true` |
| Botão "Atualizar" | Re-executa scan |

### Colunas da Tabela

Nome, Versão, Schema, Status (Novo ✔️ / Importado 🔄 / Erro ❌), Ações [Importar / Reimportar]

## 5. Modificações na Skill `create-standalone-module`

### A. Gerar `module.json` no standalone

Adicionar criação de `module.json` na raiz do projeto standalone com os parâmetros coletados.

### B. Comando `package` no `export.py`

```bash
python -m app.modules.{nome}.export package
# Gera dist/modulo-{nome}.zip com module.json + app/ + frontend/ + migration/
```

### C. Script de empacotamento (opcional)

`scripts/package.ps1` para criar o `.zip` manualmente se preferir.

## 6. Pasta `import/` na Raiz

```
D:\_Projetos\GrindX\
├── import/                  ← NOVA
│   ├── projetos.zip
│   ├── workflow.zip
│   └── .backup/             ← backups automáticos
├── packages/
│   ├── api-postgres/
│   └── frontend-webapp/
└── ...
```

## 7. Nota sobre Importação por URL

A funcionalidade existente de definir uma URL externa no campo `url` da `portal_modulos` (que carrega no iframe) permanece inalterada. O sistema de importação descrito aqui trata apenas de módulos empacotados em `.zip`, não substitui a capacidade de apontar para páginas web arbitrárias.

## 8. Segurança e Restrições

- **Uso exclusivo em desenvolvimento local** — não exposto nem disponível em container de produção
- **Admin role** — apenas usuários admin podem ver o módulo `importer` e chamar os endpoints
- **Rollback automático** — backup salvo antes de modificar arquivos; reversão em caso de falha
- **Validação de manifesto** — schema do `module.json` validado antes de qualquer operação

## 9. Testes

- Teste unitário do `import_module.py` com diretório temporário mockado
- Teste da `import_router.py` com zip mock
- Teste de rollback: simular falha e verificar se arquivos originais foram restaurados
- Teste de conflito: importar módulo já existente com e sem `force`
