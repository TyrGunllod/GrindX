# Skin System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a skin/theming system that allows each company to customize colors, fonts, icons, logos, and branding tokens, managed via an admin module and persisted in the database with JSON fallback.

**Architecture:** CSS Custom Properties + runtime SkinLoader. Two-layer CSS variables (skin tokens → semantic aliases). JSON files as default/fallback, database for per-company overrides. Skin loaded on login via localStorage persistence, applied on dashboard boot via JWT company_id.

**Tech Stack:** FastAPI, SQLAlchemy, PostgreSQL, Alembic, Vanilla JS, CSS Custom Properties, Font Awesome

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `packages/api-postgres/app/models/empresa.py` | Create | Modelo SQLAlchemy para `empresas` (companies) |
| `packages/api-postgres/app/models/theme.py` | Create | Modelo SQLAlchemy para `company_themes` |
| `packages/api-postgres/app/schemas/theme.py` | Create | Pydantic schemas para CRUD de temas |
| `packages/api-postgres/app/routers/theme_router.py` | Create | Endpoints REST para skins |
| `packages/api-postgres/app/repositories/theme_repository.py` | Create | Repository pattern para company_themes |
| `packages/api-postgres/app/services/theme_service.py` | Create | Business logic para skins |
| `packages/api-postgres/alembic/versions/003_add_empresa_and_theme.py` | Create | Migration para empresas + company_themes |
| `packages/api-postgres/app/models/usuario.py` | Modify | Adicionar `empresa_id` FK |
| `packages/api-postgres/app/auth/service.py` | Modify | Incluir `company_id` no JWT payload |
| `packages/api-postgres/app/main.py` | Modify | Registrar theme_router |
| `packages/shared/schemas/auth.py` | Modify | Adicionar `company_id` ao TokenPayload |
| `packages/api-postgres/tests/unit/test_theme_service.py` | Create | Testes unitários do theme service |
| `packages/api-postgres/tests/integration/test_theme_router.py` | Create | Testes de integração do theme router |
| `packages/frontend-webapp/shared/core.css` | Modify | Reorganizar variáveis em skin tokens + semantic aliases |
| `packages/frontend-webapp/shared/skinLoader.js` | Create | Runtime do skin system |
| `packages/frontend-webapp/skins/grindx-default.json` | Create | Skin default JSON |
| `packages/frontend-webapp/skins/_template.json` | Create | Template para novas skins |
| `packages/frontend-webapp/index.html` | Modify | Incluir skinLoader.js |
| `packages/frontend-webapp/dashboard.html` | Modify | Incluir skinLoader.js |
| `packages/frontend-webapp/script.js` | Modify | Salvar company_id no localStorage após login |
| `packages/frontend-webapp/dashboard.js` | Modify | Chamar skinLoader no boot |
| `packages/frontend-webapp/modules/admin-skins/index.html` | Create | UI do módulo admin de skins |
| `packages/frontend-webapp/modules/admin-skins/style.css` | Create | Estilos do módulo admin-skins |
| `packages/frontend-webapp/modules/admin-skins/script.js` | Create | Lógica do módulo admin-skins |

---

### Task 1: Database Models (Empresa + CompanyTheme)

**Files:**
- Create: `packages/api-postgres/app/models/empresa.py`
- Create: `packages/api-postgres/app/models/theme.py`
- Modify: `packages/api-postgres/app/models/__init__.py`
- Test: `packages/api-postgres/tests/unit/test_models_theme.py`

- [ ] **Step 1: Write the failing test**

Create `packages/api-postgres/tests/unit/test_models_theme.py`:

```python
"""Testes unitários para os modelos Empresa e CompanyTheme."""

import pytest
from sqlalchemy.orm import Session

from app.database import Base
from app.models.empresa import Empresa
from app.models.theme import CompanyTheme


def test_create_empresa(db_session: Session):
    """Testa criação de empresa."""
    empresa = Empresa(nome="Acme Corp", dominio="acme.com")
    db_session.add(empresa)
    db_session.commit()
    db_session.refresh(empresa)

    assert empresa.id is not None
    assert empresa.nome == "Acme Corp"
    assert empresa.dominio == "acme.com"
    assert empresa.ativo is True


def test_create_company_theme(db_session: Session):
    """Testa criação de tema vinculado a empresa."""
    empresa = Empresa(nome="Test Corp", dominio="test.com")
    db_session.add(empresa)
    db_session.commit()

    theme = CompanyTheme(
        company_id=empresa.id,
        name="Test Theme",
        colors={"--skin-primary": "#ff0000"},
        icon_library="fontawesome",
    )
    db_session.add(theme)
    db_session.commit()
    db_session.refresh(theme)

    assert theme.id is not None
    assert theme.company_id == empresa.id
    assert theme.is_active is False
    assert theme.colors["--skin-primary"] == "#ff0000"


def test_activate_theme_deactivates_others(db_session: Session):
    """Testa que ativar um tema desativa os outros da mesma empresa."""
    empresa = Empresa(nome="Multi Theme Corp", dominio="multi.com")
    db_session.add(empresa)
    db_session.commit()

    theme1 = CompanyTheme(company_id=empresa.id, name="Theme 1", is_active=True, icon_library="fontawesome")
    theme2 = CompanyTheme(company_id=empresa.id, name="Theme 2", is_active=False, icon_library="fontawesome")
    db_session.add_all([theme1, theme2])
    db_session.commit()

    # Ativar theme2 deve desativar theme1
    theme2.is_active = True
    db_session.commit()

    db_session.refresh(theme1)
    db_session.refresh(theme2)

    assert theme1.is_active is False
    assert theme2.is_active is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd packages/api-postgres && pytest tests/unit/test_models_theme.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.models.empresa'"

- [ ] **Step 3: Write models**

Create `packages/api-postgres/app/models/empresa.py`:

```python
"""
Modelo SQLAlchemy para a entidade Empresa.

Tabela: empresas (PostgreSQL)
Cada empresa pode ter sua própria skin/tema.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Empresa(Base):
    """Mapeamento da tabela 'empresas' no PostgreSQL."""

    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, comment="Nome da empresa")
    dominio: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True, comment="Domínio/subdomínio da empresa"
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="Se a empresa está ativa")
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Empresa(id={self.id}, nome='{self.nome}')>"
```

Create `packages/api-postgres/app/models/theme.py`:

```python
"""
Modelo SQLAlchemy para temas/skins de empresas.

Tabela: company_themes (PostgreSQL)
Armazena personalizações visuais por empresa.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class CompanyTheme(Base):
    """Mapeamento da tabela 'company_themes' no PostgreSQL."""

    __tablename__ = "company_themes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Nome da skin")
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="Skin ativa")
    colors: Mapped[dict | None] = mapped_column(JSONB, nullable=True, comment="Overrides de cores")
    fonts: Mapped[dict | None] = mapped_column(JSONB, nullable=True, comment="Overrides de fontes")
    icon_library: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="fontawesome", comment="Biblioteca de ícones"
    )
    tokens: Mapped[dict | None] = mapped_column(JSONB, nullable=True, comment="Tokens extras (radius, shadows)")
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="URL do logo")
    logo_short_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="URL do logo curto")
    company_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Nome exibido no sistema")
    copyright_text: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="Texto do rodapé")
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<CompanyTheme(id={self.id}, company_id={self.company_id}, name='{self.name}')>"
```

Modify `packages/api-postgres/app/models/__init__.py` to include the new models:

```python
from app.models.empresa import Empresa  # noqa: F401
from app.models.theme import CompanyTheme  # noqa: F401
from app.models.usuario import Usuario, UsuarioModulo  # noqa: F401
from app.models.portal import Aba, Modulo  # noqa: F401
from app.models.produto import Produto  # noqa: F401
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd packages/api-postgres && pytest tests/unit/test_models_theme.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add packages/api-postgres/app/models/empresa.py packages/api-postgres/app/models/theme.py packages/api-postgres/app/models/__init__.py packages/api-postgres/tests/unit/test_models_theme.py
git commit -m "feat(skin): add Empresa and CompanyTheme models"
```

---

### Task 2: Add empresa_id to Usuario + JWT Payload

**Files:**
- Modify: `packages/api-postgres/app/models/usuario.py`
- Modify: `packages/shared/schemas/auth.py`
- Modify: `packages/api-postgres/app/auth/service.py`
- Test: `packages/api-postgres/tests/unit/test_auth.py` (existing)

- [ ] **Step 1: Write the failing test**

Add to `packages/api-postgres/tests/unit/test_auth.py`:

```python
def test_jwt_payload_includes_company_id(db_session, auth_service):
    """Testa que o JWT inclui company_id do usuário."""
    from app.models.empresa import Empresa
    from app.models.usuario import Usuario
    from shared.security.jwt import gerar_hash_senha, verificar_jwt
    from app.core.config import settings

    empresa = Empresa(nome="Test Corp", dominio="test.com")
    db_session.add(empresa)
    db_session.commit()

    usuario = Usuario(
        username="companyuser",
        email="company@test.com",
        nome_completo="User da Empresa",
        senha_hash=gerar_hash_senha("senha123"),
        role="operador",
        empresa_id=empresa.id,
    )
    db_session.add(usuario)
    db_session.commit()

    tokens = auth_service.autenticar("companyuser", "senha123")

    payload = verificar_jwt(tokens.access_token, settings.SECRET_KEY)
    assert payload.company_id == empresa.id
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd packages/api-postgres && pytest tests/unit/test_auth.py::test_jwt_payload_includes_company_id -v`
Expected: FAIL — `empresa_id` column doesn't exist on Usuario

- [ ] **Step 3: Modify Usuario model**

Add to `packages/api-postgres/app/models/usuario.py` (after `ativo` column, before `criado_em`):

```python
    empresa_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True, comment="Empresa do usuário"
    )
```

Add import at top:
```python
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
```
(Integer already imported, just add the column)

- [ ] **Step 4: Modify TokenPayload schema**

Add to `packages/shared/schemas/auth.py`:

```python
class TokenPayload(BaseModel):
    """Schema interno representando o payload decodificado do JWT."""

    sub: str = Field(..., description="ID do usuário (subject)")
    role: str = Field(..., description="Role do usuário")
    company_id: int | None = Field(default=None, description="ID da empresa do usuário")
    exp: int | None = Field(default=None, description="Timestamp de expiração")
