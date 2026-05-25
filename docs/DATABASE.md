<!-- title: Banco de Dados — GrindX | updated: 2026-05-25 -->

# Banco de Dados — GrindX

---

## Tecnologia

- **ORM:** SQLAlchemy 2.0 (estilo declarativo moderno)
- **Banco:** PostgreSQL 14+ (`api-postgres`) e SQL Server (`api-sqlserver`, somente leitura)
- **Driver PostgreSQL:** `psycopg` (psycopg3) — `postgresql+psycopg://`
- **Driver SQL Server:** `pymssql` ou `pyodbc` — escolhido automaticamente pelo `config.py`
- **Migrações:** Alembic

---

## Modelos (`api-postgres`)

### Usuario

Gerencia autenticação e controle de acesso.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `username` | String (único) | Login do usuário |
| `email` | String (único) | E-mail |
| `nome_completo` | String | Nome exibido |
| `senha_hash` | String | Hash bcrypt |
| `role` | Enum | `admin`, `operador` ou `leitura` |
| `ativo` | Boolean | Se pode fazer login |
| `empresa_id` | Integer FK (nullable) | Referência à Empresa |
| `created_at` | DateTime | Data de criação |

### Produto

Gerencia o catálogo transacional.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `nome` | String | Nome do produto |
| `descricao` | Text | Descrição longa |
| `preco` | Numeric(10,2) | Preço unitário |
| `estoque` | Integer | Quantidade disponível |
| `ativo` | Boolean | Se está disponível |
| `created_at` | DateTime | Data de criação |
| `updated_at` | DateTime | Última atualização |

### Portal (Aba + Modulo)

Gerencia a árvore de navegação dinâmica do frontend.

**Aba:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `parent_id` | Integer FK self-ref (nullable) | Aba pai para hierarquia aninhada |
| `nome` | String | Nome exibido no menu |
| `icone` | String | Nome do ícone |
| `ordem` | Integer | Posição no menu |
| `ativo` | Boolean | Se aparece no menu |

Relationship: `parent` → Aba, `children` → List[Aba]

**Modulo:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `aba_id` | Integer FK | Referência à Aba |
| `nome` | String | Nome exibido |
| `slug` | String | Identificador amigável para URL |
| `url` | String | Caminho relativo do HTML |
| `icone` | String | Nome do ícone |
| `ordem` | Integer | Posição dentro da aba |
| `role_minima` | String | Role mínima para acesso (admin, operador, leitura) |
| `ativo` | Boolean | Se aparece no menu |

### Empresa

Representa uma empresa/organização no sistema.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `nome` | String | Nome da empresa |
| `cnpj` | String (único) | CNPJ formatado |
| `dominio` | String (único, nullable) | Domínio/subdomínio para multi-tenant |
| `ativo` | Boolean | Se está ativa |
| `created_at` | DateTime | Data de criação |

### CompanyTheme

Tema visual (skin) personalizado por empresa.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `company_id` | Integer FK | Referência à Empresa |
| `name` | String(100) | Nome da skin |
| `is_active` | Boolean | Skin ativa (apenas 1 por empresa) |
| `colors` | JSON | Overrides de cores CSS (`--skin-*`) |
| `fonts` | JSON | Overrides de fontes (`heading`, `body`) |
| `tokens` | JSON | Tokens CSS extras (`--skin-radius-*`, `--skin-shadow-*`) |
| `icon_library` | String(50) | Biblioteca de ícones (ex: `fontawesome`) |
| `logo_url` | String(500) | URL do logo customizado |
| `logo_short_url` | String(500) | URL do logo para favicon |
| `company_name` | String(100) | Nome exibido no sistema |
| `copyright_text` | String(200) | Texto do rodapé |
| `criado_em` | DateTime | Data de criação |
| `atualizado_em` | DateTime | Última atualização |

### ThemeHistory

Histórico de alterações de tema para auditoria.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `theme_id` | Integer FK | Referência ao CompanyTheme |
| `company_id` | Integer FK | Referência à Empresa |
| `action` | String | Tipo de ação (`created`, `updated`, `activated`, `deleted`) |
| `performed_by` | Integer FK (opcional) | Usuário que realizou a ação |
| `theme_snapshot` | JSON | Estado completo do tema após a ação |
| `changes` | JSON | Diff das alterações (apenas em `updated`) |
| `criado_em` | DateTime | Data da alteração |

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
cd packages/api-postgres

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

As migrações ficam em `packages/api-postgres/alembic/versions/`.

| Arquivo | Descrição |
|---------|-----------|
| `001_initial.py` | Criação inicial dos modelos |
| `002_add_company_theme.py` | Adiciona CompanyTheme e ThemeHistory |
| `003_add_empresa_model.py` | Adiciona modelo Empresa |
| `004_add_usuario_empresa.py` | Adiciona empresa_id em Usuario |
| `005_add_aba_parent_id.py` | Adiciona parent_id em portal_abas |

---

## Dados Iniciais (seed)

```powershell
cd packages/api-postgres
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
