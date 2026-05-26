# Spec: Migração para Multi-Schema no `api-postgres`

**Data:** 2026-05-25  
**Status:** Proposta  
**Escopo:** `packages/api-postgres` — modelos, Alembic, testes

---

## 1. Contexto e motivação

Atualmente todas as tabelas do `api-postgres` residem no schema `public` do PostgreSQL, sem separação por domínio. Com a adição contínua de módulos ao sistema GrindX, a ausência de separação por schema cria os seguintes problemas:

- Nomes de tabela achatados no `public` que crescem sem organização (`usuarios`, `portal_abas`, `portal_modulos`, `company_themes`, etc.)
- Impossibilidade de conceder permissões granulares por domínio a roles de banco de dados
- Dificuldade futura de isolar um módulo em serviço separado
- Ausência de fronteira explícita entre domínios no código e no banco

---

## 2. Mapeamento de domínios e schemas

As tabelas existentes são agrupadas em quatro schemas de negócio:

| Schema     | Tabelas                                               | Responsabilidade                          |
|------------|-------------------------------------------------------|-------------------------------------------|
| `iam`      | `usuarios`, `usuario_modulos`                        | Identidade, autenticação e permissões     |
| `portal`   | `portal_abas`, `portal_modulos`                      | Estrutura de navegação do portal          |
| `catalogo` | `produtos`                                            | Catálogo de produtos                      |
| `org`      | `empresas`, `company_themes`, `theme_history`        | Empresa, temas visuais e auditoria        |

> **Regra para novos módulos:** cada módulo futuro declara seu schema no `base.py` do próprio módulo. Módulos que só leiam dados de outro domínio usam FKs cross-schema; nunca importam a `Base` alheia diretamente.

---

## 3. Mudanças na camada de modelos

### 3.1 — Remover `Base` de `database.py`

A classe `Base(DeclarativeBase)` atual em `app/database.py` é substituída por quatro bases com metadata dedicada, uma por schema. O `database.py` passa a exportar apenas `engine`, `SessionLocal` e `get_db`.

```python
# app/database.py  (após a mudança)
# Base NÃO é mais exportada daqui
engine = create_engine(...)
SessionLocal = sessionmaker(...)

def get_db(): ...
```

### 3.2 — Bases por schema

Cada módulo recebe um `base.py` próprio:

```python
# app/modules/iam/base.py
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

class IamBase(DeclarativeBase):
    metadata = MetaData(schema="iam")
```

```python
# app/modules/portal/base.py
class PortalBase(DeclarativeBase):
    metadata = MetaData(schema="portal")
```

```python
# app/modules/catalogo/base.py
class CatalogoBase(DeclarativeBase):
    metadata = MetaData(schema="catalogo")
```

```python
# app/modules/org/base.py
class OrgBase(DeclarativeBase):
    metadata = MetaData(schema="org")
```

### 3.3 — Atualização dos modelos

Cada model herda da `Base` do seu módulo e todas as `ForeignKey` cross-schema passam a ser qualificadas com `schema.tabela`:

| Model            | Base atual  | Nova base      | FKs afetadas                                                |
|------------------|-------------|----------------|-------------------------------------------------------------|
| `Usuario`        | `Base`      | `IamBase`      | `org.empresas.id`                                           |
| `UsuarioModulo`  | `Base`      | `IamBase`      | `iam.usuarios.id`, `portal.portal_modulos.id`               |
| `Aba`            | `Base`      | `PortalBase`   | `portal.portal_abas.id` (self-ref)                          |
| `Modulo`         | `Base`      | `PortalBase`   | `portal.portal_abas.id`                                     |
| `Produto`        | `Base`      | `CatalogoBase` | — (nenhuma FK externa)                                      |
| `Empresa`        | `Base`      | `OrgBase`      | — (nenhuma FK externa)                                      |
| `CompanyTheme`   | `Base`      | `OrgBase`      | `org.empresas.id`                                           |
| `ThemeHistory`   | `Base`      | `OrgBase`      | `org.company_themes.id`                                     |

#### Exemplo — `Usuario` após a mudança:

