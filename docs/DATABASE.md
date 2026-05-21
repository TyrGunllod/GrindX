<!-- title: Banco de Dados — GrindX | updated: 2026-05-20 -->

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
| `role` | Enum | `admin` ou `operador` |
| `ativo` | Boolean | Se pode fazer login |
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
| `nome` | String | Nome exibido no menu |
| `icone` | String | Nome do ícone |
| `ordem` | Integer | Posição no menu |
| `ativo` | Boolean | Se aparece no menu |

**Modulo:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `aba_id` | Integer FK | Referência à Aba |
| `nome` | String | Nome exibido |
| `url` | String | Caminho relativo do HTML |
| `icone` | String | Nome do ícone |
| `ordem` | Integer | Posição dentro da aba |
| `ativo` | Boolean | Se aparece no menu |

### Empresa

Representa uma empresa/organização no sistema.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `nome` | String | Nome da empresa |
| `cnpj` | String (único) | CNPJ formatado |
| `ativo` | Boolean | Se está ativa |
| `created_at` | DateTime | Data de criação |

### CompanyTheme

Tema visual (skin) personalizado por empresa.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `company_id` | Integer FK | Referência à Empresa |
| `name` | String | Nome da skin |
| `is_active` | Boolean | Skin ativa (apenas 1 por empresa) |
| `colors` | JSONB | Overrides de cores CSS |
| `fonts` | JSONB | Overrides de fontes |
| `radius` | JSONB | Overrides de border-radius |
| `shadows` | JSONB | Overrides de box-shadow |
| `logo_url` | String | URL do logo customizado |
| `company_name_display` | String | Nome exibido no UI |
| `created_at` | DateTime | Data de criação |
| `updated_at` | DateTime | Última atualização |

### ThemeHistory

Histórico de alterações de tema para auditoria.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `theme_id` | Integer FK | Referência ao CompanyTheme |
| `changed_by` | Integer FK | Usuário que alterou |
| `action` | String | Tipo de ação (create, update, activate, deactivate) |
| `old_values` | JSONB | Valores anteriores |
| `new_values` | JSONB | Valores novos |
| `created_at` | DateTime | Data da alteração |

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

---

## Dados Iniciais (seed)

```powershell
cd packages/api-postgres
python seed.py
```

Cria:

- Empresa `GrindX` (padrão do sistema)
- Usuário `admin` / `admin123` com role `admin`
- Usuário `operador` / `operador123` com role `operador`
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
