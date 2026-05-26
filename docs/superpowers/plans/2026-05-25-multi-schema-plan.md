# Plano de Implementação: Multi-Schema no `api-postgres`

**Referência:** `spec-multi-schema.md`  
**Data:** 2026-05-25  
**Risco:** Médio — envolve movimentação de tabelas com dados em produção

---

## Visão geral das etapas

```
Fase 1 — Código Python (sem toque no banco)
  Step 1.1  Criar bases por schema (IamBase, PortalBase, CatalogoBase, OrgBase)
  Step 1.2  Mover models para app/modules/*/models/ e atualizar herança + FKs
  Step 1.3  Atualizar app/models/__init__.py como re-export
  Step 1.4  Limpar database.py (remover Base)
  Step 1.5  Atualizar alembic/env.py
  Step 1.6  Atualizar conftest.py

Fase 2 — Validação (testes passam, app sobe)
  Step 2.1  Executar suite completa de testes
  Step 2.2  Verificar startup da app e autogenerate limpo

Fase 3 — Migration de banco
  Step 3.1  Escrever migration 006
  Step 3.2  Testar migration em banco de dev (upgrade + downgrade)
  Step 3.3  Aplicar em produção
```

---

## Fase 1 — Código Python

### Step 1.1 — Criar as bases por schema

Criar os quatro arquivos de base. Nenhum model existente é alterado ainda.

**Arquivos a criar:**

```
packages/api-postgres/app/modules/iam/base.py
packages/api-postgres/app/modules/iam/__init__.py
packages/api-postgres/app/modules/iam/models/__init__.py

packages/api-postgres/app/modules/portal/base.py
packages/api-postgres/app/modules/portal/__init__.py
packages/api-postgres/app/modules/portal/models/__init__.py

packages/api-postgres/app/modules/catalogo/base.py
packages/api-postgres/app/modules/catalogo/__init__.py
packages/api-postgres/app/modules/catalogo/models/__init__.py

packages/api-postgres/app/modules/org/base.py
packages/api-postgres/app/modules/org/__init__.py
packages/api-postgres/app/modules/org/models/__init__.py
```

**Conteúdo padrão de cada `base.py`** (exemplo para `iam`):

```python
# app/modules/iam/base.py
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class IamBase(DeclarativeBase):
    """Base para todos os modelos do schema 'iam' (identidade e acesso)."""
    metadata = MetaData(schema="iam")
```

**Critério de conclusão:** os quatro `base.py` criados, sem erro de importação.

---

### Step 1.2 — Mover models e atualizar herança + FKs

Para cada model, dois ajustes:
1. Mudar o `from app.database import Base` para o novo `from app.modules.<modulo>.base import <ModuloBase>`
2. Atualizar FKs cross-schema

Pode ser feito model a model — a ordem abaixo segue o grafo de dependências (independentes primeiro):

#### 1.2.a — `Produto` → `CatalogoBase`

Arquivo: copiar `app/models/produto.py` → `app/modules/catalogo/models/produto.py`

```python
# Mudança:
# DE:  from app.database import Base
# PARA:
from app.modules.catalogo.base import CatalogoBase

class Produto(CatalogoBase):
    __tablename__ = "produtos"
    # nenhuma FK externa — sem outras alterações
```

#### 1.2.b — `Empresa` → `OrgBase`

Arquivo: `app/modules/org/models/empresa.py`

```python
from app.modules.org.base import OrgBase

class Empresa(OrgBase):
    __tablename__ = "empresas"
    # nenhuma FK externa — sem outras alterações
```

#### 1.2.c — `CompanyTheme` e `ThemeHistory` → `OrgBase`

Arquivo: `app/modules/org/models/theme.py` e `app/modules/org/models/theme_history.py`

```python
# theme.py
from app.modules.org.base import OrgBase

class CompanyTheme(OrgBase):
    __tablename__ = "company_themes"

    company_id: Mapped[int] = mapped_column(
        ForeignKey("org.empresas.id", ondelete="CASCADE"),  # <-- qualificado
        ...
    )
```

```python
# theme_history.py
class ThemeHistory(OrgBase):
    __tablename__ = "theme_history"

    theme_id: Mapped[int] = mapped_column(
        ForeignKey("org.company_themes.id", ondelete="CASCADE"),  # <-- qualificado
        ...
    )
```

#### 1.2.d — `Usuario` e `UsuarioModulo` → `IamBase`

Arquivo: `app/modules/iam/models/usuario.py`