```python
from app.modules.iam.base import IamBase

class Usuario(IamBase):
    __tablename__ = "usuarios"
    # sem __table_args__ — o schema vem do MetaData da IamBase

    empresa_id: Mapped[int | None] = mapped_column(
        ForeignKey("org.empresas.id", ondelete="SET NULL"), nullable=True
    )
```

#### Exemplo — `UsuarioModulo` com FKs cross-schema:

```python
class UsuarioModulo(IamBase):
    __tablename__ = "usuario_modulos"

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("iam.usuarios.id", ondelete="CASCADE"), primary_key=True
    )
    modulo_id: Mapped[int] = mapped_column(
        ForeignKey("portal.portal_modulos.id", ondelete="CASCADE"), primary_key=True
    )
    concedido_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("iam.usuarios.id", ondelete="SET NULL"), nullable=True
    )
```

### 3.4 — Relationships cross-schema

Relationships que atravessam schemas continuam funcionando normalmente no SQLAlchemy — o ORM não distingue schemas em relacionamentos. O único ponto de atenção é o argumento `secondary` em many-to-many, que deve usar a string qualificada:

```python
# Em Usuario (IamBase)
modulos_permitidos: Mapped[list["Modulo"]] = relationship(
    "Modulo",
    secondary="iam.usuario_modulos",   # <-- qualificado
    ...
)

# Em Modulo (PortalBase)
usuarios_permitidos = relationship(
    "Usuario",
    secondary="iam.usuario_modulos",   # <-- qualificado
    ...
)
```

---

## 4. Mudanças no Alembic

### 4.1 — `alembic/env.py`

Três mudanças obrigatórias:

**a) Importar todas as bases e construir um `target_metadata` combinado:**

```python
from app.modules.iam.base import IamBase
from app.modules.portal.base import PortalBase
from app.modules.catalogo.base import CatalogoBase
from app.modules.org.base import OrgBase

# Importar todos os models para o autogenerate detectar
from app.modules.iam.models.usuario import Usuario, UsuarioModulo       # noqa
from app.modules.portal.models.portal import Aba, Modulo               # noqa
from app.modules.catalogo.models.produto import Produto                 # noqa
from app.modules.org.models.empresa import Empresa                      # noqa
from app.modules.org.models.theme import CompanyTheme                   # noqa
from app.modules.org.models.theme_history import ThemeHistory           # noqa

# MetaData combinada para o autogenerate
from sqlalchemy import MetaData
combined_metadata = MetaData()
for base in [IamBase, PortalBase, CatalogoBase, OrgBase]:
    for table in base.metadata.tables.values():
        table.tometadata(combined_metadata)

target_metadata = combined_metadata
```

**b) Adicionar `include_schemas=True` e `version_table_schema` em ambos os modos:**

```python
def run_migrations_online() -> None:
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,           # detectar tabelas em todos os schemas
            version_table_schema="public",  # alembic_version permanece no public
        )
        with context.begin_transaction():
            context.run_migrations()
```

**c) Mesmo ajuste para `run_migrations_offline`:**

```python
def run_migrations_offline() -> None:
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_schemas=True,
        version_table_schema="public",
        dialect_opts={"paramstyle": "named"},
    )
```

### 4.2 — Migration `006_migrate_to_schemas.py`

Esta é a migration mais crítica. Ela **não cria tabelas novas** — move as existentes de `public` para seus schemas de destino via `ALTER TABLE ... SET SCHEMA`. O Alembic não tem helper nativo para isso; usamos `op.execute` com SQL direto.

**Estratégia:**

1. Criar os quatro schemas
2. Remover constraints FK cross-domínio (que referenciam `public.*`)
3. Mover tabelas na ordem correta (respeitando dependências internas)
4. Recriar as constraints FK com nomes e referências atualizados

**Ordem de movimentação (respeitando dependências):**

```
Passo 1 — schemas sem dependências externas:
  public.empresas      → org.empresas
  public.produtos      → catalogo.produtos

Passo 2 — depende de org.empresas:
  public.usuarios      → iam.usuarios  (FK empresa_id → org.empresas.id)

Passo 3 — depende de iam.usuarios:
  public.portal_abas   → portal.portal_abas
  public.portal_modulos → portal.portal_modulos
  public.company_themes → org.company_themes
  public.theme_history  → org.theme_history

Passo 4 — depende de iam.usuarios e portal.portal_modulos:
  public.usuario_modulos → iam.usuario_modulos
```

