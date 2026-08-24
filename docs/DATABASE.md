<!-- title: Banco de Dados — GrindX | updated: 2026-08-17 -->

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

Os modelos são organizados em **3 schemas de domínio** no PostgreSQL, cada um com seu próprio `DeclarativeBase`:

| Schema | Base | Domínio |
|--------|------|---------|
| `iam` | `IamBase` | Autenticação, usuários, perfis |
| `portal` | `PortalBase` | Navegação dinâmica (abas, módulos) |
| `org` | `OrgBase` | Empresa, temas, organização |

**Não existe schema `catalogo` como módulo** — não há `CatalogoBase`, nem `app/modules/catalogo/`, nem model `Produto`. A tabela `produtos` foi criada pela migration `001_initial_schema` no schema `public`, sem model/ORM correspondente, e é consultada via `api-sqlserver` (`protheus_router`). O schema `catalogo` é apenas criado vazio pelo seed (sem tabelas nem modelos).

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
└── org/
    ├── base.py           # OrgBase
    └── models/
        ├── empresa.py    # Empresa
        ├── theme.py      # CompanyTheme
        └── theme_history.py  # ThemeHistory
```

Os modelos de auditoria (`AuditLog`, `Sessao`) ficam em `app/audit/models.py`, também usando `OrgBase` (schema `org`).

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
| `temp_password_hash` | String(255) nullable | Hash bcrypt da senha temporária |
| `expires_at` | DateTime(tz) nullable | Expiração da senha temporária |
| `theme_preference` | String(10) nullable | `light`, `dark` ou null (sistema) |
| `layout_preference` | String(10) nullable | Layout preferido no desktop |
| `layout_mobile_preference` | String(10) nullable | Layout preferido no mobile |
| `codigo` | String(20) nullable | Código funcional (ex: matrícula) |
| `cbo` | String(20) nullable | Código Brasileiro de Ocupação |
| `departamento` | String(100) nullable | Departamento do usuário |
| `cargo` | String(100) nullable | Cargo do usuário |
| `classificacao` | String(50) nullable | Classificação do usuário |
| `cpf` | String(255) nullable | CPF (criptografado desde a migration 020) |
| `rg` | String(255) nullable | RG (criptografado desde a migration 020) |
| `salario` | String(255) nullable | Salário (criptografado desde a migration 020) |
| `endereco` | String(255) nullable | Endereço (criptografado desde a migration 020) |
| `numero` | String(20) nullable | Número do endereço |
| `bairro` | String(100) nullable | Bairro |
| `cidade` | String(100) nullable | Cidade |
| `uf` | String(2) nullable | Unidade federativa |
| `cep` | String(20) nullable | CEP |
| `telefone` | String(255) nullable | Telefone (criptografado desde a migration 020) |
| `celular` | String(255) nullable | Celular (criptografado desde a migration 020) |
| `role` | String(20) | `admin`, `operador` ou `leitura` |
| `ativo` | Boolean | Se pode fazer login |
| `aprovador` | String(50) nullable | Identificador do aprovador |
| `empresa_id` | Integer FK → `org.empresas` (nullable) | Empresa do usuário |
| `criado_em` | DateTime(tz) | Data de criação |
| `atualizado_em` | DateTime(tz) | Última atualização |

Índices: `ix_usuarios_username`, `ix_usuarios_role`, `ix_usuarios_ativo`, `ix_usuarios_empresa_id`. Únicos em `username` e `email`.

### Schema `iam` — UsuarioModulo (tabela associativa)

Gerencia permissão de módulos por usuário (M2M entre Usuario ↔ Modulo).

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `usuario_id` | Integer PK, FK → `iam.usuarios` | Usuário |
| `modulo_id` | Integer PK, FK → `portal.portal_modulos` | Módulo permitido |
| `concedido_em` | DateTime(tz) | Data da concessão |
| `concedido_por_id` | Integer FK → `iam.usuarios` (nullable) | Quem concedeu |

### Tabela `public` — produtos

A tabela `produtos` foi criada pela migration `001_initial_schema` no schema `public`, **sem model/ORM**. Ela não pertence a nenhum `DeclarativeBase` e é consultada via `api-sqlserver` (`protheus_router`), que não valida JWT (endpoints públicos).

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
| `ordem` | Integer (default 0) | Posição dentro da aba |
| `ativo` | Boolean | Se aparece no menu |

Índices: `ix_portal_modulos_aba_id` (composto com `ordem` via `ix_portal_modulos_aba_id_ordem` desde a migration 012).

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

Tema visual (skin) personalizado por empresa. Suporta dois layouts: `sidebar` e `topbar`.

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
| `company_id` | Integer (sem FK) | Empresa |
| `action` | String | Tipo de ação (`created`, `updated`, `activated`, `deleted`) |
| `performed_by` | Integer (sem FK, nullable) | Usuário que realizou a ação |
| `theme_snapshot` | JSON | Estado completo do tema após a ação |
| `changes` | JSON (nullable) | Diff das alterações (apenas em `updated`) |
| `criado_em` | DateTime(tz) | Data da alteração |

> Apenas `theme_id` possui Foreign Key. `company_id` e `performed_by` são colunas `Integer` comuns, sem FK — a integridade referencial é responsabilidade da aplicação.

### Schema `org` — AuditLog

Auditoria automática de alterações no banco. A cada INSERT/UPDATE/DELETE via ORM, o listener `before_flush` (`app/audit/listeners.py`) grava uma linha na **mesma transação**, com o contexto do request (usuário + IP) propagado via `ContextVar`.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `user_id` | Integer FK → `iam.usuarios.id` (ondelete CASCADE, nullable) | Usuário que executou a ação |
| `entidade` | String(100) | Nome da classe/entidade alterada |
| `entidade_id` | Integer (nullable) | ID da linha alterada |
| `acao` | String(20) | `INSERT`, `UPDATE` ou `DELETE` |
| `campos_alterados` | JSON | Nomes dos campos alterados (sem valores) |
| `ip` | String(45) (nullable) | IP do request (IPv4 ou IPv6) |
| `criado_em` | DateTime(tz) | Data da alteração |

Índices: `ix_audit_logs_user_id`, `ix_audit_logs_criado_em`, `ix_audit_logs_entidade_id` (composto `entidade` + `entidade_id`).

> Entidades **excluídas** da auto-auditoria: `audit_logs`, `sessoes` e `theme_history` (este último já tem histórico próprio).

### Schema `org` — Sessao

Rastreamento de tempo de uso (login/logout por usuário). Uma linha é criada a cada login em `POST /v1/auth/token`; o logout (`POST /v1/auth/logout` ou inatividade) fecha a sessão aberta mais recente.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador |
| `user_id` | Integer FK → `iam.usuarios.id` (ondelete CASCADE) | Usuário da sessão |
| `login_at` | DateTime(tz) | Entrada |
| `logout_at` | DateTime(tz) (nullable) | Saída (null = sessão aberta) |
| `duracao_segundos` | Integer (nullable) | Preenchido no logout |
| `ip` | String(45) (nullable) | IP do login |
| `logout_motivo` | String(20) (nullable) | `logout` (manual), `inativo` (timeout) ou `expirado` (reservado) |

Índices: `ix_sessoes_user_id`, `ix_sessoes_login_at`.

### Schema `org` — Projeto, Recurso, Tarefa, RegistroTarefa

Tabelas criadas pela migration `007_add_org_schema_tables` para gestão de projetos. **Não possuem model class** — existem apenas no banco via SQL puro na migração.

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
make migrate

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
| `001_initial_schema` | Criação inicial: `usuarios`, `produtos` (schema `public`) |
| `002_add_usuario_modulos` | Adiciona `portal_abas`, `portal_modulos`, `usuario_modulos`; cria `parent_id` + FK `fk_aba_parent` em `portal_abas` |
| `003_add_empresa_and_theme` | Adiciona `empresas`, `company_themes`, `empresa_id` em `usuarios` |
| `004_add_theme_history` | Adiciona `theme_history` + índices `ix_theme_history_*` |
| `005_add_aba_parent_id` | No-op (`pass`) — `parent_id` e a FK `fk_aba_parent` já foram criados na migration 002 |
| `006_add_temp_password_fields` | Adiciona `temp_password_hash`, `expires_at` em `usuarios` |
| `007_add_org_schema_tables` | Cria schema `org` com `projetos`, `recursos`, `tarefas`, `registros_tarefas` + índices `ix_org_projetos_nome`, `ix_org_tarefas_titulo`/`projeto_id`/`responsavel_id`, `ix_org_registros_tarefas_tarefa_id`/`autor_id` |
| `008_add_performance_indexes` | Índices B-tree: `ix_company_themes_company_active`, `ix_usuarios_role`, `ix_usuarios_ativo`, `ix_usuarios_empresa_id`, `ix_portal_modulos_aba_id` |
| `009_add_layout_mode` | Adiciona `layout_mode` em `company_themes` |
| `010_add_theme_preference` | Adiciona `theme_preference` em `usuarios` |
| `011_add_layout_preference` | Adiciona `layout_preference` em `usuarios` |
| `012_add_modulo_ordem` | Adiciona `ordem` em `portal_modulos` + índice composto `ix_portal_modulos_aba_id_ordem` |
| `013_add_profile_fields` | Adiciona campos de perfil em `usuarios` |
| `014_add_numero_field` | Adiciona `numero` em `usuarios` |
| `015_add_classificacao_field` | Adiciona `classificacao` em `usuarios` |
| `016_add_telefone_celular_fields` | Adiciona `telefone`, `celular` em `usuarios` |
| `017_add_rg_salario_fields` | Adiciona `rg`, `salario` em `usuarios` |
| `018_add_layout_mobile_preference` | Adiciona `layout_mobile_preference` em `usuarios` |
| `019_add_bairro_cidade_uf_fields` | Adiciona `bairro`, `cidade`, `uf` em `usuarios` |
| `020_encrypt_sensitive_user_fields` | Criptografa `cpf`, `rg`, `salario`, `endereco`, `telefone`, `celular` e altera para `String(255)` |
| `021_add_aprovador_to_usuarios` | Adiciona `aprovador` em `usuarios` |
| `022_add_audit_tables` | Cria `org.audit_logs` e `org.sessoes` para auditoria de alterações e tempo de uso |

---

## Dados Iniciais (seed)

```powershell
make seed
```

Cria (idempotente):

- Schemas `iam`, `portal`, `org` e `catalogo` (vazio, sem tabelas) + `create_all`
- Empresa `GrindX` com dominio `grindx.local`
- Usuário `admin` / `admin123` (e-mail `admin@erp.com.br`) com role `admin` — vinculado à GrindX
- Skin "Padrão GrindX" com `layout_mode` `topbar`
- Abas: `Principal` (ordem 0), `R. HUMANOS` (ordem 50) e `Gestão` (ordem 100)
- Módulos: `Dashboard` (home), `Usuários` (users), `Administradores` (admins, role admin), `Módulos & Abas` (structure), `Skins` (admin-skins), `Importar Módulos` (importer), `Auditoria` (auditoria, role admin), `Configurar Agente` (configurar-agente, role admin)

---

## Schema `agente` (Agente de IA)

O Agente de IA (`apps/agente-ia`) usa um schema próprio `agente`, criado automaticamente na subida do serviço (`init_db`) — **não** faz parte das migrações Alembic do `api-postgres`.

Requer a extensão **pgvector** (`CREATE EXTENSION IF NOT EXISTS vector`) no PostgreSQL.

### Tabela `agente.chunks`

Armazena os trechos (chunks) dos manuais com seus embeddings.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | serial PK | Identificador |
| `module` | varchar(120) | Slug do módulo (ex.: `users`) |
| `title` | text | Título da seção |
| `content` | text | Conteúdo do trecho |
| `filename` | text | Nome do arquivo do manual |
| `updated_at` | timestamptz | Última atualização |
| `embedding` | vector(384) | Vetor do modelo `paraphrase-multilingual-MiniLM-L12-v2` |

---

## Backup

```powershell
# Dump completo
pg_dump -U postgres grindx > grindx_backup.sql

# Restaurar
psql -U postgres grindx < grindx_backup.sql
```

Em produção, agendar backup diário via cron ou ferramenta do provedor de banco.