```

- [ ] **Step 5: Modify AuthService to include company_id in JWT**

Modify `_gerar_tokens` in `packages/api-postgres/app/auth/service.py`:

Change:
```python
        payload = {"sub": str(usuario.id), "role": usuario.role}
```
To:
```python
        payload = {"sub": str(usuario.id), "role": usuario.role, "company_id": usuario.empresa_id}
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd packages/api-postgres && pytest tests/unit/test_auth.py::test_jwt_payload_includes_company_id -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add packages/api-postgres/app/models/usuario.py packages/shared/schemas/auth.py packages/api-postgres/app/auth/service.py packages/api-postgres/tests/unit/test_auth.py
git commit -m "feat(skin): add empresa_id to Usuario and JWT payload"
```

---

### Task 3: Alembic Migration

**Files:**
- Create: `packages/api-postgres/alembic/versions/003_add_empresa_and_theme.py`

- [ ] **Step 1: Create migration file**

Create `packages/api-postgres/alembic/versions/003_add_empresa_and_theme.py`:

```python
"""add empresa and company_theme tables

Revision ID: 003_add_empresa_and_theme
Revises: 002_add_usuario_modulos
Create Date: 2026-05-20 12:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "003_add_empresa_and_theme"
down_revision = "002_add_usuario_modulos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabela empresas
    op.create_table(
        "empresas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("dominio", sa.String(255), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dominio"),
    )

    # Adicionar empresa_id em usuarios
    op.add_column("usuarios", sa.Column("empresa_id", sa.Integer(), nullable=True, comment="Empresa do usuário"))
    op.create_foreign_key("fk_usuarios_empresa_id", "usuarios", "empresas", ["empresa_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_usuarios_empresa_id", "usuarios", ["empresa_id"])

    # Criar tabela company_themes
    op.create_table(
        "company_themes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("colors", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("fonts", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("icon_library", sa.String(50), nullable=False, server_default="fontawesome"),
        sa.Column("tokens", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("logo_short_url", sa.String(500), nullable=True),
        sa.Column("company_name", sa.String(100), nullable=True),
        sa.Column("copyright_text", sa.String(200), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_company_themes_company_id", "company_themes", ["company_id"])


def downgrade() -> None:
    op.drop_index("ix_company_themes_company_id", table_name="company_themes")
    op.drop_table("company_themes")
    op.drop_index("ix_usuarios_empresa_id", table_name="usuarios")
    op.drop_constraint("fk_usuarios_empresa_id", "usuarios", type_="foreignkey")
    op.drop_column("usuarios", "empresa_id")
    op.drop_table("empresas")
```

- [ ] **Step 2: Verify migration syntax**

Run: `cd packages/api-postgres && python -c "from alembic.versions import _003_add_empresa_and_theme; print('OK')"`
Expected: OK (or import error is fine, just verify no syntax errors)

- [ ] **Step 3: Commit**

```bash
git add packages/api-postgres/alembic/versions/003_add_empresa_and_theme.py
git commit -m "feat(skin): add alembic migration for empresas and company_themes"
```

---

### Task 4: Theme Repository

**Files:**
- Create: `packages/api-postgres/app/repositories/theme_repository.py`
- Modify: `packages/api-postgres/app/repositories/__init__.py`
- Test: `packages/api-postgres/tests/unit/test_theme_repository.py`

- [ ] **Step 1: Write the failing test**

Create `packages/api-postgres/tests/unit/test_theme_repository.py`:

```python
"""Testes unitários para ThemeRepository."""

import pytest
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.theme import CompanyTheme
from app.repositories.theme_repository import ThemeRepository


@pytest.fixture
def theme_repo(db_session: Session) -> ThemeRepository:
    return ThemeRepository(db_session)


@pytest.fixture
def empresa(db_session: Session) -> Empresa:
    emp = Empresa(nome="Test Corp", dominio="test.com")
    db_session.add(emp)
    db_session.commit()
    return emp


@pytest.fixture
def active_theme(db_session: Session, empresa: Empresa) -> CompanyTheme:
    theme = CompanyTheme(
        company_id=empresa.id,
        name="Active Theme",
        is_active=True,
        colors={"--skin-primary": "#ff0000"},
        icon_library="fontawesome",
    )
    db_session.add(theme)
    db_session.commit()
    return theme


def test_find_active_by_company_id(theme_repo: ThemeRepository, empresa: Empresa, active_theme: CompanyTheme):
    """Testa busca do tema ativo por empresa."""
    result = theme_repo.find_active_by_company_id(empresa.id)
    assert result is not None
    assert result.id == active_theme.id
    assert result.colors["--skin-primary"] == "#ff0000"


def test_find_active_returns_none_if_no_theme(theme_repo: ThemeRepository, empresa: Empresa):
    """Testa que retorna None se não há tema ativo."""
    result = theme_repo.find_active_by_company_id(empresa.id)
    assert result is None


def test_find_all_by_company_id(theme_repo: ThemeRepository, empresa: Empresa):
    """Testa busca de todos os temas de uma empresa."""
    t1 = CompanyTheme(company_id=empresa.id, name="Theme 1", icon_library="fontawesome")
    t2 = CompanyTheme(company_id=empresa.id, name="Theme 2", icon_library="fontawesome")
    theme_repo.db.add_all([t1, t2])
    theme_repo.db.commit()

    results = theme_repo.find_all_by_company_id(empresa.id)
    assert len(results) == 2


def test_activate_deactivates_others(theme_repo: ThemeRepository, empresa: Empresa):
    """Testa que ativar um tema desativa os outros."""
    t1 = CompanyTheme(company_id=empresa.id, name="T1", is_active=True, icon_library="fontawesome")
    t2 = CompanyTheme(company_id=empresa.id, name="T2", is_active=False, icon_library="fontawesome")
    theme_repo.db.add_all([t1, t2])
    theme_repo.db.commit()

    theme_repo.activate_theme(t2.id, empresa.id)

    t1_check = theme_repo.db.get(CompanyTheme, t1.id)
    t2_check = theme_repo.db.get(CompanyTheme, t2.id)
    assert t1_check.is_active is False
    assert t2_check.is_active is True


def test_delete_raises_if_active(theme_repo: ThemeRepository, empresa: Empresa, active_theme: CompanyTheme):
    """Testa que não pode deletar tema ativo."""
    from shared.exceptions.base import ConflictError

    with pytest.raises(ConflictError):
        theme_repo.delete(active_theme.id)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd packages/api-postgres && pytest tests/unit/test_theme_repository.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.repositories.theme_repository'"

- [ ] **Step 3: Write repository**

Create `packages/api-postgres/app/repositories/theme_repository.py`:

```python
"""
Repository para CompanyTheme.

Operações de persistência para temas/skins de empresas.
"""

from shared.exceptions.base import ConflictError
from sqlalchemy.orm import Session

from app.models.theme import CompanyTheme


class ThemeRepository:
    """Repository para CRUD de CompanyTheme."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_active_by_company_id(self, company_id: int) -> CompanyTheme | None:
        """Busca o tema ativo de uma empresa."""
        return (
            self.db.query(CompanyTheme)
            .filter(CompanyTheme.company_id == company_id, CompanyTheme.is_active == True)
            .first()
        )

    def find_all_by_company_id(self, company_id: int) -> list[CompanyTheme]:
        """Busca todos os temas de uma empresa."""
        return self.db.query(CompanyTheme).filter(CompanyTheme.company_id == company_id).all()

    def find_by_id(self, theme_id: int) -> CompanyTheme | None:
        """Busca tema por ID."""
        return self.db.get(CompanyTheme, theme_id)

    def create(self, theme: CompanyTheme) -> CompanyTheme:
        """Cria um novo tema."""
        self.db.add(theme)
        self.db.commit()
        self.db.refresh(theme)
        return theme

    def update(self, theme: CompanyTheme, **kwargs) -> CompanyTheme:
        """Atualiza campos de um tema."""
        for key, value in kwargs.items():
            if hasattr(theme, key):
                setattr(theme, key, value)
        self.db.commit()
        self.db.refresh(theme)
        return theme

    def activate_theme(self, theme_id: int, company_id: int) -> CompanyTheme:
        """Ativa um tema e desativa todos os outros da mesma empresa."""
        # Desativar todos os temas da empresa
        self.db.query(CompanyTheme).filter(
            CompanyTheme.company_id == company_id
        ).update({"is_active": False})

        # Ativar o tema selecionado
        theme = self.db.get(CompanyTheme, theme_id)
        if theme is None:
            raise ValueError(f"Tema {theme_id} não encontrado")
        if theme.company_id != company_id:
            raise ValueError(f"Tema {theme_id} não pertence à empresa {company_id}")
        theme.is_active = True
        self.db.commit()
        self.db.refresh(theme)
        return theme

    def delete(self, theme_id: int) -> None:
        """Deleta um tema. Não pode deletar tema ativo."""
        theme = self.db.get(CompanyTheme, theme_id)
        if theme is None:
            raise ValueError(f"Tema {theme_id} não encontrado")
        if theme.is_active:
            raise ConflictError("Não é possível deletar um tema ativo. Desative-o primeiro.")
        self.db.delete(theme)
        self.db.commit()
```

Modify `packages/api-postgres/app/repositories/__init__.py` to export:

```python
from app.repositories.theme_repository import ThemeRepository  # noqa: F401
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd packages/api-postgres && pytest tests/unit/test_theme_repository.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add packages/api-postgres/app/repositories/theme_repository.py packages/api-postgres/app/repositories/__init__.py packages/api-postgres/tests/unit/test_theme_repository.py
git commit -m "feat(skin): add ThemeRepository with CRUD and activation logic"
```

---

### Task 5: Theme Service

**Files:**
- Create: `packages/api-postgres/app/services/theme_service.py`
- Test: `packages/api-postgres/tests/unit/test_theme_service.py`

- [ ] **Step 1: Write the failing test**

Create `packages/api-postgres/tests/unit/test_theme_service.py`:

```python
"""Testes unitários para ThemeService."""