```python
from app.modules.iam.base import IamBase

class Usuario(IamBase):
    __tablename__ = "usuarios"

    empresa_id: Mapped[int | None] = mapped_column(
        ForeignKey("org.empresas.id", ondelete="SET NULL"),  # <-- qualificado
        ...
    )

    modulos_permitidos: Mapped[list["Modulo"]] = relationship(
        "Modulo",
        secondary="iam.usuario_modulos",    # <-- qualificado
        ...
    )


class UsuarioModulo(IamBase):
    __tablename__ = "usuario_modulos"

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("iam.usuarios.id", ondelete="CASCADE"),       # <-- qualificado
        primary_key=True,
    )
    modulo_id: Mapped[int] = mapped_column(
        ForeignKey("portal.portal_modulos.id", ondelete="CASCADE"),  # <-- qualificado
        primary_key=True,
    )
    concedido_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("iam.usuarios.id", ondelete="SET NULL"),      # <-- qualificado
        nullable=True,
    )
```

#### 1.2.e — `Aba` e `Modulo` → `PortalBase`

Arquivo: `app/modules/portal/models/portal.py`

```python
from app.modules.portal.base import PortalBase

class Aba(PortalBase):
    __tablename__ = "portal_abas"

    parent_id = Column(
        Integer, ForeignKey("portal.portal_abas.id"), nullable=True  # <-- qualificado
    )


class Modulo(PortalBase):
    __tablename__ = "portal_modulos"

    aba_id = Column(
        Integer, ForeignKey("portal.portal_abas.id"), nullable=False  # <-- qualificado
    )

    usuarios_permitidos = relationship(
        "Usuario",
        secondary="iam.usuario_modulos",    # <-- qualificado
        ...
    )
```

**Critério de conclusão:** todos os models movidos, cada um importando sua Base correta, todas as FKs cross-schema qualificadas.

---

### Step 1.3 — Atualizar `app/models/__init__.py`

Muda apenas os imports — o que é exportado permanece igual, então nenhum outro arquivo precisa mudar:

```python
# app/models/__init__.py
"""Re-exporta todos os modelos para manter compatibilidade com imports existentes."""

from app.modules.catalogo.models.produto import Produto             # noqa: F401
from app.modules.iam.models.usuario import Usuario, UsuarioModulo   # noqa: F401
from app.modules.org.models.empresa import Empresa                  # noqa: F401
from app.modules.org.models.theme import CompanyTheme               # noqa: F401
from app.modules.org.models.theme_history import ThemeHistory       # noqa: F401
from app.modules.portal.models.portal import Aba, Modulo            # noqa: F401
```

**Critério de conclusão:** `from app.models import Usuario` continua funcionando sem qualquer alteração nos routers ou repositories.

---

### Step 1.4 — Limpar `database.py`

Remover a classe `Base` de `database.py`. Se algum código ainda importar `Base` de lá, o erro de import vai revelar o ponto durante os testes.

```python
# database.py — REMOVER este bloco:
# class Base(DeclarativeBase):
#     """Classe base para todos os modelos SQLAlchemy do PostgreSQL."""
#     pass
```

**Critério de conclusão:** `database.py` não exporta mais `Base`. O pylint/mypy reporta erro em qualquer `from app.database import Base` remanescente.

---

### Step 1.5 — Atualizar `alembic/env.py`

Três mudanças (detalhadas na spec):

1. Substituir `from app.database import Base` pelo import das quatro bases + combined_metadata
2. Adicionar `include_schemas=True` em `run_migrations_online`
3. Adicionar `include_schemas=True` e `version_table_schema="public"` em `run_migrations_offline`

```python
# env.py — bloco de imports e metadata (substituir o bloco atual)

from app.modules.iam.base import IamBase
from app.modules.portal.base import PortalBase
from app.modules.catalogo.base import CatalogoBase
from app.modules.org.base import OrgBase

# Importar models para o autogenerate detectar
from app.modules.iam.models.usuario import Usuario, UsuarioModulo       # noqa
from app.modules.portal.models.portal import Aba, Modulo               # noqa
from app.modules.catalogo.models.produto import Produto                 # noqa
from app.modules.org.models.empresa import Empresa                      # noqa
from app.modules.org.models.theme import CompanyTheme                   # noqa
from app.modules.org.models.theme_history import ThemeHistory           # noqa

from sqlalchemy import MetaData

combined_metadata = MetaData()
for _base in [IamBase, PortalBase, CatalogoBase, OrgBase]:
    for _table in _base.metadata.tables.values():
        _table.tometadata(combined_metadata)

target_metadata = combined_metadata
```

**Critério de conclusão:** `alembic check` não lança exceção de import; o comando reporta "Target database is up to date" (ainda não há migration 006).