**Constraints FK a remover antes e recriar depois:**

| Constraint                    | Tabela origem         | Referência original           | Nova referência                   |
|-------------------------------|-----------------------|-------------------------------|-----------------------------------|
| `fk_usuarios_empresa_id`      | `usuarios`            | `empresas.id`                 | `org.empresas.id`                 |
| FK em `usuario_modulos`       | `usuario_modulos`     | `usuarios.id`                 | `iam.usuarios.id`                 |
| FK em `usuario_modulos`       | `usuario_modulos`     | `portal_modulos.id`           | `portal.portal_modulos.id`        |
| FK em `usuario_modulos`       | `usuario_modulos`     | `usuarios.id` (concedido_por) | `iam.usuarios.id`                 |
| FK em `company_themes`        | `company_themes`      | `empresas.id`                 | `org.empresas.id`                 |
| FK em `theme_history`         | `theme_history`       | `company_themes.id`           | `org.company_themes.id`           |
| `fk_aba_parent`               | `portal_abas`         | `portal_abas.id`              | `portal.portal_abas.id`           |
| FK em `portal_modulos`        | `portal_modulos`      | `portal_abas.id`              | `portal.portal_abas.id`           |

**Esqueleto da migration:**

```python
def upgrade() -> None:
    # 1. Criar schemas
    for schema in ("iam", "portal", "catalogo", "org"):
        op.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    # 2. Remover FKs cross-schema antes de mover tabelas
    op.drop_constraint("fk_usuarios_empresa_id", "usuarios", type_="foreignkey")
    # ... (demais constraints listadas acima)

    # 3. Mover tabelas (na ordem de dependências)
    op.execute("ALTER TABLE public.empresas SET SCHEMA org")
    op.execute("ALTER TABLE public.produtos SET SCHEMA catalogo")
    op.execute("ALTER TABLE public.usuarios SET SCHEMA iam")
    op.execute("ALTER TABLE public.portal_abas SET SCHEMA portal")
    op.execute("ALTER TABLE public.portal_modulos SET SCHEMA portal")
    op.execute("ALTER TABLE public.company_themes SET SCHEMA org")
    op.execute("ALTER TABLE public.theme_history SET SCHEMA org")
    op.execute("ALTER TABLE public.usuario_modulos SET SCHEMA iam")

    # 4. Recriar FKs com referências qualificadas
    op.create_foreign_key(
        "fk_usuarios_empresa_id", "usuarios",
        "empresas", ["empresa_id"], ["id"],
        source_schema="iam", referent_schema="org",
        ondelete="SET NULL",
    )
    # ... (demais constraints)

def downgrade() -> None:
    # Inverso: remover FKs → mover de volta para public → recriar FKs originais → DROP schemas
    ...
```

---

## 5. Mudanças nos testes

### 5.1 — Problema com SQLite

O SQLite não suporta schemas com `MetaData(schema="...")` da mesma forma que o PostgreSQL. Quando o SQLAlchemy tenta criar `iam.usuarios` no SQLite, ele trata `iam` como um database ATTACH separado — o que não existe no teste.

**Solução: `schema_translate_map`**

O SQLAlchemy suporta a opção `execution_options(schema_translate_map=...)` que faz o engine substituir todos os schemas por `None` (schema padrão do SQLite) em tempo de execução. O schema real no PostgreSQL não é afetado.

### 5.2 — `conftest.py` após a mudança

