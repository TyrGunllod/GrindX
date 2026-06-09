<!-- title: Banco de Dados — GrindX | updated: 2026-05-28 -->

# Banco de Dados — GrindX

---

## Tecnologia

- **ORM:** SQLAlchemy 2.0 (estilo declarativo moderno)
- **Banco:** PostgreSQL 14+ (`api-postgres`) e SQL Server (`api-sqlserver`, somente leitura)
- **Driver PostgreSQL:** `psycopg` (psycopg3) — `postgresql+psycopg://`
- **Driver SQL Server:** `pymssql` ou `pyodbc` — escolhido automaticamente pelo `config.py`
- **Migrações:** Alembic

---

## Arquitetura Multi-Schema

Os modelos são organizados em **4 schemas de domínio** no PostgreSQL, cada um com seu próprio `DeclarativeBase`:

| Schema | Base | Domínio |
|--------|------|---------|
| `iam` | `IamBase` | Autenticação, usuários, perfis |
| `portal` | `PortalBase` | Navegação dinâmica (abas, módulos) |
| `catalogo` | `CatalogoBase` | Produtos, catálogo |
| `org` | `OrgBase` | Empresa, temas, organização |

Todas as bases compartilham um único `registry()` e `MetaData()`, com schema definido via `__table_args__` herdado. Isso permite chaves estrangeiras entre schemas (ex: `usuario_modulos` em `iam` referenciando `portal_modulos` em `portal`).

**Localização dos modelos:**

```
app/modules/
├── iam/
│   ├── base.py           # IamBase, registry, metadata
│   └── models/
│       └── usuario.py    # Usuario, UsuarioModulo
├── portal/
│   ├── base.py           # PortalBase
│   └── models/
│       └── portal.py     # Aba, Modulo
├── catalogo/
│   ├── base.py           # CatalogoBase
│   └── models/
│       └── produto.py    # Produto
└── org/
    ├── base.py           # OrgBase
    └── models/
        ├── empresa.py    # Empresa
        ├── theme.py      # CompanyTheme
        └── theme_history.py  # ThemeHistory
```

Os arquivos em `app/models/*.py` foram mantidos como **re-export shims** para compatibilidade com código existente (repositories, routers, seed).

---

## Modelos (`api-postgres`)

### Schema `iam` — Usuario

Gerencia autenticação e controle de acesso.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `username` | String(50) único | Login do usuário |
| `email` | String(255) único | E-mail |
| `nome_completo` | String(150) | Nome exibido |
| `senha_hash` | String(255) | Hash bcrypt |
| `role` | String(20) | `admin`, `operador` ou `leitura` |
| `ativo` | Boolean | Se pode fazer login |
| `empresa_id` | Integer FK → `org.empresas` (nullable) | Empresa do usuário |
| `criado_em` | DateTime(tz) | Data de criação |
| `atualizado_em` | DateTime(tz) | Última atualização |

### Schema `iam` — UsuarioModulo (tabela associativa)

Gerencia permissão de módulos por usuário (M2M entre Usuario ↔ Modulo).

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `usuario_id` | Integer PK, FK → `iam.usuarios` | Usuário |
| `modulo_id` | Integer PK, FK → `portal.portal_modulos` | Módulo permitido |
| `concedido_em` | DateTime(tz) | Data da concessão |
| `concedido_por_id` | Integer FK → `iam.usuarios` (nullable) | Quem concedeu |

### Schema `catalogo` — Produto

Gerencia o catálogo transacional.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `nome` | String(100) | Nome do produto |
| `descricao` | String(500) (nullable) | Descrição |
| `preco` | Numeric(10,2) | Preço unitário |
| `ativo` | Boolean | Se está disponível |
| `criado_em` | DateTime(tz) | Data de criação |
| `atualizado_em` | DateTime(tz) | Última atualização |

### Schema `portal` — Aba

Gerencia a árvore de navegação dinâmica do frontend.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `parent_id` | Integer FK self-ref (nullable) | Aba pai para hierarquia aninhada |
| `nome` | String(50) | Nome exibido no menu |
| `icone` | String(50) (nullable) | Nome do ícone |
| `ordem` | Integer | Posição no menu |
| `ativo` | Boolean | Se aparece no menu |

Relationship: `parent` → Aba, `children` → List[Aba]

### Schema `portal` — Modulo

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `aba_id` | Integer FK → `portal.portal_abas` | Aba pai |
| `nome` | String(100) | Nome exibido |
| `slug` | String(100) único | Identificador amigável para URL |
| `url` | String(255) | Caminho relativo do HTML |
| `icone` | String(50) (nullable) | Nome do ícone |
| `role_minima` | String(20) | Role mínima para acesso (admin, operador, leitura) |
| `ativo` | Boolean | Se aparece no menu |

### Schema `org` — Empresa