---

### Step 1.6 — Atualizar `tests/conftest.py`

Substituir o `from app.database import Base` e o `Base.metadata.create_all` pelo padrão com `schema_translate_map` detalhado na spec (seção 5.2).

Constante de mapeamento a definir no topo do arquivo:

```python
_SCHEMA_TRANSLATE = {"iam": None, "portal": None, "catalogo": None, "org": None}
```

> Quando um novo schema for criado no projeto, basta adicionar a entrada aqui.

**Critério de conclusão:** fixture `db_session` cria todas as tabelas no SQLite sem erro de schema.

---

## Fase 2 — Validação

### Step 2.1 — Executar suite completa de testes

```bash
cd packages/api-postgres
pytest tests/ -v
```

**Critério de conclusão:** todos os testes que passavam antes continuam passando. Zero regressões.

Possíveis falhas esperadas e solução:

| Falha | Causa | Solução |
|---|---|---|
| `OperationalError: no such table: iam.usuarios` | `schema_translate_map` não propagado para a sessão | Verificar que o `sessionmaker` recebe o engine com `execution_options` |
| `NoForeignKeysError` em relationship | String de FK cross-schema errada | Conferir se a string bate exatamente com `"schema.tabela.coluna"` |
| `Import error: cannot import name 'Base' from 'app.database'` | Import antigo remanescente | Buscar `from app.database import Base` em todos os arquivos e corrigir |

### Step 2.2 — Verificar startup e autogenerate

```bash
# A app deve subir sem erros
uvicorn app.main:app --reload

# O autogenerate não deve sugerir nenhuma mudança além da 006 ainda pendente
alembic revision --autogenerate -m "check_after_refactor" --dry-run
```

**Critério de conclusão:** app sobe sem erro; autogenerate em banco que já rodou as migrations 001-005 produz apenas a migration de movimentação de schemas (ou nada, dependendo de quando a 006 for escrita).

---

## Fase 3 — Migration de banco

### Step 3.1 — Escrever a migration `006_migrate_to_schemas.py`

A migration deve ser **escrita manualmente** (não gerada por autogenerate) por ser uma operação DDL especial (`SET SCHEMA`).

**Estrutura do arquivo:**

```python
"""Migrar tabelas do schema public para schemas de domínio.

Revision ID: 006_migrate_to_schemas
Revises: 005_add_aba_parent_id
Create Date: 2026-05-25

Schemas criados: iam, portal, catalogo, org
"""

revision = "006_migrate_to_schemas"
down_revision = "005_add_aba_parent_id"
branch_labels = None
depends_on = None

SCHEMAS = ("iam", "portal", "catalogo", "org")

# Mapa: tabela → schema de destino
TABLE_SCHEMA_MAP = {
    "empresas": "org",
    "produtos": "catalogo",
    "usuarios": "iam",
    "portal_abas": "portal",
    "portal_modulos": "portal",
    "company_themes": "org",
    "theme_history": "org",
    "usuario_modulos": "iam",
}

def upgrade() -> None:
    # 1. Criar schemas
    for schema in SCHEMAS:
        op.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    # 2. Remover constraints FK cross-domínio
    #    (constraints internas dentro do mesmo schema não precisam ser removidas
    #     antes do SET SCHEMA, pois o PostgreSQL atualiza referências no mesmo schema)
    op.drop_constraint("fk_usuarios_empresa_id", "usuarios", type_="foreignkey")
    op.drop_constraint("fk_usuario_modulos_usuario",
                        "usuario_modulos", type_="foreignkey")
    op.drop_constraint("fk_usuario_modulos_modulo",
                        "usuario_modulos", type_="foreignkey")
    op.drop_constraint("fk_usuario_modulos_concedido_por",
                        "usuario_modulos", type_="foreignkey")
    op.drop_constraint("fk_company_themes_company",
                        "company_themes", type_="foreignkey")
    op.drop_constraint("fk_theme_history_theme",
                        "theme_history", type_="foreignkey")

    # 3. Mover tabelas (ordem importa!)
    for table, schema in TABLE_SCHEMA_MAP.items():
        op.execute(f"ALTER TABLE public.{table} SET SCHEMA {schema}")

    # 4. Recriar FKs com referências qualificadas
    op.create_foreign_key(
        "fk_usuarios_empresa_id", "usuarios", "empresas",
        ["empresa_id"], ["id"],
        source_schema="iam", referent_schema="org",
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_usuario_modulos_usuario", "usuario_modulos", "usuarios",
        ["usuario_id"], ["id"],
        source_schema="iam", referent_schema="iam",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_usuario_modulos_modulo", "usuario_modulos", "portal_modulos",
        ["modulo_id"], ["id"],
        source_schema="iam", referent_schema="portal",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_usuario_modulos_concedido_por", "usuario_modulos", "usuarios",
        ["concedido_por_id"], ["id"],
        source_schema="iam", referent_schema="iam",
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_company_themes_company", "company_themes", "empresas",
        ["company_id"], ["id"],
        source_schema="org", referent_schema="org",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_theme_history_theme", "theme_history", "company_themes",
        ["theme_id"], ["id"],
        source_schema="org", referent_schema="org",
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # Inverso do upgrade: remove FKs novas → move de volta → recria FKs originais → drop schemas
    # (Implementar antes de colocar em produção)
    ...
```