```python
# packages/api-postgres/tests/conftest.py

# Importar as quatro bases e o combined_metadata (mesmo que o env.py do Alembic)
from app.modules.iam.base import IamBase
from app.modules.portal.base import PortalBase
from app.modules.catalogo.base import CatalogoBase
from app.modules.org.base import OrgBase
from app.database import get_db
from app.main import app

# Mapa que "zera" todos os schemas para o SQLite
_SCHEMA_TRANSLATE = {"iam": None, "portal": None, "catalogo": None, "org": None}

# Metadata combinada (idêntica ao env.py do Alembic)
from sqlalchemy import MetaData
_all_metadata = MetaData()
for _base in [IamBase, PortalBase, CatalogoBase, OrgBase]:
    for _table in _base.metadata.tables.values():
        _table.tometadata(_all_metadata)


@pytest.fixture(scope="function")
def db_session() -> Session:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Cria todas as tabelas no SQLite sem prefixo de schema
    with engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE).connect() as conn:
        _all_metadata.create_all(conn)

    TestingSession = sessionmaker(
        bind=engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE),
        autocommit=False,
        autoflush=False,
    )
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        with engine.execution_options(schema_translate_map=_SCHEMA_TRANSLATE).connect() as conn:
            _all_metadata.drop_all(conn)
```

> O `schema_translate_map` é propagado para a `SessionLocal` via bind no engine com `execution_options` — todos os queries da sessão usam o mapa automaticamente.

---

## 6. Nova estrutura de diretórios

A estrutura de `app/` muda de flat para modular:

```
packages/api-postgres/app/
├── database.py               # engine, SessionLocal, get_db (sem Base)
├── main.py                   # sem alteração na lógica
├── core/                     # sem alteração
├── auth/                     # sem alteração
├── middleware/               # sem alteração
├── modules/
│   ├── iam/
│   │   ├── base.py           # IamBase  ←  NOVO
│   │   └── models/
│   │       └── usuario.py    # herda IamBase
│   ├── portal/
│   │   ├── base.py           # PortalBase  ←  NOVO
│   │   └── models/
│   │       └── portal.py     # herda PortalBase
│   ├── catalogo/
│   │   ├── base.py           # CatalogoBase  ←  NOVO
│   │   └── models/
│   │       └── produto.py    # herda CatalogoBase
│   └── org/
│       ├── base.py           # OrgBase  ←  NOVO
│       └── models/
│           ├── empresa.py    # herda OrgBase
│           ├── theme.py      # herda OrgBase
│           └── theme_history.py  # herda OrgBase
├── models/                   # mantido para compatibilidade — re-exporta tudo
│   └── __init__.py           # from app.modules.*.models.* import ...
├── repositories/             # sem alteração (importam models, não Base)
├── routers/                  # sem alteração
├── schemas/                  # sem alteração
└── services/                 # sem alteração
```

> Manter `app/models/__init__.py` re-exportando tudo garante que imports existentes (nos routers, repositories, etc.) **não precisem ser alterados** neste momento.

---

## 7. Comportamento de `alembic autogenerate`

Após a mudança, o `alembic revision --autogenerate` passará a:

- Detectar e gerar corretamente tabelas novas em qualquer dos quatro schemas
- Nunca mais sugerir criar tabelas no `public` (a menos que uma Base seja criada sem schema)
- Nomear migrations com o schema explícito nas operações (`schema="iam"` em `op.create_table`)

---

## 8. Permissões de banco (opcional, pós-implantação)

Com os schemas separados, é possível conceder permissões granulares por role de banco — sem impacto no código da aplicação:

```sql
-- Exemplo: role de leitura apenas no catálogo
GRANT USAGE ON SCHEMA catalogo TO grindx_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA catalogo TO grindx_readonly;

-- Role de serviço com acesso apenas ao IAM
GRANT USAGE ON SCHEMA iam TO grindx_auth_service;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA iam TO grindx_auth_service;
```

---

## 9. Restrições e decisões de design

| Decisão | Justificativa |
|---|---|
| `MetaData(schema=...)` na Base, não em `__table_args__` | Evita repetição em cada model do módulo; garante consistência |
| FKs cross-schema com string qualificada (`"iam.usuarios.id"`) | Única forma do SQLAlchemy gerar DDL correto cross-schema |
| `schema_translate_map` nos testes | Mantém SQLite como backend de teste sem alterar os models |
| `version_table_schema="public"` | A tabela `alembic_version` fica no `public`, fácil de localizar |
| `app/models/__init__.py` mantido como re-export | Zero breaking change nos imports de routers/repositories existentes |
| `app/models/` movido para `app/modules/*/models/` gradualmente | Permite migração incremental sem travar o desenvolvimento |