import pytest
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.theme import CompanyTheme
from app.repositories.theme_repository import ThemeRepository
from app.services.theme_service import ThemeService
from shared.exceptions.base import NotFoundError, ConflictError


@pytest.fixture
def theme_service(db_session: Session) -> ThemeService:
    repo = ThemeRepository(db_session)
    return ThemeService(repo)


@pytest.fixture
def empresa(db_session: Session) -> Empresa:
    emp = Empresa(nome="Test Corp", dominio="test.com")
    db_session.add(emp)
    db_session.commit()
    return emp


def test_get_active_theme_returns_none_if_no_theme(theme_service: ThemeService, empresa: Empresa):
    """Testa que retorna None quando não há tema ativo."""
    result = theme_service.get_active_theme(empresa.id)
    assert result is None


def test_get_active_theme(theme_service: ThemeService, empresa: Empresa):
    """Testa busca do tema ativo."""
    theme = CompanyTheme(
        company_id=empresa.id,
        name="Test Theme",
        is_active=True,
        colors={"--skin-primary": "#00ff00"},
        icon_library="fontawesome",
    )
    theme_service.repo.db.add(theme)
    theme_service.repo.db.commit()

    result = theme_service.get_active_theme(empresa.id)
    assert result is not None
    assert result["name"] == "Test Theme"
    assert result["colors"]["--skin-primary"] == "#00ff00"


def test_create_theme(theme_service: ThemeService, empresa: Empresa):
    """Testa criação de tema."""
    result = theme_service.create_theme(
        company_id=empresa.id,
        name="New Theme",
        colors={"--skin-primary": "#123456"},
    )
    assert result["name"] == "New Theme"
    assert result["company_id"] == empresa.id
    assert result["is_active"] is False


def test_update_theme(theme_service: ThemeService, empresa: Empresa):
    """Testa atualização de tema."""
    created = theme_service.create_theme(company_id=empresa.id, name="Old Name", icon_library="fontawesome")
    updated = theme_service.update_theme(created["id"], company_id=empresa.id, name="New Name")
    assert updated["name"] == "New Name"


def test_activate_theme(theme_service: ThemeService, empresa: Empresa):
    """Testa ativação de tema."""
    t1 = theme_service.create_theme(company_id=empresa.id, name="T1", icon_library="fontawesome")
    t2 = theme_service.create_theme(company_id=empresa.id, name="T2", icon_library="fontawesome")

    # Ativar t1
    theme_service.activate_theme(t1["id"], empresa.id)
    t1_check = theme_service.get_theme_by_id(t1["id"])
    assert t1_check["is_active"] is True

    # Ativar t2 deve desativar t1
    theme_service.activate_theme(t2["id"], empresa.id)
    t1_check = theme_service.get_theme_by_id(t1["id"])
    t2_check = theme_service.get_theme_by_id(t2["id"])
    assert t1_check["is_active"] is False
    assert t2_check["is_active"] is True


def test_delete_active_theme_raises(theme_service: ThemeService, empresa: Empresa):
    """Testa que não pode deletar tema ativo."""
    created = theme_service.create_theme(company_id=empresa.id, name="Active", icon_library="fontawesome")
    theme_service.activate_theme(created["id"], empresa.id)

    with pytest.raises(ConflictError):
        theme_service.delete_theme(created["id"])


def test_list_themes(theme_service: ThemeService, empresa: Empresa):
    """Testa listagem de temas."""
    theme_service.create_theme(company_id=empresa.id, name="T1", icon_library="fontawesome")
    theme_service.create_theme(company_id=empresa.id, name="T2", icon_library="fontawesome")

    results = theme_service.list_themes(empresa.id)
    assert len(results) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd packages/api-postgres && pytest tests/unit/test_theme_service.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.services.theme_service'"

- [ ] **Step 3: Write service**

Create `packages/api-postgres/app/services/theme_service.py`:

```python
"""
Service para CompanyTheme.

Business logic para gestão de skins/temas de empresas.
"""

import structlog
from shared.exceptions.base import NotFoundError

from app.repositories.theme_repository import ThemeRepository

logger = structlog.get_logger(__name__)


class ThemeService:
    """Service para CRUD de temas de empresas."""

    def __init__(self, repo: ThemeRepository) -> None:
        self.repo = repo

    def get_active_theme(self, company_id: int) -> dict | None:
        """Retorna o tema ativo de uma empresa como dict serializável."""
        theme = self.repo.find_active_by_company_id(company_id)
        if theme is None:
            return None
        return self._to_dict(theme)

    def list_themes(self, company_id: int) -> list[dict]:
        """Lista todos os temas de uma empresa."""
        themes = self.repo.find_all_by_company_id(company_id)
        return [self._to_dict(t) for t in themes]

    def get_theme_by_id(self, theme_id: int) -> dict | None:
        """Busca tema por ID."""
        theme = self.repo.find_by_id(theme_id)
        if theme is None:
            return None
        return self._to_dict(theme)

    def create_theme(
        self,
        company_id: int,
        name: str,
        colors: dict | None = None,
        fonts: dict | None = None,
        icon_library: str = "fontawesome",
        tokens: dict | None = None,
        logo_url: str | None = None,
        logo_short_url: str | None = None,
        company_name: str | None = None,
        copyright_text: str | None = None,
    ) -> dict:
        """Cria um novo tema."""
        from app.models.theme import CompanyTheme

        theme = CompanyTheme(
            company_id=company_id,
            name=name,
            colors=colors,
            fonts=fonts,
            icon_library=icon_library,
            tokens=tokens,
            logo_url=logo_url,
            logo_short_url=logo_short_url,
            company_name=company_name,
            copyright_text=copyright_text,
        )
        theme = self.repo.create(theme)
        logger.info("Tema criado", theme_id=theme.id, company_id=company_id)
        return self._to_dict(theme)

    def update_theme(self, theme_id: int, company_id: int, **kwargs) -> dict:
        """Atualiza um tema existente."""
        theme = self.repo.find_by_id(theme_id)
        if theme is None:
            raise NotFoundError(f"Tema {theme_id} não encontrado")
        if theme.company_id != company_id:
            raise NotFoundError(f"Tema {theme_id} não pertence à empresa {company_id}")

        theme = self.repo.update(theme, **kwargs)
        logger.info("Tema atualizado", theme_id=theme.id)
        return self._to_dict(theme)

    def activate_theme(self, theme_id: int, company_id: int) -> dict:
        """Ativa um tema e desativa os outros da mesma empresa."""
        theme = self.repo.activate_theme(theme_id, company_id)
        logger.info("Tema ativado", theme_id=theme.id, company_id=company_id)
        return self._to_dict(theme)

    def delete_theme(self, theme_id: int) -> None:
        """Deleta um tema."""
        self.repo.delete(theme_id)
        logger.info("Tema deletado", theme_id=theme_id)

    @staticmethod
    def _to_dict(theme) -> dict:
        """Converte modelo para dict serializável."""
        return {
            "id": theme.id,
            "company_id": theme.company_id,
            "name": theme.name,
            "is_active": theme.is_active,
            "colors": theme.colors,
            "fonts": theme.fonts,
            "icon_library": theme.icon_library,
            "tokens": theme.tokens,
            "logo_url": theme.logo_url,
            "logo_short_url": theme.logo_short_url,
            "company_name": theme.company_name,
            "copyright_text": theme.copyright_text,
            "criado_em": theme.criado_em.isoformat() if theme.criado_em else None,
            "atualizado_em": theme.atualizado_em.isoformat() if theme.atualizado_em else None,
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd packages/api-postgres && pytest tests/unit/test_theme_service.py -v`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add packages/api-postgres/app/services/theme_service.py packages/api-postgres/tests/unit/test_theme_service.py
git commit -m "feat(skin): add ThemeService with business logic"
```

---

### Task 6: Theme Router (API Endpoints)

**Files:**
- Create: `packages/api-postgres/app/schemas/theme.py`
- Create: `packages/api-postgres/app/routers/theme_router.py`
- Modify: `packages/api-postgres/app/main.py`
- Test: `packages/api-postgres/tests/integration/test_theme_router.py`

- [ ] **Step 1: Write schemas**

Create `packages/api-postgres/app/schemas/theme.py`:

```python
"""Schemas para o CRUD de temas/skins."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ThemeCreate(BaseModel):
    """Schema para criação de tema."""

    name: str = Field(..., min_length=1, max_length=100, description="Nome da skin")
    colors: Optional[dict] = Field(default=None, description="Overrides de cores")
    fonts: Optional[dict] = Field(default=None, description="Overrides de fontes")
    icon_library: str = Field(default="fontawesome", description="Biblioteca de ícones")
    tokens: Optional[dict] = Field(default=None, description="Tokens extras")
    logo_url: Optional[str] = Field(default=None, max_length=500, description="URL do logo")
    logo_short_url: Optional[str] = Field(default=None, max_length=500, description="URL do logo curto")
    company_name: Optional[str] = Field(default=None, max_length=100, description="Nome exibido no sistema")
    copyright_text: Optional[str] = Field(default=None, max_length=200, description="Texto do rodapé")


class ThemeUpdate(BaseModel):
    """Schema para atualização de tema (todos opcionais)."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    colors: Optional[dict] = None
    fonts: Optional[dict] = None
    icon_library: Optional[str] = None
    tokens: Optional[dict] = None
    logo_url: Optional[str] = Field(default=None, max_length=500)
    logo_short_url: Optional[str] = Field(default=None, max_length=500)
    company_name: Optional[str] = Field(default=None, max_length=100)
    copyright_text: Optional[str] = Field(default=None, max_length=200)


class ThemeResponse(BaseModel):
    """Schema de resposta para tema."""

    id: int
    company_id: int
    name: str
    is_active: bool
    colors: dict | None = None
    fonts: dict | None = None
    icon_library: str
    tokens: dict | None = None
    logo_url: str | None = None
    logo_short_url: str | None = None
    company_name: str | None = None
    copyright_text: str | None = None
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None

    class Config:
        from_attributes = True
