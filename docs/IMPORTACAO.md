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

O importador executa 9 steps automaticamente:
1. Valida o `module.json`
2. Faz backup dos arquivos que serão modificados
3. Copia o backend para `app/modules/{module_name}/`
4. Copia o frontend para `modules/{module_name}/`
5. Copia migrations para `alembic/versions/`
6. Registra as rotas em `main.py`
7. Registra a dependency factory em `auth/dependencies.py`
8. Registra o import do model em `alembic/env.py`
9. Executa `alembic upgrade head` e registra no menu

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

O zip deve ter esta estrutura na raiz:

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

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `module_name` | Sim | Nome técnico em snake_case |
| `entity_name` | Sim | Nome da entidade em PascalCase |
| `schema_name` | Sim | Schema do banco (`org`, `catalogo`, `portal`) |
| `route_prefix` | Sim | Prefixo da URL da API |
| `frontend_url` | Sim | Caminho do HTML no frontend |
| `menu_label` | Sim | Rótulo no menu lateral |
| `version` | Não | Versão do módulo (semver) |
| `table_name` | Não | Nome da tabela (null para read-only) |
| `route_tag` | Não | Tag no Swagger |
| `menu_icone` | Não | Ícone do menu (default: `folder`) |
| `role_minima` | Não | Role mínima (default: `operador`) |
| `dependencies` | Não | Lista de módulos dependentes |

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
curl -H "Authorization: Bearer <token>" http://localhost:8000/v1/import/scan
```

Resposta:
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
      "ja_importado": false
    }
  ]
}
```

### 3. Importar o módulo

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  http://localhost:8000/v1/import/projeto
```

Para sobrescrever um módulo já importado:
```bash
curl -X POST -H "Authorization: Bearer <token>" \
  "http://localhost:8000/v1/import/projeto?force=true"
```

Resposta (sucesso):
```json
{
  "success": true,
  "message": "Módulo importado com sucesso",
  "steps": [
    "Manifesto validado",
    "Backup concluído",
    "Backend copiado",
    "Frontend copiado",
    "Migration copiada",
    "Router registrado",
    "Dependency registrada",
    "Import do model registrado no alembic/env.py",
    "Migrations executadas",
    "Menu registrado"
  ]
}
```

---

## Importar via Frontend

1. Acesse o GrindX → Aba **Gestão** → **Importar Módulos**
2. Clique em **Escanear** para listar os zips na pasta `import/`
3. O módulo aparece na lista com status "Não importado"
4. Clique no módulo → expande o card com detalhes
5. Clique em **Importar** → confirma no modal
6. O log das 9 etapas aparece em tempo real

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
curl -H "Authorization: Bearer <token>" http://localhost:8000/v1/projetos
```

### 2. Verificar menu

O módulo deve aparecer no menu lateral do portal.

### 3. Verificar frontend

Acesse `http://localhost:8000/modules/projeto/index.html`

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

Para sobrescrever um módulo já importado, use `?force=true` na API.

---

## Troubleshooting

### "Campos obrigatórios ausentes no module.json"

O `module.json` não contém todos os campos obrigatórios. Verifique se o zip foi gerado com `make package` (não manualmente).

### "Router já registrado em main.py"

O módulo já foi importado anteriormente. Use `?force=true` para sobrescrever.

### "Migration falhou"

Verifique se as tabelas dependentes já existem no banco. Para módulos com FKs, importe as dependências primeiro.

### "module.json não encontrado dentro do zip"

O zip não contém `module.json` na raiz. Regenere com `make package`.

### Zip com estrutura errada

Se o zip contém `modulo-{nome}/app/modules/...` em vez de `app/modules/...`, regenere com `make package`.

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
curl -X POST -H "Authorization: Bearer <token>" http://localhost:8000/v1/import/projeto
```