> **Atenção:** os nomes das constraints originais (`fk_usuarios_empresa_id`, etc.) devem ser confirmados no banco de dev com `\d+ <tabela>` no psql antes de executar a migration — nomes gerados automaticamente pelo PostgreSQL podem diferir do que as migrations antigas definiram.

**Critério de conclusão:** migration escrita, revisada, com `downgrade` implementado.

---

### Step 3.2 — Testar migration em banco de dev

```bash
# Aplicar
alembic upgrade 006_migrate_to_schemas

# Verificar estrutura
psql -d grindx_dev -c "\dn"                          # listar schemas
psql -d grindx_dev -c "\dt iam.*"                    # tabelas do iam
psql -d grindx_dev -c "\dt portal.*"
psql -d grindx_dev -c "\dt catalogo.*"
psql -d grindx_dev -c "\dt org.*"

# Verificar FKs
psql -d grindx_dev -c "\d+ iam.usuarios"
psql -d grindx_dev -c "\d+ iam.usuario_modulos"

# Rodar autogenerate — deve retornar vazio (sem drift)
alembic revision --autogenerate -m "verify" --dry-run

# Testar downgrade completo
alembic downgrade base
alembic upgrade head
```

**Critério de conclusão:** upgrade e downgrade executam sem erro; autogenerate retorna sem pendências; dados preservados.

---

### Step 3.3 — Aplicar em produção

```bash
# 1. Backup antes de qualquer coisa
pg_dump grindx_prod > grindx_prod_pre_006_$(date +%Y%m%d_%H%M%S).dump

# 2. Verificar versão atual
alembic current

# 3. Aplicar
alembic upgrade 006_migrate_to_schemas

# 4. Confirmar
alembic current   # deve mostrar 006_migrate_to_schemas (head)
```

**Critério de conclusão:** produção na versão `006`, aplicação funcional, zero downtime (a migration é DDL rápida — sem varredura de dados).

---

## Checklist de rollback

Se algo falhar na Fase 3:

1. `alembic downgrade 005_add_aba_parent_id` — reverte a migration (se o `downgrade` estiver implementado)
2. Se o `downgrade` falhar: restaurar o backup `pg_dump` gerado antes
3. Reverter o deploy do código para a versão sem schemas (o código da Fase 1 é compatível com ambos os estados do banco enquanto `public.*` ainda existe)

---

## Estimativa de esforço

| Etapa | Esforço estimado |
|---|---|
| Step 1.1 — criar bases | 15 min |
| Step 1.2 — mover models e atualizar FKs | 45 min |
| Step 1.3 — atualizar `models/__init__.py` | 5 min |
| Step 1.4 — limpar `database.py` | 5 min |
| Step 1.5 — atualizar `env.py` | 20 min |
| Step 1.6 — atualizar `conftest.py` | 20 min |
| Step 2.1 — rodar testes e corrigir | 30–60 min |
| Step 2.2 — verificar startup e autogenerate | 15 min |
| Step 3.1 — escrever migration 006 | 45 min |
| Step 3.2 — testar em dev (upgrade + downgrade) | 30 min |
| Step 3.3 — aplicar em produção | 10 min |
| **Total** | **~4–5 horas** |

---

## Convenção para novos módulos (pós-implantação)

Ao adicionar um novo módulo ao GrindX:

1. Criar `app/modules/<nome>/base.py` com `MetaData(schema="<nome>")`
2. Criar `app/modules/<nome>/models/` com os models herdando a nova Base
3. Re-exportar em `app/models/__init__.py`
4. Importar a Base e os models no `alembic/env.py`
5. Adicionar o schema ao `_SCHEMA_TRANSLATE` no `conftest.py`
6. Criar a primeira migration do módulo com `op.execute("CREATE SCHEMA IF NOT EXISTS <nome>")` antes de qualquer `op.create_table`