```

- [ ] **Step 2: Write router**

Create `packages/api-postgres/app/routers/theme_router.py`:

```python
"""
Router para gestão de temas/skins de empresas.

Endpoints para CRUD de temas e ativação.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from shared.exceptions.base import ConflictError, NotFoundError
from shared.schemas.base import ErrorResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_db, require_role
from app.repositories.theme_repository import ThemeRepository
from app.schemas.theme import ThemeCreate, ThemeResponse, ThemeUpdate
from app.services.theme_service import ThemeService

router = APIRouter(prefix="/v1/themes", tags=["Temas"])


def _get_theme_service(db: Session = Depends(get_db)) -> ThemeService:
    repo = ThemeRepository(db)
    return ThemeService(repo)


@router.get(
    "/active",
    response_model=ThemeResponse,
    summary="Tema ativo da empresa",
    description="Retorna o tema ativo da empresa do usuário logado.",
    responses={404: {"model": ErrorResponse, "description": "Nenhum tema ativo encontrado"}},
)
def get_active_theme(
    current_user=Depends(get_current_user),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Retorna o tema ativo da empresa do usuário."""
    if not current_user.company_id:
        raise HTTPException(status_code=404, detail="Usuário não possui empresa vinculada")

    theme = service.get_active_theme(current_user.company_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Nenhum tema ativo encontrado para esta empresa")
    return theme


@router.get(
    "",
    response_model=list[ThemeResponse],
    summary="Listar temas",
    description="Lista todos os temas da empresa do usuário logado. Requer role admin.",
)
def list_themes(
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> list[dict]:
    """Lista todos os temas da empresa."""
    return service.list_themes(current_user.company_id)


@router.get(
    "/{theme_id}",
    response_model=ThemeResponse,
    summary="Detalhes do tema",
    description="Retorna detalhes de um tema específico. Requer role admin.",
    responses={404: {"model": ErrorResponse, "description": "Tema não encontrado"}},
)
def get_theme(
    theme_id: int,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Retorna detalhes de um tema."""
    theme = service.get_theme_by_id(theme_id)
    if theme is None or theme["company_id"] != current_user.company_id:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    return theme


@router.post(
    "",
    response_model=ThemeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tema",
    description="Cria um novo tema para a empresa. Requer role admin.",
)
def create_theme(
    dados: ThemeCreate,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Cria um novo tema."""
    return service.create_theme(company_id=current_user.company_id, **dados.model_dump())


@router.put(
    "/{theme_id}",
    response_model=ThemeResponse,
    summary="Atualizar tema",
    description="Atualiza um tema existente. Requer role admin.",
    responses={404: {"model": ErrorResponse, "description": "Tema não encontrado"}},
)
def update_theme(
    theme_id: int,
    dados: ThemeUpdate,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Atualiza um tema."""
    update_data = dados.model_dump(exclude_unset=True)
    return service.update_theme(theme_id, company_id=current_user.company_id, **update_data)


@router.post(
    "/{theme_id}/activate",
    response_model=ThemeResponse,
    summary="Ativar tema",
    description="Ativa um tema e desativa os outros da mesma empresa. Requer role admin.",
    responses={404: {"model": ErrorResponse, "description": "Tema não encontrado"}},
)
def activate_theme(
    theme_id: int,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Ativa um tema."""
    try:
        return service.activate_theme(theme_id, company_id=current_user.company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete(
    "/{theme_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar tema",
    description="Deleta um tema. Não pode deletar tema ativo. Requer role admin.",
    responses={
        404: {"model": ErrorResponse, "description": "Tema não encontrado"},
        409: {"model": ErrorResponse, "description": "Tema está ativo"},
    },
)
def delete_theme(
    theme_id: int,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> None:
    """Deleta um tema."""
    try:
        service.delete_theme(theme_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
```

- [ ] **Step 3: Register router in main.py**

Add to `packages/api-postgres/app/main.py`:

```python
from app.routers.theme_router import router as theme_router
```

And after the existing `app.include_router` calls:

```python
app.include_router(theme_router)
```

- [ ] **Step 4: Write integration tests**

Create `packages/api-postgres/tests/integration/test_theme_router.py`:

```python
"""Testes de integração para o router de temas."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.theme import CompanyTheme
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha


@pytest.fixture
def empresa(db_session: Session) -> Empresa:
    emp = Empresa(nome="Test Corp", dominio="test.com")
    db_session.add(emp)
    db_session.commit()
    return emp


@pytest.fixture
def admin_user(db_session: Session, empresa: Empresa) -> Usuario:
    user = Usuario(
        username="admintheme",
        email="admin@theme.com",
        nome_completo="Admin Theme",
        senha_hash=gerar_hash_senha("senha123"),
        role="admin",
        empresa_id=empresa.id,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_auth_headers(client: TestClient, admin_user: Usuario) -> dict:
    response = client.post(
        "/v1/auth/token",
        json={"username": "admintheme", "password": "senha123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_active_theme_no_theme(client: TestClient, admin_auth_headers: dict):
    """Testa que retorna 404 quando não há tema ativo."""
    response = client.get("/v1/themes/active", headers=admin_auth_headers)
    assert response.status_code == 404


def test_create_and_get_active_theme(client: TestClient, admin_auth_headers: dict):
    """Testa criação e busca do tema ativo."""
    # Criar tema
    create_resp = client.post(
        "/v1/themes",
        json={
            "name": "Test Active",
            "colors": {"--skin-primary": "#ff0000"},
            "icon_library": "fontawesome",
        },
        headers=admin_auth_headers,
    )
    assert create_resp.status_code == 201
    theme_id = create_resp.json()["id"]

    # Ativar tema
    activate_resp = client.post(f"/v1/themes/{theme_id}/activate", headers=admin_auth_headers)
    assert activate_resp.status_code == 200
    assert activate_resp.json()["is_active"] is True

    # Buscar tema ativo
    get_resp = client.get("/v1/themes/active", headers=admin_auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Test Active"
    assert get_resp.json()["colors"]["--skin-primary"] == "#ff0000"


def test_list_themes(client: TestClient, admin_auth_headers: dict):
    """Testa listagem de temas."""
    client.post("/v1/themes", json={"name": "T1", "icon_library": "fontawesome"}, headers=admin_auth_headers)
    client.post("/v1/themes", json={"name": "T2", "icon_library": "fontawesome"}, headers=admin_auth_headers)

    response = client.get("/v1/themes", headers=admin_auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_active_theme_fails(client: TestClient, admin_auth_headers: dict):
    """Testa que não pode deletar tema ativo."""
    create_resp = client.post(
        "/v1/themes",
        json={"name": "Delete Test", "icon_library": "fontawesome"},
        headers=admin_auth_headers,
    )
    theme_id = create_resp.json()["id"]

    # Ativar
    client.post(f"/v1/themes/{theme_id}/activate", headers=admin_auth_headers)

    # Tentar deletar
    delete_resp = client.delete(f"/v1/themes/{theme_id}", headers=admin_auth_headers)
    assert delete_resp.status_code == 409


def test_delete_inactive_theme_succeeds(client: TestClient, admin_auth_headers: dict):
    """Testa que pode deletar tema inativo."""
    create_resp = client.post(
        "/v1/themes",
        json={"name": "Delete Inactive", "icon_library": "fontawesome"},
        headers=admin_auth_headers,
    )
    theme_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/v1/themes/{theme_id}", headers=admin_auth_headers)
    assert delete_resp.status_code == 204
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd packages/api-postgres && pytest tests/integration/test_theme_router.py -v`
Expected: PASS (5 tests)

- [ ] **Step 6: Commit**

```bash
git add packages/api-postgres/app/schemas/theme.py packages/api-postgres/app/routers/theme_router.py packages/api-postgres/app/main.py packages/api-postgres/tests/integration/test_theme_router.py
git commit -m "feat(skin): add theme router with CRUD endpoints and integration tests"
```

---

### Task 7: Reorganize core.css (Skin Tokens + Semantic Aliases)

**Files:**
- Modify: `packages/frontend-webapp/shared/core.css`

- [ ] **Step 1: Reorganize CSS variables**

Replace the `:root` block in `packages/frontend-webapp/shared/core.css` (lines 52-80) with:

```css
:root {
    /* Spacing Scale (Rem based) */
    --space-1: 0.25rem;
    --space-2: 0.5rem;
    --space-4: 1rem;
    --space-8: 2rem;

    /* GrindX Brand Tokens */
    --brand-natt: #06090f;
    --brand-fjord: #0d1e35;
    --brand-is: #00c2e0;
    --brand-eld: #ff4d00;
    --brand-rimfrost: #ddeaf2;
    --brand-askr: #4a5e72;

    /* === SKIN TOKENS (overrideáveis pelo skinLoader) === */

    /* Colors */
    --skin-primary: #00c2e0;
    --skin-primary-hover: #00a8c4;
    --skin-danger: #ef4444;
    --skin-success: #10b981;
    --skin-warning: #f59e0b;
    --skin-bg-main: #f8fafc;
    --skin-bg-card: #ffffff;
    --skin-text-main: #1e293b;
    --skin-text-muted: #64748b;
    --skin-border-color: #e2e8f0;
    --skin-focus-ring: rgba(0, 194, 224, 0.35);

    /* Dark mode color overrides (opcionais, com fallback) */
    --skin-bg-main-dark: #0f172a;
    --skin-bg-card-dark: #1e293b;
    --skin-text-main-dark: #f8fafc;
    --skin-text-muted-dark: #94a3b8;
    --skin-border-color-dark: rgba(255, 255, 255, 0.05);

    /* Fonts */
    --skin-font-heading: 'Barlow Condensed', 'Arial Narrow', sans-serif;
    --skin-font-body: 'DM Sans', system-ui, -apple-system, sans-serif;

    /* Tokens */
    --skin-radius-sm: 0.25rem;
    --skin-radius-md: 0.5rem;
    --skin-radius-lg: 0.75rem;
    --skin-radius-xl: 1.5rem;
    --skin-shadow-card: 0 10px 25px rgba(0,0,0,0.1);
    --skin-shadow-modal: 0 20px 25px -5px rgba(0,0,0,0.2);

    /* === SEMANTIC ALIASES (usados pelo CSS, não sobrescrever diretamente) === */
    --primary: var(--skin-primary);
    --primary-hover: var(--skin-primary-hover);
    --danger: var(--skin-danger);
    --success: var(--skin-success);
    --warning: var(--skin-warning);
    --bg-main: var(--skin-bg-main);
    --bg-card: var(--skin-bg-card);
    --text-main: var(--skin-text-main);
    --text-muted: var(--skin-text-muted);
    --border-color: var(--skin-border-color);
    --focus-ring: var(--skin-focus-ring);
}
```

Replace the dark mode block (lines 84-100) with:

```css
/* Dark Mode (Class based or Auto) */
@media (prefers-color-scheme: dark) {
    :root:not(.light-theme) {
        --bg-main: var(--skin-bg-main-dark, #0f172a);
        --bg-card: var(--skin-bg-card-dark, #1e293b);
        --text-main: var(--skin-text-main-dark, #f8fafc);
        --text-muted: var(--skin-text-muted-dark, #94a3b8);
        --border-color: var(--skin-border-color-dark, rgba(255, 255, 255, 0.05));
    }
}

.dark-theme {
    --bg-main: var(--skin-bg-main-dark, #0f172a);
    --bg-card: var(--skin-bg-card-dark, #1e293b);
    --text-main: var(--skin-text-main-dark, #f8fafc);
    --text-muted: var(--skin-text-muted-dark, #94a3b8);
    --border-color: var(--skin-border-color-dark, rgba(255, 255, 255, 0.05));
}
```

- [ ] **Step 2: Verify no CSS breakage**

Open `packages/frontend-webapp/index.html` in browser and verify login page renders correctly.

- [ ] **Step 3: Commit**

```bash
git add packages/frontend-webapp/shared/core.css
git commit -m "refactor(skin): reorganize CSS variables into skin tokens and semantic aliases"
```

---

### Task 8: Create skinLoader.js

**Files:**
- Create: `packages/frontend-webapp/shared/skinLoader.js`
- Create: `packages/frontend-webapp/skins/grindx-default.json`
- Create: `packages/frontend-webapp/skins/_template.json`

- [ ] **Step 1: Create default skin JSON**

Create `packages/frontend-webapp/skins/grindx-default.json`:

```json
{
  "name": "GrindX Default",
  "colors": {
    "--skin-primary": "#00c2e0",
    "--skin-primary-hover": "#00a8c4",
    "--skin-danger": "#ef4444",
    "--skin-success": "#10b981",
    "--skin-warning": "#f59e0b",
    "--skin-bg-main": "#f8fafc",
    "--skin-bg-card": "#ffffff",
    "--skin-text-main": "#1e293b",
    "--skin-text-muted": "#64748b",
    "--skin-border-color": "#e2e8f0",
    "--skin-focus-ring": "rgba(0, 194, 224, 0.35)",
    "--skin-bg-main-dark": "#0f172a",
    "--skin-bg-card-dark": "#1e293b",
    "--skin-text-main-dark": "#f8fafc",
    "--skin-text-muted-dark": "#94a3b8",
    "--skin-border-color-dark": "rgba(255, 255, 255, 0.05)"
  },
  "fonts": {
    "heading": "Barlow Condensed",
    "body": "DM Sans"
  },
  "icon_library": "fontawesome",
  "tokens": {
    "--skin-radius-sm": "0.25rem",
    "--skin-radius-md": "0.5rem",
    "--skin-radius-lg": "0.75rem",
    "--skin-radius-xl": "1.5rem",
    "--skin-shadow-card": "0 10px 25px rgba(0,0,0,0.1)",
    "--skin-shadow-modal": "0 20px 25px -5px rgba(0,0,0,0.2)"
  },
  "company_name": "GrindX",
  "copyright_text": "© 2026 GrindX. Desenvolvido por Alex Grellet.",
  "logo_url": null,
  "logo_short_url": null
}
```

Create `packages/frontend-webapp/skins/_template.json`:

```json
{
  "name": "Nome da Skin",
  "colors": {
    "--skin-primary": "#00c2e0",
    "--skin-primary-hover": "#00a8c4",
    "--skin-danger": "#ef4444",
    "--skin-success": "#10b981",
    "--skin-warning": "#f59e0b",
    "--skin-bg-main": "#f8fafc",
    "--skin-bg-card": "#ffffff",
    "--skin-text-main": "#1e293b",
    "--skin-text-muted": "#64748b",
    "--skin-border-color": "#e2e8f0",
    "--skin-focus-ring": "rgba(0, 194, 224, 0.35)"
  },
  "fonts": {
    "heading": "Barlow Condensed",
    "body": "DM Sans"
  },
  "icon_library": "fontawesome",
  "tokens": {
    "--skin-radius-sm": "0.25rem",
    "--skin-radius-md": "0.5rem",
    "--skin-radius-lg": "0.75rem",
    "--skin-radius-xl": "1.5rem"
  },
  "company_name": "Nome da Empresa",
  "copyright_text": "© 2026 Nome da Empresa. Todos os direitos reservados.",
  "logo_url": null,
  "logo_short_url": null
}
```

- [ ] **Step 2: Create skinLoader.js**

Create `packages/frontend-webapp/shared/skinLoader.js`:

```javascript
/**
 * SKIN LOADER - GrindX
 * Runtime do sistema de skins/theming.
 * Carrega e aplica skins do DB (via API) ou JSON fallback.
 */

const SKIN_DEFAULTS = {
    colors: {
        '--skin-primary': '#00c2e0',
        '--skin-primary-hover': '#00a8c4',
        '--skin-danger': '#ef4444',
        '--skin-success': '#10b981',
        '--skin-warning': '#f59e0b',
        '--skin-bg-main': '#f8fafc',
        '--skin-bg-card': '#ffffff',
        '--skin-text-main': '#1e293b',
        '--skin-text-muted': '#64748b',
        '--skin-border-color': '#e2e8f0',
        '--skin-focus-ring': 'rgba(0, 194, 224, 0.35)',
        '--skin-bg-main-dark': '#0f172a',
        '--skin-bg-card-dark': '#1e293b',
        '--skin-text-main-dark': '#f8fafc',
        '--skin-text-muted-dark': '#94a3b8',
        '--skin-border-color-dark': 'rgba(255, 255, 255, 0.05)',
    },
    fonts: { heading: 'Barlow Condensed', body: 'DM Sans' },
    icon_library: 'fontawesome',
    tokens: {
        '--skin-radius-sm': '0.25rem',
        '--skin-radius-md': '0.5rem',
        '--skin-radius-lg': '0.75rem',
        '--skin-radius-xl': '1.5rem',
        '--skin-shadow-card': '0 10px 25px rgba(0,0,0,0.1)',
        '--skin-shadow-modal': '0 20px 25px -5px rgba(0,0,0,0.2)',
    },
    company_name: 'GrindX',
    copyright_text: '© 2026 GrindX. Desenvolvido por Alex Grellet.',
    logo_url: null,
    logo_short_url: null,
};

const ICON_CDN_MAP = {
    fontawesome: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    lucide: 'https://unpkg.com/lucide@latest/dist/umd/lucide.min.js',
    material: 'https://fonts.googleapis.com/icon?family=Material+Icons',
};

const FONT_CDN_MAP = {
    Inter: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
    Roboto: 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap',
    'Open Sans': 'https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap',
};

class SkinLoader {
    constructor() {
        this.currentSkin = null;
        this._iconLinkEl = null;
        this._fontLinkEl = null;
    }

    async load(companyId) {
        let skin = null;

        // 1. Tenta API
        if (companyId) {
            skin = await this._fetchFromAPI(companyId);
        }

        // 2. Fallback para JSON local
        if (!skin) {
            skin = await this._fetchFromJSON('grindx-default');
        }

        // 3. Merge com defaults
        const merged = this._deepMerge(SKIN_DEFAULTS, skin || {});
        this.currentSkin = merged;

        // 4. Aplica
        this._applyColors(merged.colors);
        this._applyTokens(merged.tokens);
        this._applyFonts(merged.fonts);
        this._loadIconLibrary(merged.icon_library);
        this._updateBranding(merged.company_name, merged.copyright_text);
        this._updateLogos(merged.logo_url, merged.logo_short_url);
    }

    async reload(companyId) {
        await this.load(companyId);
    }

    async _fetchFromAPI(companyId) {
        try {
            const token = grindx?.session?.getToken();
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            const baseUrl = grindx?.config?.API_BASE_URL || 'http://127.0.0.1:8002/v1';
            const resp = await fetch(`${baseUrl}/themes/active`, { headers });
            if (!resp.ok) return null;
            return await resp.json();
        } catch (e) {
            console.warn('SkinLoader: API indisponível, usando fallback', e);
            return null;
        }
    }

    async _fetchFromJSON(skinName) {
        try {
            const resp = await fetch(`skins/${skinName}.json`);
            if (!resp.ok) return null;
            return await resp.json();
        } catch (e) {
            console.warn('SkinLoader: JSON fallback indisponível', e);
            return null;
        }
    }

    _deepMerge(target, source) {
        const result = { ...target };
        for (const key of Object.keys(source)) {
            if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                result[key] = this._deepMerge(target[key] || {}, source[key]);
            } else if (source[key] !== undefined && source[key] !== null) {
                result[key] = source[key];
            }
        }
        return result;
    }

    _applyColors(colors) {
        if (!colors) return;
        const root = document.documentElement;
        for (const [key, value] of Object.entries(colors)) {
            if (key.startsWith('--skin-')) {
                root.style.setProperty(key, value);
            }
        }
    }

    _applyTokens(tokens) {
        if (!tokens) return;
        const root = document.documentElement;
        for (const [key, value] of Object.entries(tokens)) {
            if (key.startsWith('--skin-')) {
                root.style.setProperty(key, value);
            }
        }
    }

    _applyFonts(fonts) {
        if (!fonts) return;

        // Remove font link anterior
        if (this._fontLinkEl) {
            this._fontLinkEl.remove();
            this._fontLinkEl = null;
        }

        // Carrega Google Fonts se necessário
        const fontNames = [fonts.heading, fonts.body].filter(Boolean);
        for (const name of fontNames) {
            if (FONT_CDN_MAP[name]) {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = FONT_CDN_MAP[name];
                document.head.appendChild(link);
                this._fontLinkEl = link;
            }
        }

        // Aplica font-family
        const root = document.documentElement;
        if (fonts.heading) {
            root.style.setProperty('--skin-font-heading', `'${fonts.heading}', 'Arial Narrow', sans-serif`);
        }
        if (fonts.body) {
            root.style.setProperty('--skin-font-body', `'${fonts.body}', system-ui, -apple-system, sans-serif`);
        }
    }

    _loadIconLibrary(library) {
        if (!library || library === 'fontawesome') return;

        // Remove link anterior
        if (this._iconLinkEl) {
            this._iconLinkEl.remove();
            this._iconLinkEl = null;
        }

        const cdnUrl = ICON_CDN_MAP[library];
        if (!cdnUrl) return;

        if (library === 'lucide') {
            const script = document.createElement('script');
            script.src = cdnUrl;
            script.onload = () => {
                if (window.lucide) {
                    window.lucide.createIcons();
                }
            };
            document.head.appendChild(script);
            this._iconLinkEl = script;
        } else {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = cdnUrl;
            document.head.appendChild(link);
            this._iconLinkEl = link;
        }
    }

    _updateBranding(companyName, copyrightText) {
        // Atualiza título da página
        if (companyName) {
            document.title = document.title.replace('GrindX', companyName);

            // Atualiza logo no sidebar
            const logoEl = document.querySelector('.logo-grindx');
            if (logoEl) {
                logoEl.innerHTML = companyName.substring(0, 1) + '<span class="logo-full">' + companyName.substring(1) + '</span>';
            }

            // Atualiza copyright no sidebar
            const copyrightEl = document.querySelector('.copyright-text');
            if (copyrightEl && copyrightText) {
                copyrightEl.textContent = copyrightText;
            }

            // Atualiza copyright no login
            const loginCopyright = document.querySelector('.login-page .text-center[style*="font-size: 0.7rem"]');
            if (loginCopyright && copyrightText) {
                loginCopyright.textContent = copyrightText;
            }
        }
    }

    _updateLogos(logoUrl, logoShortUrl) {
        if (logoUrl) {
            // Atualiza logo no sidebar
            const logoEl = document.querySelector('.logo-grindx');
            if (logoEl) {
                logoEl.innerHTML = `<img src="${logoUrl}" alt="Logo" style="max-height: 32px; width: auto;">`;
            }
        }
        if (logoShortUrl) {
            // Atualiza favicon
            const favicon = document.querySelector('link[rel="icon"]');
            if (favicon) {
                favicon.href = logoShortUrl;
            }
        }
    }

    // Live preview para admin module
    applyPreviewColors(colors) {
        if (!colors) return;
        const root = document.documentElement;
        for (const [key, value] of Object.entries(colors)) {
            if (key.startsWith('--skin-')) {
                root.style.setProperty(key, value);
            }
        }
    }

    resetToDefaults() {
        const root = document.documentElement;
        for (const [key, value] of Object.entries(SKIN_DEFAULTS.colors)) {
            root.style.setProperty(key, value);
        }
        for (const [key, value] of Object.entries(SKIN_DEFAULTS.tokens)) {
            root.style.setProperty(key, value);
        }
    }
}

// Instância global
window.skinLoader = new SkinLoader();
```

- [ ] **Step 3: Commit**

```bash
git add packages/frontend-webapp/shared/skinLoader.js packages/frontend-webapp/skins/grindx-default.json packages/frontend-webapp/skins/_template.json
git commit -m "feat(skin): add skinLoader.js runtime and default skin JSON"
```

---

### Task 9: Integrate skinLoader into Login and Dashboard

**Files:**
- Modify: `packages/frontend-webapp/index.html`
- Modify: `packages/frontend-webapp/dashboard.html`
- Modify: `packages/frontend-webapp/script.js`
- Modify: `packages/frontend-webapp/dashboard.js`

- [ ] **Step 1: Modify index.html (login)**

Add before `</body>` in `packages/frontend-webapp/index.html`, after the existing scripts:

```html
    <script src="shared/skinLoader.js"></script>
```

- [ ] **Step 2: Modify script.js (login) to save company_id after login**

Find the login success handler in `packages/frontend-webapp/script.js` and add after tokens are saved:

```javascript
// Salvar company_id para skin do próximo login
if (userProfile?.empresa_id) {
    window.grindx.storage.set('last_skin_company_id', String(userProfile.empresa_id));
}
```

Also add on page load to apply last skin:

```javascript
// Aplicar skin da última empresa usada
(function applyLastSkin() {
    const lastCompanyId = window.grindx?.storage?.get('last_skin_company_id');
    if (lastCompanyId && window.skinLoader) {
        window.skinLoader.load(parseInt(lastCompanyId));
    }
})();
```

- [ ] **Step 3: Modify dashboard.html**

Add in `<head>` after existing stylesheets:

```html
    <script src="shared/skinLoader.js"></script>
```

- [ ] **Step 4: Modify dashboard.js to call skinLoader on boot**

Add to `DashboardController.init()` method, after `this.checkAuth()`:

```javascript
        // Carregar skin da empresa
        this.loadCompanySkin();
```

Add new method to `DashboardController`:

```javascript
    loadCompanySkin() {
        const companyId = this.user?.company_id;
        if (companyId && window.skinLoader) {
            window.skinLoader.load(parseInt(companyId)).then(() => {
                // Salvar para próximo login
                window.grindx.storage.set('last_skin_company_id', String(companyId));
            });
        }
    }
```

- [ ] **Step 5: Verify integration**

Run the frontend and verify:
1. Login page loads with default skin
2. After login, dashboard applies company skin
3. `last_skin_company_id` is saved in localStorage

- [ ] **Step 6: Commit**

```bash
git add packages/frontend-webapp/index.html packages/frontend-webapp/dashboard.html packages/frontend-webapp/script.js packages/frontend-webapp/dashboard.js
git commit -m "feat(skin): integrate skinLoader into login and dashboard"
```

---

### Task 10: Admin Skins Module (Frontend UI)

**Files:**
- Create: `packages/frontend-webapp/modules/admin-skins/index.html`
- Create: `packages/frontend-webapp/modules/admin-skins/style.css`
- Create: `packages/frontend-webapp/modules/admin-skins/script.js`

- [ ] **Step 1: Create index.html**

Create `packages/frontend-webapp/modules/admin-skins/index.html`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestão de Skins</title>
    <link rel="stylesheet" href="../../shared/core.css">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="module-page">
        <header class="skins-header">
            <h1 class="font-display">Gestão de Skins</h1>
            <button class="btn btn-primary" id="btnNewSkin">
                <i class="fas fa-plus"></i> Nova Skin
            </button>
        </header>

        <div class="skins-grid" id="skinsGrid">
            <!-- Skins serão renderizadas aqui -->
        </div>

        <!-- Modal de Edição -->
        <div class="modal-overlay" id="skinModal" style="display: none;">
            <div class="modal-card skin-modal">
                <div class="modal-header">
                    <h2 id="modalTitle">Nova Skin</h2>
                    <button class="btn-icon" id="btnCloseModal">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <form id="skinForm" class="skin-form">
                    <!-- Identidade -->
                    <fieldset class="form-section">
                        <legend>Identidade</legend>
                        <div class="form-row">
                            <label for="skinName">Nome da Skin</label>
                            <input type="text" id="skinName" required placeholder="Ex: Acme Corp Blue">
                        </div>
                        <div class="form-row">
                            <label for="companyName">Nome da Empresa no Sistema</label>
                            <input type="text" id="companyName" placeholder="Ex: Acme Corporation">
                        </div>
                        <div class="form-row">
                            <label for="copyrightText">Copyright</label>
                            <input type="text" id="copyrightText" placeholder="© 2026 Acme Corp. Todos os direitos reservados.">
                        </div>
                        <div class="form-row">
                            <label for="logoUrl">URL do Logo</label>
                            <input type="text" id="logoUrl" placeholder="https://exemplo.com/logo.svg">
                        </div>
                        <div class="form-row">
                            <label for="logoShortUrl">URL do Logo Curto (favicon)</label>
                            <input type="text" id="logoShortUrl" placeholder="https://exemplo.com/favicon.ico">
                        </div>
                    </fieldset>

                    <!-- Cores -->
                    <fieldset class="form-section">
                        <legend>Cores</legend>
                        <div class="color-grid">
                            <div class="color-picker-group">
                                <label for="colorPrimary">Primary</label>
                                <input type="color" id="colorPrimary" value="#00c2e0">
                                <span class="color-value" id="colorPrimaryValue">#00c2e0</span>
                            </div>
                            <div class="color-picker-group">
                                <label for="colorDanger">Danger</label>
                                <input type="color" id="colorDanger" value="#ef4444">
                                <span class="color-value" id="colorDangerValue">#ef4444</span>
                            </div>
                            <div class="color-picker-group">
                                <label for="colorSuccess">Success</label>
                                <input type="color" id="colorSuccess" value="#10b981">
                                <span class="color-value" id="colorSuccessValue">#10b981</span>
                            </div>
                            <div class="color-picker-group">
                                <label for="colorWarning">Warning</label>
                                <input type="color" id="colorWarning" value="#f59e0b">
                                <span class="color-value" id="colorWarningValue">#f59e0b</span>
                            </div>
                            <div class="color-picker-group">
                                <label for="colorBgMain">Background Main</label>
                                <input type="color" id="colorBgMain" value="#f8fafc">
                                <span class="color-value" id="colorBgMainValue">#f8fafc</span>
                            </div>
                            <div class="color-picker-group">
                                <label for="colorBgCard">Background Card</label>
                                <input type="color" id="colorBgCard" value="#ffffff">
                                <span class="color-value" id="colorBgCardValue">#ffffff</span>
                            </div>
                        </div>
                    </fieldset>

                    <!-- Fontes -->
                    <fieldset class="form-section">
                        <legend>Fontes</legend>
                        <div class="form-row">
                            <label for="fontHeading">Fonte de Títulos</label>
                            <select id="fontHeading">
                                <option value="Barlow Condensed">Barlow Condensed</option>
                                <option value="DM Sans">DM Sans</option>
                                <option value="Inter">Inter</option>
                                <option value="Roboto">Roboto</option>
                                <option value="Open Sans">Open Sans</option>
                            </select>
                        </div>
                        <div class="form-row">
                            <label for="fontBody">Fonte de Texto</label>
                            <select id="fontBody">
                                <option value="DM Sans">DM Sans</option>
                                <option value="Barlow Condensed">Barlow Condensed</option>
                                <option value="Inter">Inter</option>
                                <option value="Roboto">Roboto</option>
                                <option value="Open Sans">Open Sans</option>
                            </select>
                        </div>
                    </fieldset>

                    <!-- Ícones -->
                    <fieldset class="form-section">
                        <legend>Biblioteca de Ícones</legend>
                        <div class="radio-group">
                            <label class="radio-label">
                                <input type="radio" name="iconLibrary" value="fontawesome" checked>
                                Font Awesome
                            </label>
                            <label class="radio-label">
                                <input type="radio" name="iconLibrary" value="lucide">
                                Lucide
                            </label>
                            <label class="radio-label">
                                <input type="radio" name="iconLibrary" value="material">
                                Material Icons
                            </label>
                        </div>
                    </fieldset>

                    <!-- Tokens Extras -->
                    <fieldset class="form-section">
                        <legend>Tokens Extras</legend>
                        <div class="form-row">
                            <label for="radiusMd">Border Radius (md)</label>
                            <input type="text" id="radiusMd" placeholder="0.5rem" value="0.5rem">
                        </div>
                        <div class="form-row">
                            <label for="radiusLg">Border Radius (lg)</label>
                            <input type="text" id="radiusLg" placeholder="0.75rem" value="0.75rem">
                        </div>
                    </fieldset>
                </form>

                <!-- Preview -->
                <div class="preview-section">
                    <h3>Preview</h3>
                    <div class="preview-card" id="previewCard">
                        <div class="preview-header">Título de Exemplo</div>
                        <div class="preview-body">
                            <p>Texto de exemplo para visualizar as cores e fontes.</p>
                            <button class="btn btn-primary">Botão Primary</button>
                            <button class="btn" style="background: var(--skin-danger); color: white;">Botão Danger</button>
                        </div>
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="btn" id="btnPreviewSkin" type="button">
                        <i class="fas fa-eye"></i> Preview
                    </button>
                    <button class="btn" id="btnResetSkin" type="button">
                        <i class="fas fa-undo"></i> Reset
                    </button>
                    <button class="btn btn-primary" id="btnSaveSkin" type="submit" form="skinForm">
                        <i class="fas fa-save"></i> Salvar
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="../../shared/app.js"></script>
    <script src="../../shared/skinLoader.js"></script>
    <script src="script.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create style.css**

Create `packages/frontend-webapp/modules/admin-skins/style.css`:

```css
.skins-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.skins-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
}

.skin-card {
    background: var(--skin-bg-card, #fff);
    border: 1px solid var(--skin-border-color, #e2e8f0);
    border-radius: var(--skin-radius-md, 0.5rem);
    padding: 1rem;
    box-shadow: var(--skin-shadow-card, 0 10px 25px rgba(0,0,0,0.1));
}

.skin-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.skin-card-name {
    font-weight: 600;
    font-size: 1rem;
}

.skin-card-badge {
    font-size: 0.7rem;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    background: var(--skin-primary, #00c2e0);
    color: white;
    text-transform: uppercase;
    font-weight: 600;
}

.skin-card-preview {
    height: 60px;
    border-radius: var(--skin-radius-sm, 0.25rem);
    margin-bottom: 0.75rem;
    display: flex;
    gap: 0.25rem;
    overflow: hidden;
}

.skin-card-preview span {
    flex: 1;
}

.skin-card-actions {
    display: flex;
    gap: 0.5rem;
}

.skin-card-actions .btn {
    flex: 1;
    font-size: 0.8rem;
    padding: 0.4rem;
}

/* Modal */
.skin-modal {
    max-width: 700px;
    max-height: 90vh;
    overflow-y: auto;
}

.skin-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.form-section {
    border: 1px solid var(--skin-border-color, #e2e8f0);
    border-radius: var(--skin-radius-md, 0.5rem);
    padding: 1rem;
}

.form-section legend {
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0 0.5rem;
    color: var(--skin-text-muted, #64748b);
}

.form-row {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    margin-bottom: 0.75rem;
}

.form-row label {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--skin-text-muted, #64748b);
}

.form-row input,
.form-row select {
    padding: 0.5rem;
    border: 1px solid var(--skin-border-color, #e2e8f0);
    border-radius: var(--skin-radius-sm, 0.25rem);
    font-size: 0.9rem;
    background: var(--skin-bg-main, #f8fafc);
    color: var(--skin-text-main, #1e293b);
}

.color-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.75rem;
}

.color-picker-group {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
}

.color-picker-group input[type="color"] {
    width: 50px;
    height: 50px;
    border: 2px solid var(--skin-border-color, #e2e8f0);
    border-radius: var(--skin-radius-sm, 0.25rem);
    cursor: pointer;
    padding: 0;
}

.color-value {
    font-size: 0.75rem;
    font-family: monospace;
    color: var(--skin-text-muted, #64748b);
}

.radio-group {
    display: flex;
    gap: 1rem;
}

.radio-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
}

.preview-section {
    margin-top: 1rem;
}

.preview-section h3 {
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
    color: var(--skin-text-muted, #64748b);
}

.preview-card {
    border: 1px solid var(--skin-border-color, #e2e8f0);
    border-radius: var(--skin-radius-md, 0.5rem);
    overflow: hidden;
}

.preview-header {
    padding: 0.75rem 1rem;
    background: var(--skin-primary, #00c2e0);
    color: white;
    font-weight: 600;
}

.preview-body {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
}
```

- [ ] **Step 3: Create script.js**

Create `packages/frontend-webapp/modules/admin-skins/script.js`:

```javascript
/**
 * ADMIN SKINS MODULE - GrindX
 * Gestão de skins/temas via módulo admin.
 */

class AdminSkinsController {
    constructor() {
        this.skins = [];
        this.editingSkinId = null;
        this.apiBase = grindx.config.API_BASE_URL;
        this.token = grindx.session.getToken();

        this.init();
    }

    async init() {
        this.setupEvents();
        await this.loadSkins();
    }

    setupEvents() {
        document.getElementById('btnNewSkin')?.addEventListener('click', () => this.openNewSkinModal());
        document.getElementById('btnCloseModal')?.addEventListener('click', () => this.closeModal());
        document.getElementById('btnSaveSkin')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.saveSkin();
        });
        document.getElementById('btnPreviewSkin')?.addEventListener('click', () => this.previewSkin());
        document.getElementById('btnResetSkin')?.addEventListener('click', () => this.resetPreview());

        // Color pickers live update
        ['colorPrimary', 'colorDanger', 'colorSuccess', 'colorWarning', 'colorBgMain', 'colorBgCard'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', (e) => {
                    document.getElementById(id + 'Value').textContent = e.target.value;
                    this.previewSkin();
                });
            }
        });

        // Font select live update
        ['fontHeading', 'fontBody'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('change', () => this.previewSkin());
            }
        });
    }

    async loadSkins() {
        try {
            const resp = await fetch(`${this.apiBase}/themes`, {
                headers: { Authorization: `Bearer ${this.token}` },
            });
            if (!resp.ok) throw new Error('Failed to load skins');
            this.skins = await resp.json();
            this.renderSkins();
        } catch (e) {
            console.error('Erro ao carregar skins:', e);
        }
    }

    renderSkins() {
        const grid = document.getElementById('skinsGrid');
        if (!grid) return;

        const cards = this.skins.map(skin => {
            const colors = skin.colors || {};
            const primary = colors['--skin-primary'] || '#00c2e0';
            const danger = colors['--skin-danger'] || '#ef4444';
            const success = colors['--skin-success'] || '#10b981';
            const bgMain = colors['--skin-bg-main'] || '#f8fafc';

            return `
                <div class="skin-card" data-id="${skin.id}">
                    <div class="skin-card-header">
                        <span class="skin-card-name">${skin.name}</span>
                        ${skin.is_active ? '<span class="skin-card-badge">Ativa</span>' : ''}
                    </div>
                    <div class="skin-card-preview">
                        <span style="background: ${primary}"></span>
                        <span style="background: ${danger}"></span>
                        <span style="background: ${success}"></span>
                        <span style="background: ${bgMain}; border: 1px solid #e2e8f0"></span>
                    </div>
                    <div class="skin-card-actions">
                        ${skin.is_active
                            ? '<button class="btn" disabled>Ativa</button>'
                            : `<button class="btn btn-primary" onclick="window.adminSkins.activateSkin(${skin.id})">Ativar</button>`
                        }
                        <button class="btn" onclick="window.adminSkins.editSkin(${skin.id})">Editar</button>
                        <button class="btn" style="background: var(--skin-danger); color: white;" onclick="window.adminSkins.deleteSkin(${skin.id})">Excluir</button>
                    </div>
                </div>
            `;
        }).join('');

        // Card para criar nova skin
        grid.innerHTML = cards + `
            <div class="skin-card" style="display: flex; align-items: center; justify-content: center; cursor: pointer; border-style: dashed;" onclick="window.adminSkins.openNewSkinModal()">
                <div style="text-align: center; color: var(--skin-text-muted);">
                    <i class="fas fa-plus" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                    <div>Criar Nova Skin</div>
                </div>
            </div>
        `;
    }

    openNewSkinModal() {
        this.editingSkinId = null;
        document.getElementById('modalTitle').textContent = 'Nova Skin';
        this.resetForm();
        this.openModal();
    }

    async editSkin(id) {
        const skin = this.skins.find(s => s.id === id);
        if (!skin) return;

        this.editingSkinId = id;
        document.getElementById('modalTitle').textContent = `Editar: ${skin.name}`;

        // Preencher formulário
        document.getElementById('skinName').value = skin.name || '';
        document.getElementById('companyName').value = skin.company_name || '';
        document.getElementById('copyrightText').value = skin.copyright_text || '';
        document.getElementById('logoUrl').value = skin.logo_url || '';
        document.getElementById('logoShortUrl').value = skin.logo_short_url || '';

        const colors = skin.colors || {};
        document.getElementById('colorPrimary').value = colors['--skin-primary'] || '#00c2e0';
        document.getElementById('colorPrimaryValue').textContent = colors['--skin-primary'] || '#00c2e0';
        document.getElementById('colorDanger').value = colors['--skin-danger'] || '#ef4444';
        document.getElementById('colorDangerValue').textContent = colors['--skin-danger'] || '#ef4444';
        document.getElementById('colorSuccess').value = colors['--skin-success'] || '#10b981';
        document.getElementById('colorSuccessValue').textContent = colors['--skin-success'] || '#10b981';
        document.getElementById('colorWarning').value = colors['--skin-warning'] || '#f59e0b';
        document.getElementById('colorWarningValue').textContent = colors['--skin-warning'] || '#f59e0b';
        document.getElementById('colorBgMain').value = colors['--skin-bg-main'] || '#f8fafc';
        document.getElementById('colorBgMainValue').textContent = colors['--skin-bg-main'] || '#f8fafc';
        document.getElementById('colorBgCard').value = colors['--skin-bg-card'] || '#ffffff';
        document.getElementById('colorBgCardValue').textContent = colors['--skin-bg-card'] || '#ffffff';

        const fonts = skin.fonts || {};
        document.getElementById('fontHeading').value = fonts.heading || 'Barlow Condensed';
        document.getElementById('fontBody').value = fonts.body || 'DM Sans';

        const iconRadio = document.querySelector(`input[name="iconLibrary"][value="${skin.icon_library || 'fontawesome'}"]`);
        if (iconRadio) iconRadio.checked = true;

        const tokens = skin.tokens || {};
        document.getElementById('radiusMd').value = tokens['--skin-radius-md'] || '0.5rem';
        document.getElementById('radiusLg').value = tokens['--skin-radius-lg'] || '0.75rem';

        this.openModal();
    }

    async saveSkin() {
        const name = document.getElementById('skinName').value.trim();
        if (!name) {
            alert('Nome da skin é obrigatório');
            return;
        }

        const data = {
            name,
            company_name: document.getElementById('companyName').value || null,
            copyright_text: document.getElementById('copyrightText').value || null,
            logo_url: document.getElementById('logoUrl').value || null,
            logo_short_url: document.getElementById('logoShortUrl').value || null,
            colors: {
                '--skin-primary': document.getElementById('colorPrimary').value,
                '--skin-danger': document.getElementById('colorDanger').value,
                '--skin-success': document.getElementById('colorSuccess').value,
                '--skin-warning': document.getElementById('colorWarning').value,
                '--skin-bg-main': document.getElementById('colorBgMain').value,
                '--skin-bg-card': document.getElementById('colorBgCard').value,
            },
            fonts: {
                heading: document.getElementById('fontHeading').value,
                body: document.getElementById('fontBody').value,
            },
            icon_library: document.querySelector('input[name="iconLibrary"]:checked')?.value || 'fontawesome',
            tokens: {
                '--skin-radius-md': document.getElementById('radiusMd').value,
                '--skin-radius-lg': document.getElementById('radiusLg').value,
            },
        };

        try {
            const url = this.editingSkinId
                ? `${this.apiBase}/themes/${this.editingSkinId}`
                : `${this.apiBase}/themes`;
            const method = this.editingSkinId ? 'PUT' : 'POST';

            const resp = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${this.token}`,
                },
                body: JSON.stringify(data),
            });

            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.detail || 'Erro ao salvar skin');
            }

            this.closeModal();
            await this.loadSkins();
        } catch (e) {
            console.error('Erro ao salvar skin:', e);
            alert(e.message);
        }
    }

    async activateSkin(id) {
        try {
            const resp = await fetch(`${this.apiBase}/themes/${id}/activate`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${this.token}` },
            });
            if (!resp.ok) throw new Error('Erro ao ativar skin');
            await this.loadSkins();
            // Recarregar skin atual
            const companyId = grindx.session.getUserProfile()?.empresa_id || window.dashboard?.user?.company_id;
            if (companyId && window.skinLoader) {
                window.skinLoader.reload(parseInt(companyId));
            }
        } catch (e) {
            console.error('Erro ao ativar skin:', e);
            alert(e.message);
        }
    }

    async deleteSkin(id) {
        if (!confirm('Tem certeza que deseja excluir esta skin?')) return;

        try {
            const resp = await fetch(`${this.apiBase}/themes/${id}`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${this.token}` },
            });
            if (!resp.ok) {
                const err = await resp.json();
                if (resp.status === 409) {
                    throw new Error('Não é possível excluir uma skin ativa. Desative-a primeiro.');
                }
                throw new Error(err.detail || 'Erro ao excluir skin');
            }
            await this.loadSkins();
        } catch (e) {
            console.error('Erro ao excluir skin:', e);
            alert(e.message);
        }
    }

    previewSkin() {
        const colors = {
            '--skin-primary': document.getElementById('colorPrimary').value,
            '--skin-danger': document.getElementById('colorDanger').value,
            '--skin-success': document.getElementById('colorSuccess').value,
            '--skin-warning': document.getElementById('colorWarning').value,
            '--skin-bg-main': document.getElementById('colorBgMain').value,
            '--skin-bg-card': document.getElementById('colorBgCard').value,
        };

        if (window.skinLoader) {
            window.skinLoader.applyPreviewColors(colors);
        }

        // Atualizar preview card
        const previewCard = document.getElementById('previewCard');
        if (previewCard) {
            previewCard.style.background = colors['--skin-bg-card'];
            previewCard.style.borderColor = colors['--skin-border-color'] || '#e2e8f0';
            const header = previewCard.querySelector('.preview-header');
            if (header) header.style.background = colors['--skin-primary'];
        }
    }

    resetPreview() {
        if (window.skinLoader) {
            window.skinLoader.resetToDefaults();
        }
        document.getElementById('colorPrimary').value = '#00c2e0';
        document.getElementById('colorPrimaryValue').textContent = '#00c2e0';
        document.getElementById('colorDanger').value = '#ef4444';
        document.getElementById('colorDangerValue').textContent = '#ef4444';
        document.getElementById('colorSuccess').value = '#10b981';
        document.getElementById('colorSuccessValue').textContent = '#10b981';
        document.getElementById('colorWarning').value = '#f59e0b';
        document.getElementById('colorWarningValue').textContent = '#f59e0b';
        document.getElementById('colorBgMain').value = '#f8fafc';
        document.getElementById('colorBgMainValue').textContent = '#f8fafc';
        document.getElementById('colorBgCard').value = '#ffffff';
        document.getElementById('colorBgCardValue').textContent = '#ffffff';
    }

    resetForm() {
        document.getElementById('skinName').value = '';
        document.getElementById('companyName').value = '';
        document.getElementById('copyrightText').value = '';
        document.getElementById('logoUrl').value = '';
        document.getElementById('logoShortUrl').value = '';
        this.resetPreview();
        document.getElementById('fontHeading').value = 'Barlow Condensed';
        document.getElementById('fontBody').value = 'DM Sans';
        document.querySelector('input[name="iconLibrary"][value="fontawesome"]').checked = true;
        document.getElementById('radiusMd').value = '0.5rem';
        document.getElementById('radiusLg').value = '0.75rem';
    }

    openModal() {
        document.getElementById('skinModal').style.display = 'flex';
    }

    closeModal() {
        document.getElementById('skinModal').style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.adminSkins = new AdminSkinsController();
});
```

- [ ] **Step 4: Commit**

```bash
git add packages/frontend-webapp/modules/admin-skins/
git commit -m "feat(skin): add admin-skins module with CRUD UI"
```

---

### Task 11: Register admin-skins module in dynamic menu

**Files:**
- Modify: `packages/api-postgres/seed.py` (add admin-skins module to portal)

- [ ] **Step 1: Add admin-skins module to seed data**

Add to the seed data in `packages/api-postgres/seed.py`, in the "Gestão" aba section:

```python
# Módulo de gestão de skins
admin_skins = Modulo(
    aba_id=gestao_aba.id,
    nome="Skins",
    slug="admin-skins",
    url="modules/admin-skins/index.html",
    icone="fas fa-palette",
    role_minima="admin",
    ativo=True,
)
db.add(admin_skins)
```

- [ ] **Step 2: Commit**

```bash
git add packages/api-postgres/seed.py
git commit -m "feat(skin): register admin-skins module in portal seed data"
```

---

### Task 12: Run all tests and verify

- [ ] **Step 1: Run all backend tests**

Run: `cd packages/api-postgres && pytest -v`
Expected: ALL PASS

- [ ] **Step 2: Run root tests**

Run: `pytest -v`
Expected: ALL PASS

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat(skin): complete skin system implementation"
```

---

## Spec Coverage Checklist

| Spec Section | Task | Status |
|--------------|------|--------|
| Data Model (company_themes) | Task 1 | Covered |
| JWT company_id | Task 2 | Covered |
| Alembic Migration | Task 3 | Covered |
| Theme Repository | Task 4 | Covered |
| Theme Service | Task 5 | Covered |
| API Endpoints | Task 6 | Covered |
| CSS Architecture (skin tokens + aliases) | Task 7 | Covered |
| skinLoader.js Runtime | Task 8 | Covered |
| Login/Dashboard Integration | Task 9 | Covered |
| Admin Module UI | Task 10 | Covered |
| Dynamic Menu Registration | Task 11 | Covered |
| localStorage persistence for login skin | Task 9 | Covered |
| Error Handling | Tasks 4, 5, 6 | Covered |
| Testing | Tasks 1-6, 12 | Covered |
| Security (RBAC on endpoints) | Task 6 | Covered |

## Placeholder Scan

No placeholders found. All code is complete. All paths are exact. All tests have actual code.

## Type Consistency

- `company_id` is `int` throughout (model, schema, JWT payload, repository, service, router)
- `ThemeResponse` schema matches `_to_dict()` output from service
- All endpoints use `require_role("admin")` for CRUD, `get_current_user` for `/active`
- CSS variable naming consistent: `--skin-*` for tokens, semantic aliases unchanged
