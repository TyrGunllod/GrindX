# Procedimento de Importação de Módulos

Guia completo para importar módulos standalone do `Project_Management` para o `GrindX` via `.zip`.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Comandos Make](#comandos-make)
- [Gerar os Zips](#gerar-os-zips)
- [Estrutura do Zip](#estrutura-do-zip)
- [Campo module.json](#campo-modulejson)
- [Importar via API](#importar-via-api)
- [Importar via Frontend](#importar-via-frontend)
- [Ordem de Importação](#ordem-de-importação)
- [Verificação Pós-Importação](#verificação-pós-importação)
- [Desfazer Importação (Rollback)](#desfazer-importação-rollback)
- [Troubleshooting](#troubleshooting)

---

## Visão Geral

O GrindX possui um sistema de importação que aceita módulos compactados em `.zip` com um manifesto `module.json`. O processo:

1. **Empacota** o módulo standalone em um `.zip` (via `export.py package`)
2. **Copia** o `.zip` para a pasta `import/` do GrindX
3. **Importa** via API (`POST /v1/import/{module_name}`) ou frontend (módulo Importer)

O importador executa steps automaticamente. O fluxo depende do campo `target_api`:

**Para módulos PostgreSQL (padrão):**
1. Valida o `module.json`
2. Faz backup dos arquivos que serão modificados
3. Copia o backend para `app/modules/{module_name}/`
4. Mescla os requirements do módulo
5. Copia o frontend para `modules/{module_name}/`
6. Copia migrations para `alembic/versions/`
7. Registra as rotas em `main.py`
8. Registra a dependency factory em `auth/dependencies.py`
9. Registra o import do model em `alembic/env.py`
10. Registra no menu
11. Agenda a migração `alembic upgrade head` em **segundo plano**

> A migração roda em background — o script registra `"Migração adiada (executada em segundo plano)"` e o router adiciona `"Migrações agendadas em segundo plano"`.

**Para módulos SQL Server (`target_api: "sqlserver"`):**
- Copia o backend para `apps/api-sqlserver/app/modules/{module_name}/`
- Registra as rotas no `main.py` do api-sqlserver
- **Pula** migration, dependency factory e alembic/env.py (não aplicável)
- **Pula** `alembic upgrade head` (sem schema para gerenciar)
- **Pula** o backup (`backup_existing` retorna `None` — "backup desnecessário")

---

## Pré-requisitos

- Python 3.12+
- GrindX clonado e funcionando
- Dependências instaladas: `pip install -r requirements.txt`
- Variável de ambiente configurada (para testes):
  ```powershell
  $env:GRINDX_PACKAGES = "D:\_Projetos\GrindX\packages"
  ```

---

## Comandos Make

Cada módulo possui um `Makefile` com comandos prontos. Use `make` no diretório do módulo:

| Comando | O que faz |
|---------|-----------|
| `make help` | Exibe todos os comandos disponíveis |
| `make test` | Roda todos os testes |
| `make test-unit` | Roda apenas testes unitários |
| `make test-integration` | Roda apenas testes de integração |
| `make package` | Gera o zip para importação |
| `make dry-run` | Simula a geração do zip |
| `make import` | Gera zip + copia para `import/` do GrindX |
| `make export` | Exporta direto para o GrindX (CLI) |
| `make clean` | Limpa caches e `__pycache__` |

**Fluxo rápido de importação:**

```powershell
cd D:\_Projetos\Project_Management\modulo-projeto
make import
```

Isso gera o zip e copia automaticamente para `D:\_Projetos\GrindX\import\`. Depois é só importar via API ou frontend.

---

## Gerar os Zips

### Via Makefile (recomendado)

```powershell
cd D:\_Projetos\Project_Management\modulo-{nome}
make package
```

O zip é gerado em `dist/modulo-{nome}.zip` e a estrutura é exibida no terminal.

### Via Python (alternativa)

```powershell
cd D:\_Projetos\Project_Management\modulo-{nome}
python -m app.modules.{nome}.export package
```

### Gerar todos os módulos

```powershell
cd D:\_Projetos\Project_Management
foreach ($mod in @("projeto", "recursos", "tarefas", "cronograma", "dashboard")) {
    cd "modulo-$mod"
    make package
    cd ..
}
```

### Dry-run (simular sem gerar)

```powershell
make dry-run
```

---

## Estrutura do Zip

### Para módulos PostgreSQL (`target_api` omitido ou `"postgres"`)

```
modulo-{nome}.zip
├── module.json                    ← Manifesto (obrigatório)
├── app/modules/{nome}/            ← Backend
│   ├── __init__.py
│   ├── base.py
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── routers/
│   └── tests/
├── frontend/                      ← Frontend
│   ├── index.html
│   ├── script.js
│   └── style.css
└── migration/                     ← Migrations Alembic (opcional)
    └── 0001_...py
```

### Para módulos SQL Server (`target_api: "sqlserver"`)

```
modulo-{nome}.zip
├── module.json                    ← Manifesto (obrigatório)
├── app/modules/{nome}/            ← Backend (sem models/ nem base.py)
│   ├── __init__.py
│   ├── exceptions.py
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   └── routers/
├── frontend/                      ← Frontend
│   ├── index.html
│   ├── script.js
│   └── style.css
└── (migration/ é ignorado se presente)
```

**Diferenças importantes:**
- **Sem `models/` e `base.py`** — consultas SQL raw via `text()` nas repositories
- **Sem `migration/`** — sem schema para gerenciar (aponta para tabelas do Protheus)
- **`frontend/shared/` é ignorado** pelo importador (já existe no monorepo)
- **Apenas GET** — os módulos sqlserver são read-only por definição

**Importante:** `module.json` deve estar na raiz do zip, não dentro de um subdiretório.

---

## Campo module.json

O manifesto `module.json` contém os metadados do módulo. Campos obrigatórios para o importador:

```json
{
  "module_name": "projeto",
  "entity_name": "Projeto",
  "version": "1.0.0",
  "schema_name": "org",
  "table_name": "projetos",
  "route_prefix": "/v1/projetos",
  "route_tag": "Projetos",
  "frontend_url": "modules/projeto/index.html",
  "menu_label": "Projetos",
  "menu_icone": "folder",
  "role_minima": "operador",
  "dependencies": []
}
```

Para módulos SQL Server (read-only), adicione `target_api: "sqlserver"`:

```json
{
  "module_name": "custo",
  "entity_name": "CustoProduto",
  "target_api": "sqlserver",
  "schema_name": "custo",
  "route_prefix": "/v1/produtos/custos",
  "route_tag": "Custo Produto",
  "frontend_tabs": [
    {"name": "Custos", "url": "modules/custos/index.html", "menu_icone": "calculator", "order": 1}
  ],
  "menu_label": "Custo Produto",
  "menu_icone": "calculator",
  "role_minima": "leitura"
}
```

Para módulos **frontend-only** (sem backend — só HTML/CSS/JS, reutilizando endpoints de outro módulo), adicione `frontend_only: true`:

```json
{
  "module_name": "pop_viz",
  "entity_name": "PopViz",
  "version": "1.0.0",
  "frontend_only": true,
  "frontend_tabs": [
    {"name": "Visualizador POP", "url": "modules/pop_viz/index.html"}
  ],
  "menu_label": "Visualizador POP",
  "menu_icone": "folder",
  "role_minima": "leitura",
  "dependencies": ["pop_docs"]
}
```

Módulos frontend-only **dispensam** `schema_name`/`route_prefix` e **não rodam migrações**. A pasta de frontend deve ter o **mesmo nome** do `module_name` (ex: `pop_viz`, não `pop-viz`) — o scan e a remoção dependem desse nome idêntico.

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `module_name` | Sim | Nome técnico em snake_case |
| `entity_name` | Sim | Nome da entidade em PascalCase |
| `schema_name` | Sim* | Schema do banco (`org`, `catalogo`, `portal`, `custo`) — exceto frontend-only (`frontend_only: true`) |
| `route_prefix` | Sim* | Prefixo da URL da API — exceto frontend-only (`frontend_only: true`) |
| `frontend_url` | Sim* | Caminho do HTML no frontend (ou `frontend_tabs`) |
| `frontend_tabs` | Sim* | Lista de abas com `name`, `url`, `menu_icone`, `order` |
| `menu_label` | Sim | Rótulo no menu lateral |
| `target_api` | Não | API alvo: `"postgres"` (default) ou `"sqlserver"` |
| `frontend_only` | Não | Marca o módulo como frontend-only — dispensa `schema_name`/`route_prefix` e pula migrações (default: `false`) |
| `version` | Não | Versão do módulo (semver) |
| `table_name` | Não | Nome da tabela (null para read-only) |
| `route_tag` | Não | Tag no Swagger |
| `menu_icone` | Não | Ícone do menu (default: `folder`) |
| `role_minima` | Não | Role mínima (default: `operador`) |
| `dependencies` | Não | Lista de módulos dependentes |

> `*` Obrigatório: `frontend_url` OU `frontend_tabs`.
> `*` `schema_name` e `route_prefix` são obrigatórios, exceto quando `frontend_only: true`.

---

## Importar via API

### 1. Copiar o zip para a pasta import/

```powershell
# Via Makefile (recomendado — já gera o zip)
cd D:\_Projetos\Project_Management\modulo-projeto
make import

# Ou manualmente
Copy-Item modulo-projeto\dist\modulo-projeto.zip D:\_Projetos\GrindX\import\

# Copiar todos
Copy-Item modulo-*\dist\modulo-*.zip D:\_Projetos\GrindX\import\
```

### 2. Escanear módulos disponíveis

```bash
curl -X GET -H "Authorization: Bearer <token>" http://localhost:8002/v1/import/scan
```

O `scan` é um endpoint **GET** e retorna `{modules: [...], instalados: [...]}`, cada item com os campos `slug`, `module_name`, `entity_name`, `version`, `menu_label`, `schema_name`, `target_api`, `ja_importado` e `pode_remover`:
```json
{
  "modules": [
    {
      "slug": "projeto",
      "module_name": "projeto",
      "entity_name": "Projeto",
      "version": "1.0.0",
      "menu_label": "Projetos",
      "schema_name": "org",
      "target_api": "postgres",
      "ja_importado": false,
      "pode_remover": true
    },
    {
      "slug": "custo",
      "module_name": "custo",
      "entity_name": "CustoProduto",
      "version": "1.0.0",
      "menu_label": "Custo Produto",
      "schema_name": "custo",
      "target_api": "sqlserver",
      "ja_importado": false,
      "pode_remover": true
    }
  ],
  "instalados": []
}
```

### 3. Importar o módulo

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  http://localhost:8002/v1/import/projeto
```

O parâmetro `force` **tem default `true`** — reimportar sempre sobrescreve por padrão. Para uma reimportação sem sobrescrever, use `?force=false`:

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  "http://localhost:8002/v1/import/projeto?force=false"
```

Resposta (sucesso — ~11 etapas para módulos PostgreSQL):
```json
{
  "success": true,
  "message": "Módulo importado com sucesso",
  "steps": [
    "Manifesto validado",
    "Backup concluído",
    "Backend copiado",
    "Requirements mesclados",
    "Frontend copiado",
    "Migration copiada",
    "Router registrado",
    "Dependency registrado em dependencies.py",
    "Import do model registrado no alembic/env.py",
    "Menu registrado",
    "Migração adiada (executada em segundo plano)"
  ]
}
```

> A migração Alembic roda **em segundo plano**; o router adiciona a etapa `"Migrações agendadas em segundo plano"`. Para módulos `sqlserver`, o backup é **pulado** (`backup_existing` retorna `None` — "backup desnecessário").

#### Executar o script importador diretamente

O script real fica em `apps/api-postgres/scripts/import_module.py`. A partir de `apps/api-postgres`:

```powershell
python scripts/import_module.py {nome} --import-dir={tmp} --target-api=sqlserver --force
```

Para remover um módulo importado, use `--remove` (o endpoint `DELETE /v1/import/{module_name}` também remove).

---

## Importar via Frontend

1. Acesse o GrindX → Aba **Gestão** → **Importar Módulos**
2. Clique em **Escanear** para listar os zips na pasta `import/`
3. O módulo aparece na lista com status "Não importado"
4. Clique no módulo → expande o card com detalhes
5. Clique em **Importar** → confirma no modal
6. O log das ~11 etapas aparece em tempo real

---

## Ordem de Importação

Para módulos com dependências, importe nesta ordem:

| Ordem | Módulo | Depende de |
|-------|--------|------------|
| 1 | `projeto` | — |
| 2 | `recursos` | — |
| 3 | `tarefas` | `projeto`, `recursos` |
| 4 | `cronograma` | `tarefas`, `projeto`, `recursos` |
| 5 | `dashboard` | `projeto`, `tarefas`, `recursos` |

**Regra geral:** importe módulos sem FK primeiro. Módulos que referenciam outros (via FK) devem ser importados depois.

---

## Verificação Pós-Importação

### 1. Verificar rotas registradas

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8002/v1/projetos
```

### 2. Verificar menu

O módulo deve aparecer no menu lateral do portal.

### 3. Verificar frontend

Acesse `http://localhost:8101/modules/projeto/index.html`

### 4. Verificar migration

```bash
cd D:\_Projetos\GrindX\apps\api-postgres
python -m alembic current
```

A tabela `org.projetos` deve estar listada.

---

## Desfazer Importação (Rollback)

O importador cria backup automático antes de cada import. Se algo falhar, o rollback é automático.

Para rollback manual, restaure os arquivos do backup:
```
import/.backup/{module_name}_{timestamp}/
├── main.py
├── dependencies.py
└── env.py
```

Para remover um módulo importado, use `DELETE /v1/import/{module_name}` (admin) ou rode o script com `--remove`. Reimportar sobrescreve por padrão (`force` tem default `true`).

---

## Troubleshooting

### "Campos obrigatórios ausentes no module.json"

O `module.json` não contém todos os campos obrigatórios. Verifique se o zip foi gerado com `make package` (não manualmente). Para módulos frontend-only, o erro só ocorre se `frontend_only: true` estiver ausente.

### "Router já registrado em main.py"

O módulo já foi importado anteriormente. Reimportar já sobrescreve por padrão (`force` tem default `true`). Para não sobrescrever, use `?force=false`.

### "Migration falhou"

Verifique se as tabelas dependentes já existem no banco. Para módulos com FKs, importe as dependências primeiro.

### "module.json não encontrado dentro do zip"

O zip não contém `module.json` na raiz. Regenere com `make package`.

### Zip com estrutura errada

Se o zip contém `modulo-{nome}/app/modules/...` em vez de `app/modules/...`, regenere com `make package`.

### Módulo SQL Server não aparece como importado

Módulos sqlserver são copiados para `apps/api-sqlserver/app/modules/`, não para `apps/api-postgres/app/modules/`. O scan verifica ambos os diretórios. Se o módulo não aparece como importado, verifique se o diretório foi criado no api-sqlserver.

---

## Referência Rápida

```powershell
# Entrar no diretório do módulo
cd D:\_Projetos\Project_Management\modulo-projeto

# Ver comandos disponíveis
make help

# Gerar zip e copiar para import/ do GrindX
make import

# Gerar zip sem copiar
make package

# Rodar testes
make test

# Importar via API (depois de copiar o zip)
curl -X POST -H "Authorization: Bearer <token>" http://localhost:8002/v1/import/projeto
```