Representa uma empresa/organização no sistema.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `nome` | String(100) | Nome da empresa |
| `dominio` | String(255) único (nullable) | Domínio/subdomínio para multi-tenant |
| `ativo` | Boolean | Se está ativa |
| `criado_em` | DateTime(tz) | Data de criação |
| `atualizado_em` | DateTime(tz) | Última atualização |

### Schema `org` — CompanyTheme

Tema visual (skin) personalizado por empresa. Suporta dois layouts: `sidebar` (padrão para temas existentes) e `topbar`.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `company_id` | Integer FK → `org.empresas` | Empresa dona do tema |
| `name` | String(100) | Nome da skin |
| `is_active` | Boolean | Skin ativa (apenas 1 por empresa) |
| `layout_mode` | String(20) | `topbar` (padrão) ou `sidebar` |
| `colors` | JSON (nullable) | Overrides de cores CSS (`--skin-*`) |
| `fonts` | JSON (nullable) | Overrides de fontes (`heading`, `body`) |
| `tokens` | JSON (nullable) | Tokens CSS extras (`--skin-radius-*`, `--skin-shadow-*`) |
| `icon_library` | String(50) | Biblioteca de ícones (ex: `fontawesome`) |
| `logo_url` | String(500) (nullable) | URL do logo customizado |
| `logo_short_url` | String(500) (nullable) | URL do logo para favicon |
| `company_name` | String(100) (nullable) | Nome exibido no sistema |
| `copyright_text` | String(200) (nullable) | Texto do rodapé |
| `criado_em` | DateTime(tz) | Data de criação |
| `atualizado_em` | DateTime(tz) | Última atualização |

### Schema `org` — ThemeHistory

Histórico de alterações de tema para auditoria.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `theme_id` | Integer FK → `org.company_themes` | Tema alterado |
| `company_id` | Integer FK → `org.empresas` | Empresa |
| `action` | String | Tipo de ação (`created`, `updated`, `activated`, `deleted`) |
| `performed_by` | Integer FK → `iam.usuarios` (nullable) | Usuário que realizou a ação |
| `theme_snapshot` | JSON | Estado completo do tema após a ação |
| `changes` | JSON (nullable) | Diff das alterações (apenas em `updated`) |
| `criado_em` | DateTime(tz) | Data da alteração |

---

## Conexão

### PostgreSQL

A URL de conexão usa psycopg3 por padrão:

```
postgresql+psycopg://usuario:senha@host:porta/banco
```

### SQL Server

A URL é construída automaticamente pelo `Settings.DATABASE_URL` em `app/core/config.py` com base nas variáveis `DB_SERVER`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD` e `DB_DRIVER`.

Se `DB_DRIVER` contiver "ODBC", usa pyodbc. Caso contrário, usa pymssql com porta separada por `:` (ao invés de `,`).

---

## Migrações (Alembic)

```powershell
cd apps/api-postgres

# Criar nova migração após alterar um model
alembic revision --autogenerate -m "adiciona campo X em Produto"

# Aplicar todas as migrações pendentes
python manage_db.py upgrade head

# Ver migração atual
alembic current

# Histórico de migrações
alembic history

# Reverter uma migração
alembic downgrade -1

# Reverter todas
alembic downgrade base
```

As migrações ficam em `apps/api-postgres/alembic/versions/`.

| Arquivo | Descrição |
|---------|-----------|
| `001_initial.py` | Criação inicial dos modelos (schema `public`) |
| `002_add_company_theme.py` | Adiciona CompanyTheme e ThemeHistory (`public`) |
| `003_add_empresa_model.py` | Adiciona modelo Empresa (`public`) |
| `004_add_usuario_empresa.py` | Adiciona empresa_id em Usuario (`public`) |
| `005_add_aba_parent_id.py` | Adiciona parent_id em portal_abas (`public`) |
| `006_add_performance_indexes.py` | Índices B-tree para performance |
| `007_add_org_schema_tables.py` | Cria schema `org` e move tabelas |
| `008_add_temp_password_fields.py` | Campos de senha temporária |
| `009_add_layout_mode.py` | Adiciona `layout_mode` em `company_themes` |

---

## Dados Iniciais (seed)

```powershell
cd apps/api-postgres
python seed.py
```

Cria:

- Skin "Padrão GrindX" com `logo_url` definido para um logo padrão
- Empresa `GrindX` com dominio `grindx.local`
- Usuário `admin` / `admin123` com role `admin` — vinculado à GrindX
- Usuário `operador` / `operador123` com role `operador` — vinculado à GrindX
- Usuário `leitura` / `leitura123` com role `leitura` — vinculado à GrindX
- Usuários sem empresa são vinculados automaticamente à GrindX
- Estrutura inicial de abas e módulos no portal

---

## Backup

```powershell
# Dump completo
pg_dump -U postgres grindx > grindx_backup.sql

# Restaurar
psql -U postgres grindx < grindx_backup.sql
```

Em produção, agendar backup diário via cron ou ferramenta do provedor de banco.
