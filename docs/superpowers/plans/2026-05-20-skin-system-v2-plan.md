# Skin System v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance the skin system with theme history tracking, logo upload, skin templates, advanced admin UI with expanded preview, auto dark mode, test button, and localStorage caching.

**Architecture:** Backend adds ThemeHistory model + endpoints for history/upload/templates. Frontend admin UI gets advanced mode toggle, color text inputs, expanded mini-dashboard preview, template picker. skinLoader.js gets localStorage cache. Dashboard gets skin_preview query param handling.

**Tech Stack:** FastAPI, SQLAlchemy, PostgreSQL, Alembic, Vanilla JS, CSS Custom Properties, Font Awesome

---

### Task 1: Theme History Model + Migration

**Files:**
- Create: `packages/api-postgres/app/models/theme_history.py`
- Modify: `packages/api-postgres/app/models/__init__.py`
- Create: `packages/api-postgres/alembic/versions/004_add_theme_history.py`
- Test: `packages/api-postgres/tests/unit/test_models_theme_history.py`

- [ ] **Step 1: Write the failing test**

Create `packages/api-postgres/tests/unit/test_models_theme_history.py`:

```python
"""Testes unitários para o modelo ThemeHistory."""

import pytest
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.theme import CompanyTheme
from app.models.theme_history import ThemeHistory


def test_create_theme_history(db_session: Session):
    """Testa criação de registro de histórico."""
    empresa = Empresa(nome="Test Corp", dominio="test.com")
    db_session.add(empresa)
    db_session.commit()

    theme = CompanyTheme(company_id=empresa.id, name="Test Theme", icon_library="fontawesome")
    db_session.add(theme)
    db_session.commit()

    history = ThemeHistory(theme_id=theme.id, action="create", snapshot={})
    db_session.add(history)
    db_session.commit()
    db_session.refresh(history)

    assert history.id is not None
    assert history.theme_id == theme.id
    assert history.action == "create"
    assert history.snapshot == {}
    assert history.changed_at is not None


def test_history_cascade_on_theme_delete(db_session: Session):
    """Testa que histórico é deletado quando tema é deletado."""
    empresa = Empresa(nome="Cascade Corp", dominio="cascade.com")
    db_session.add(empresa)
    db_session.commit()

    theme = CompanyTheme(company_id=empresa.id, name="To Delete", icon_library="fontawesome")
    db_session.add(theme)
    db_session.commit()

    history = ThemeHistory(theme_id=theme.id, action="create", snapshot={})
    db_session.add(history)
    db_session.commit()

    db_session.delete(theme)
    db_session.commit()

    result = db_session.query(ThemeHistory).filter_by(theme_id=theme.id).first()
    assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd packages/api-postgres && pytest tests/unit/test_models_theme_history.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.models.theme_history'"

- [ ] **Step 3: Write model**

Create `packages/api-postgres/app/models/theme_history.py`:

```python
"""
Modelo SQLAlchemy para histórico de alterações de temas.

Tabela: theme_history (PostgreSQL)
Registra cada alteração feita em temas/skins.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ThemeHistory(Base):
    """Mapeamento da tabela 'theme_history' no PostgreSQL."""

    __tablename__ = "theme_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    theme_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("company_themes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Tipo da ação: create/update/delete/activate"
    )
    snapshot: Mapped[dict | None] = mapped_column(
        "snapshot", nullable=True, comment="Estado do tema antes da mudança"
    )
    changed_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, comment="Usuário que fez a mudança"
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ThemeHistory(id={self.id}, theme_id={self.theme_id}, action='{self.action}')>"
```

Modify `packages/api-postgres/app/models/__init__.py` — add line after CompanyTheme import:

```python
from app.models.theme_history import ThemeHistory  # noqa: F401
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd packages/api-postgres && pytest tests/unit/test_models_theme_history.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Create migration**

Create `packages/api-postgres/alembic/versions/004_add_theme_history.py`:

```python
"""add theme_history table

Revision ID: 004_add_theme_history
Revises: 003_add_empresa_and_theme
Create Date: 2026-05-20 18:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "004_add_theme_history"
down_revision = "003_add_empresa_and_theme"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "theme_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("theme_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=True),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["theme_id"], ["company_themes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_theme_history_theme_id", "theme_history", ["theme_id"])


def downgrade() -> None:
    op.drop_index("ix_theme_history_theme_id", table_name="theme_history")
    op.drop_table("theme_history")
```

- [ ] **Step 6: Commit**

```bash
git add packages/api-postgres/app/models/theme_history.py packages/api-postgres/app/models/__init__.py packages/api-postgres/alembic/versions/004_add_theme_history.py packages/api-postgres/tests/unit/test_models_theme_history.py
git commit -m "feat(skin-v2): add ThemeHistory model and migration"
```

---

### Task 2: Theme Service — History Logging

**Files:**
- Modify: `packages/api-postgres/app/services/theme_service.py`
- Test: `packages/api-postgres/tests/unit/test_theme_service.py` (append tests)

- [ ] **Step 1: Write failing tests**

Append to `packages/api-postgres/tests/unit/test_theme_service.py`:

```python
def test_create_theme_logs_history(theme_service: ThemeService, empresa: Empresa):
    """Testa que criar tema registra histórico."""
    theme_service.create_theme(company_id=empresa.id, name="History Test", icon_library="fontawesome")

    from app.models.theme_history import ThemeHistory

    history = theme_service.repo.db.query(ThemeHistory).filter_by(action="create").first()
    assert history is not None
    assert history.action == "create"


def test_update_theme_logs_history(theme_service: ThemeService, empresa: Empresa):
    """Testa que atualizar tema registra histórico com snapshot anterior."""
    created = theme_service.create_theme(company_id=empresa.id, name="Old", icon_library="fontawesome")
    theme_service.update_theme(created["id"], company_id=empresa.id, name="New")

    from app.models.theme_history import ThemeHistory

    history = theme_service.repo.db.query(ThemeHistory).filter_by(action="update").first()
    assert history is not None
    assert history.snapshot["name"] == "Old"


def test_activate_theme_logs_history(theme_service: ThemeService, empresa: Empresa):
    """Testa que ativar tema registra histórico."""
    created = theme_service.create_theme(company_id=empresa.id, name="Activate Test", icon_library="fontawesome")
    theme_service.activate_theme(created["id"], empresa.id)

    from app.models.theme_history import ThemeHistory

    history = theme_service.repo.db.query(ThemeHistory).filter_by(action="activate").first()
    assert history is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd packages/api-postgres && pytest tests/unit/test_theme_service.py -v -k history`
Expected: FAIL (history records not found)

- [ ] **Step 3: Modify ThemeService**

In `packages/api-postgres/app/services/theme_service.py`, add import at top:

```python
from app.models.theme_history import ThemeHistory
```

In `create_theme`, after `theme = self.repo.create(theme)`, add:

```python
        self._log_history(theme.id, "create", {})
```

In `update_theme`, add before `theme = self.repo.update(theme, **kwargs)`:

```python
        snapshot_before = self._to_dict(theme)
```

After `theme = self.repo.update(theme, **kwargs)`, add:

```python
        self._log_history(theme.id, "update", snapshot_before)
```

In `activate_theme`, after `theme = self.repo.activate_theme(theme_id, company_id)`, add:

```python
        self._log_history(theme.id, "activate", self._to_dict(theme))
```

Add new method to ThemeService class (before `_to_dict`):

```python
    def _log_history(self, theme_id: int, action: str, snapshot: dict) -> None:
        """Registra uma entrada no histórico de alterações do tema."""
        entry = ThemeHistory(theme_id=theme_id, action=action, snapshot=snapshot)
        self.repo.db.add(entry)
        self.repo.db.commit()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd packages/api-postgres && pytest tests/unit/test_theme_service.py -v`
Expected: PASS (10 tests)

- [ ] **Step 5: Commit**

```bash
git add packages/api-postgres/app/services/theme_service.py packages/api-postgres/tests/unit/test_theme_service.py
git commit -m "feat(skin-v2): add history logging to ThemeService CRUD operations"
```

---

### Task 3: Theme History Endpoint

**Files:**
- Modify: `packages/api-postgres/app/routers/theme_router.py`
- Modify: `packages/api-postgres/app/services/theme_service.py`
- Test: `packages/api-postgres/tests/integration/test_theme_router.py` (append)

- [ ] **Step 1: Write failing tests**

Append to `packages/api-postgres/tests/integration/test_theme_router.py`:

```python
def test_get_theme_history(client: TestClient, admin_auth_headers: dict):
    """Testa busca do histórico de um tema."""
    create_resp = client.post(
        "/v1/themes",
        json={"name": "History Theme", "icon_library": "fontawesome"},
        headers=admin_auth_headers,
    )
    theme_id = create_resp.json()["id"]

    client.put(f"/v1/themes/{theme_id}", json={"name": "Updated Name"}, headers=admin_auth_headers)

    resp = client.get(f"/v1/themes/{theme_id}/history", headers=admin_auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 2
    actions = [h["action"] for h in resp.json()]
    assert "create" in actions
    assert "update" in actions


def test_get_theme_history_not_found(client: TestClient, admin_auth_headers: dict):
    """Testa que retorna 404 para histórico de tema inexistente."""
    resp = client.get("/v1/themes/99999/history", headers=admin_auth_headers)
    assert resp.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd packages/api-postgres && pytest tests/integration/test_theme_router.py::test_get_theme_history -v`
Expected: FAIL (404)

- [ ] **Step 3: Add service method**

Add to `packages/api-postgres/app/services/theme_service.py`:

```python
    def get_theme_history(self, theme_id: int, company_id: int) -> list[dict]:
        """Retorna histórico de alterações de um tema."""
        theme = self.repo.find_by_id(theme_id)
        if theme is None:
            raise NotFoundError(f"Tema {theme_id} não encontrado")
        if theme.company_id != company_id:
            raise NotFoundError(f"Tema {theme_id} não pertence à empresa {company_id}")

        entries = (
            self.repo.db.query(ThemeHistory)
            .filter(ThemeHistory.theme_id == theme_id)
            .order_by(ThemeHistory.changed_at.desc())
            .all()
        )
        return [
            {
                "id": e.id,
                "theme_id": e.theme_id,
                "action": e.action,
                "snapshot": e.snapshot,
                "changed_by": e.changed_by,
                "changed_at": e.changed_at.isoformat() if e.changed_at else None,
            }
            for e in entries
        ]
```

- [ ] **Step 4: Add endpoint**

Add to `packages/api-postgres/app/routers/theme_router.py`:

```python
@router.get(
    "/{theme_id}/history",
    summary="Histórico do tema",
    description="Retorna o histórico de alterações de um tema. Requer role admin.",
    responses={404: {"model": ErrorResponse, "description": "Tema não encontrado"}},
)
def get_theme_history(
    theme_id: int,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> list[dict]:
    """Retorna histórico de alterações do tema."""
    company_id = _require_company_id(current_user)
    return service.get_theme_history(theme_id, company_id)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd packages/api-postgres && pytest tests/integration/test_theme_router.py -v`
Expected: PASS (7 tests)

- [ ] **Step 6: Commit**

```bash
git add packages/api-postgres/app/routers/theme_router.py packages/api-postgres/app/services/theme_service.py packages/api-postgres/tests/integration/test_theme_router.py
git commit -m "feat(skin-v2): add GET /themes/{id}/history endpoint"
```

---

### Task 4: Logo Upload Endpoint

**Files:**
- Create: `packages/api-postgres/static/uploads/logos/.gitkeep`
- Modify: `packages/api-postgres/app/routers/theme_router.py`
- Modify: `packages/api-postgres/app/main.py`
- Test: `packages/api-postgres/tests/integration/test_theme_router.py` (append)

- [ ] **Step 1: Create directory**

Create `packages/api-postgres/static/uploads/logos/.gitkeep` (empty file).

- [ ] **Step 2: Mount static files in main.py**

Add to imports in `packages/api-postgres/app/main.py`:

```python
from fastapi.staticfiles import StaticFiles
from pathlib import Path
```

After `app.include_router(theme_router)`:

```python
# Static files for uploads
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
```

- [ ] **Step 3: Write failing test**

Append to `packages/api-postgres/tests/integration/test_theme_router.py`:

```python
import io

def test_upload_logo(client: TestClient, admin_auth_headers: dict, empresa: Empresa, db_session):
    """Testa upload de logo para um tema."""
    from app.models.theme import CompanyTheme

    theme = CompanyTheme(company_id=empresa.id, name="Logo Test", icon_library="fontawesome")
    db_session.add(theme)
    db_session.commit()

    file_content = io.BytesIO(b"fake png content")
    file_content.name = "test-logo.png"

    resp = client.post(
        f"/v1/themes/{theme.id}/upload-logo",
        files={"file": ("test-logo.png", file_content, "image/png")},
        headers=admin_auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "url" in data
    assert "test-logo" in data["url"]

    db_session.refresh(theme)
    assert theme.logo_url is not None
```

- [ ] **Step 4: Run test to verify it fails**

Run: `cd packages/api-postgres && pytest tests/integration/test_theme_router.py::test_upload_logo -v`
Expected: FAIL (404)

- [ ] **Step 5: Write upload endpoint**

Add imports to `packages/api-postgres/app/routers/theme_router.py`:

```python
import uuid
from pathlib import Path as PyPath
from fastapi import UploadFile, File
```

Add constants after existing ones:

```python
UPLOAD_DIR = PyPath(__file__).parent.parent.parent / "static" / "uploads" / "logos"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
```

Add endpoint:

```python
@router.post(
    "/{theme_id}/upload-logo",
    summary="Upload de logo",
    description="Faz upload de uma imagem de logo para o tema. Requer role admin.",
    responses={
        400: {"model": ErrorResponse, "description": "Arquivo inválido"},
        404: {"model": ErrorResponse, "description": "Tema não encontrado"},
    },
)
def upload_logo(
    theme_id: int,
    file: UploadFile = File(...),
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Faz upload de logo para o tema."""
    company_id = _require_company_id(current_user)

    theme = service.get_theme_by_id(theme_id)
    if theme is None or theme["company_id"] != company_id:
        raise HTTPException(status_code=404, detail="Tema não encontrado")

    ext = PyPath(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Tipo não permitido. Aceitos: {', '.join(ALLOWED_EXTENSIONS)}")

    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"Arquivo muito grande. Máximo: {MAX_FILE_SIZE // (1024*1024)}MB")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    unique_name = f"{theme_id}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = UPLOAD_DIR / unique_name
    file_path.write_bytes(content)

    logo_url = f"/static/uploads/logos/{unique_name}"
    service.update_theme(theme_id, company_id=company_id, logo_url=logo_url)

    return {"url": logo_url}
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd packages/api-postgres && pytest tests/integration/test_theme_router.py::test_upload_logo -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add packages/api-postgres/app/routers/theme_router.py packages/api-postgres/app/main.py packages/api-postgres/static/uploads/logos/.gitkeep packages/api-postgres/tests/integration/test_theme_router.py
git commit -m "feat(skin-v2): add logo upload endpoint with validation"
```

---

### Task 5: Skin Templates (Backend)

**Files:**
- Create: `packages/api-postgres/app/data/skin-templates/corporate-blue.json`
- Create: `packages/api-postgres/app/data/skin-templates/dark-minimal.json`
- Create: `packages/api-postgres/app/data/skin-templates/warm-earth.json`
- Create: `packages/api-postgres/app/data/skin-templates/forest-green.json`
- Create: `packages/api-postgres/app/data/skin-templates/sunset-orange.json`
- Modify: `packages/api-postgres/app/routers/theme_router.py`
- Test: `packages/api-postgres/tests/integration/test_theme_router.py` (append)

- [ ] **Step 1: Create template files**

Create `packages/api-postgres/app/data/skin-templates/corporate-blue.json`:

```json
{
  "name": "Corporate Blue",
  "colors": {
    "--skin-primary": "#2563eb",
    "--skin-primary-hover": "#1d4ed8",
    "--skin-danger": "#dc2626",
    "--skin-success": "#16a34a",
    "--skin-warning": "#d97706",
    "--skin-bg-main": "#f1f5f9",
    "--skin-bg-card": "#ffffff",
    "--skin-text-main": "#0f172a",
    "--skin-text-muted": "#64748b",
    "--skin-border-color": "#cbd5e1",
    "--skin-focus-ring": "rgba(37, 99, 235, 0.35)"
  },
  "fonts": { "heading": "Inter", "body": "Inter" },
  "icon_library": "fontawesome",
  "tokens": {
    "--skin-radius-sm": "0.25rem",
    "--skin-radius-md": "0.5rem",
    "--skin-radius-lg": "0.75rem",
    "--skin-radius-xl": "1rem",
    "--skin-shadow-card": "0 4px 6px rgba(0,0,0,0.07)",
    "--skin-shadow-modal": "0 20px 25px -5px rgba(0,0,0,0.15)"
  }
}
```

Create `packages/api-postgres/app/data/skin-templates/dark-minimal.json`:

```json
{
  "name": "Dark Minimal",
  "colors": {
    "--skin-primary": "#818cf8",
    "--skin-primary-hover": "#6366f1",
    "--skin-danger": "#f87171",
    "--skin-success": "#34d399",
    "--skin-warning": "#fbbf24",
    "--skin-bg-main": "#0f172a",
    "--skin-bg-card": "#1e293b",
    "--skin-text-main": "#f1f5f9",
    "--skin-text-muted": "#94a3b8",
    "--skin-border-color": "#334155",
    "--skin-focus-ring": "rgba(129, 140, 248, 0.35)"
  },
  "fonts": { "heading": "Inter", "body": "DM Sans" },
  "icon_library": "fontawesome",
  "tokens": {
    "--skin-radius-sm": "0.25rem",
    "--skin-radius-md": "0.375rem",
    "--skin-radius-lg": "0.5rem",
    "--skin-radius-xl": "0.75rem",
    "--skin-shadow-card": "0 4px 6px rgba(0,0,0,0.3)",
    "--skin-shadow-modal": "0 20px 25px rgba(0,0,0,0.5)"
  }
}
```

Create `packages/api-postgres/app/data/skin-templates/warm-earth.json`:

```json
{
  "name": "Warm Earth",
  "colors": {
    "--skin-primary": "#b45309",
    "--skin-primary-hover": "#92400e",
    "--skin-danger": "#dc2626",
    "--skin-success": "#65a30d",
    "--skin-warning": "#d97706",
    "--skin-bg-main": "#fef3c7",
    "--skin-bg-card": "#fffbeb",
    "--skin-text-main": "#451a03",
    "--skin-text-muted": "#92400e",
    "--skin-border-color": "#fcd34d",
    "--skin-focus-ring": "rgba(180, 83, 9, 0.35)"
  },
  "fonts": { "heading": "Barlow Condensed", "body": "Open Sans" },
  "icon_library": "fontawesome",
  "tokens": {
    "--skin-radius-sm": "0.375rem",
    "--skin-radius-md": "0.625rem",
    "--skin-radius-lg": "1rem",
    "--skin-radius-xl": "1.5rem",
    "--skin-shadow-card": "0 8px 20px rgba(180, 83, 9, 0.1)",
    "--skin-shadow-modal": "0 20px 25px rgba(180, 83, 9, 0.15)"
  }
}
```

Create `packages/api-postgres/app/data/skin-templates/forest-green.json`:

```json
{
  "name": "Forest Green",
  "colors": {
    "--skin-primary": "#059669",
    "--skin-primary-hover": "#047857",
    "--skin-danger": "#ef4444",
    "--skin-success": "#10b981",
    "--skin-warning": "#f59e0b",
    "--skin-bg-main": "#ecfdf5",
    "--skin-bg-card": "#ffffff",
    "--skin-text-main": "#064e3b",
    "--skin-text-muted": "#065f46",
    "--skin-border-color": "#a7f3d0",
    "--skin-focus-ring": "rgba(5, 150, 105, 0.35)"
  },
  "fonts": { "heading": "Barlow Condensed", "body": "DM Sans" },
  "icon_library": "fontawesome",
  "tokens": {
    "--skin-radius-sm": "0.25rem",
    "--skin-radius-md": "0.5rem",
    "--skin-radius-lg": "0.75rem",
    "--skin-radius-xl": "1.25rem",
    "--skin-shadow-card": "0 6px 16px rgba(5, 150, 105, 0.08)",
    "--skin-shadow-modal": "0 20px 25px rgba(5, 150, 105, 0.12)"
  }
}
```

Create `packages/api-postgres/app/data/skin-templates/sunset-orange.json`:

```json
{
  "name": "Sunset Orange",
  "colors": {
    "--skin-primary": "#ea580c",
    "--skin-primary-hover": "#c2410c",
    "--skin-danger": "#ef4444",
    "--skin-success": "#22c55e",
    "--skin-warning": "#f59e0b",
    "--skin-bg-main": "#fff7ed",
    "--skin-bg-card": "#ffffff",
    "--skin-text-main": "#431407",
    "--skin-text-muted": "#9a3412",
    "--skin-border-color": "#fed7aa",
    "--skin-focus-ring": "rgba(234, 88, 12, 0.35)"
  },
  "fonts": { "heading": "Barlow Condensed", "body": "DM Sans" },
  "icon_library": "fontawesome",
  "tokens": {
    "--skin-radius-sm": "0.25rem",
    "--skin-radius-md": "0.5rem",
    "--skin-radius-lg": "0.75rem",
    "--skin-radius-xl": "1.5rem",
    "--skin-shadow-card": "0 8px 20px rgba(234, 88, 12, 0.1)",
    "--skin-shadow-modal": "0 20px 25px rgba(234, 88, 12, 0.15)"
  }
}
```

- [ ] **Step 2: Write failing tests**

Append to `packages/api-postgres/tests/integration/test_theme_router.py`:

```python
def test_list_templates(client: TestClient, admin_auth_headers: dict):
    """Testa listagem de templates disponíveis."""
    resp = client.get("/v1/themes/templates", headers=admin_auth_headers)
    assert resp.status_code == 200
    templates = resp.json()
    assert len(templates) >= 5
    slugs = [t["slug"] for t in templates]
    assert "corporate-blue" in slugs
    assert "dark-minimal" in slugs


def test_create_from_template(client: TestClient, admin_auth_headers: dict):
    """Testa criação de tema a partir de template."""
    resp = client.post(
        "/v1/themes/from-template",
        json={"template_slug": "corporate-blue", "name": "My Blue Theme"},
        headers=admin_auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Blue Theme"
    assert data["colors"]["--skin-primary"] == "#2563eb"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd packages/api-postgres && pytest tests/integration/test_theme_router.py -v -k template`
Expected: FAIL (endpoints don't exist)

- [ ] **Step 4: Write template endpoints**

Add import to `packages/api-postgres/app/routers/theme_router.py`:

```python
import json
```

Add constant:

```python
TEMPLATES_DIR = PyPath(__file__).parent.parent / "data" / "skin-templates"
```

Add endpoints:

```python
@router.get(
    "/templates",
    summary="Listar templates",
    description="Lista todos os templates de skin disponíveis.",
)
def list_templates(current_user=Depends(get_current_user)) -> list[dict]:
    """Lista templates disponíveis."""
    if not TEMPLATES_DIR.exists():
        return []
    templates = []
    for f in sorted(TEMPLATES_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            colors = data.get("colors", {})
            templates.append({
                "slug": f.stem,
                "name": data.get("name", f.stem),
                "preview": {
                    "primary": colors.get("--skin-primary", "#00c2e0"),
                    "bg": colors.get("--skin-bg-main", "#f8fafc"),
                },
            })
        except (json.JSONDecodeError, OSError):
            continue
    return templates


@router.post(
    "/from-template",
    response_model=ThemeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tema de template",
    description="Cria um novo tema a partir de um template. Requer role admin.",
    responses={404: {"model": ErrorResponse, "description": "Template não encontrado"}},
)
def create_from_template(
    dados: dict,
    current_user=Depends(require_role("admin")),
    service: ThemeService = Depends(_get_theme_service),
) -> dict:
    """Cria tema a partir de template."""
    company_id = _require_company_id(current_user)
    template_slug = dados.get("template_slug")
    name = dados.get("name", template_slug)

    if not template_slug:
        raise HTTPException(status_code=400, detail="template_slug é obrigatório")

    template_path = TEMPLATES_DIR / f"{template_slug}.json"
    if not template_path.exists():
        raise HTTPException(status_code=404, detail=f"Template '{template_slug}' não encontrado")

    try:
        template = json.loads(template_path.read_text())
    except (json.JSONDecodeError, OSError):
        raise HTTPException(status_code=500, detail="Erro ao ler template")

    return service.create_theme(
        company_id=company_id,
        name=name,
        colors=template.get("colors"),
        fonts=template.get("fonts"),
        icon_library=template.get("icon_library", "fontawesome"),
        tokens=template.get("tokens"),
    )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd packages/api-postgres && pytest tests/integration/test_theme_router.py -v`
Expected: PASS (9 tests)

- [ ] **Step 6: Commit**

```bash
git add packages/api-postgres/app/data/skin-templates/*.json packages/api-postgres/app/routers/theme_router.py packages/api-postgres/tests/integration/test_theme_router.py
git commit -m "feat(skin-v2): add skin templates backend with 5 presets"
```

---

### Task 6: skinLoader.js — localStorage Cache

**Files:**
- Modify: `packages/frontend-webapp/shared/skinLoader.js`

- [ ] **Step 1: Replace skinLoader.js**

Replace the entire file with the v2 version. Key changes from v1:
- Add `CACHE_TTL = 5 * 60 * 1000` constant
- In `load()`: check cache first → apply immediately → fetch API in background → re-apply if different → update cache
- Add `_getCache(companyId)`, `_setCache(companyId, data)`, `_clearCache(companyId)` methods
- Add `_applySkin(skin)` method (extracted from load)
- Add `loadForPreview(themeId)` method for preview mode
- Add `reload(companyId)` that clears cache before loading

Full file content is in the spec at `docs/superpowers/specs/2026-05-20-skin-system-v2-design.md` Section 3.3 for cache format and Section 3.2 for loadForPreview.

- [ ] **Step 2: Commit**

```bash
git add packages/frontend-webapp/shared/skinLoader.js
git commit -m "feat(skin-v2): add localStorage cache to skinLoader with 5min TTL"
```

---

### Task 7: Dashboard — skin_preview Query Param + Banner

**Files:**
- Modify: `packages/frontend-webapp/dashboard.html`
- Modify: `packages/frontend-webapp/dashboard.js`

- [ ] **Step 1: Add banner to dashboard.html**

Add after `<main class="main-viewport">` opening tag:

```html
     <!-- Preview Banner (skin_preview mode) -->
     <div id="previewBanner" style="display:none; background: var(--skin-primary, #00c2e0); color: white; padding: 0.5rem 1rem; text-align: center; font-size: 0.85rem;">
         <span id="previewBannerText"></span>
         <button id="btnApplyPreview" class="btn" style="background: white; color: var(--skin-primary, #00c2e0); margin: 0 0.25rem; padding: 0.15rem 0.5rem; font-size: 0.8rem;">Aplicar Permanentemente</button>
         <button id="btnClosePreview" class="btn" style="background: rgba(255,255,255,0.2); color: white; margin: 0 0.25rem; padding: 0.15rem 0.5rem; font-size: 0.8rem;">Fechar Preview</button>
     </div>
```

- [ ] **Step 2: Add preview mode to dashboard.js**

Add to `DashboardController.init()` after `this.loadCompanySkin()`:

```javascript
        this.checkPreviewMode();
```

Add new method:

```javascript
    checkPreviewMode() {
        const params = new URLSearchParams(window.location.search);
        const previewId = params.get('skin_preview');
        if (!previewId || !window.skinLoader) return;

        const banner = document.getElementById('previewBanner');
        const bannerText = document.getElementById('previewBannerText');
        if (!banner) return;

        window.skinLoader.loadForPreview(parseInt(previewId)).then(() => {
            const skin = window.skinLoader.currentSkin;
            if (skin) {
                bannerText.textContent = `Preview da skin '${skin.name}' — `;
                banner.style.display = 'block';
                this._previewThemeId = parseInt(previewId);
            }
        });

        document.getElementById('btnApplyPreview')?.addEventListener('click', () => {
            if (this._previewThemeId) {
                const token = window.grindx.session.getToken();
                fetch(`${window.grindx.config.API_BASE_URL}/themes/${this._previewThemeId}/activate`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${token}` },
                }).then(() => window.location.reload());
            }
        });

        document.getElementById('btnClosePreview')?.addEventListener('click', () => {
            window.close();
        });
    }
```

- [ ] **Step 3: Commit**

```bash
git add packages/frontend-webapp/dashboard.html packages/frontend-webapp/dashboard.js
git commit -m "feat(skin-v2): add skin_preview query param mode with apply/close banner"
```

---

### Task 8: Admin UI v2 — Full Rewrite

**Files:**
- Modify: `packages/frontend-webapp/modules/admin-skins/index.html`
- Modify: `packages/frontend-webapp/modules/admin-skins/style.css`
- Modify: `packages/frontend-webapp/modules/admin-skins/script.js`

- [ ] **Step 1: Replace all 3 files**

Replace all three files with the v2 versions from the spec. Key changes:
- **index.html**: Advanced mode toggle, color fields generated via JS, expanded preview dashboard, template modal, upload button
- **style.css**: New styles for advanced toggle, color picker rows, preview dashboard (sidebar, stats, table, badges), template grid
- **script.js**: Color field arrays (BASIC/ADVANCED/DARK), dynamic rendering, hex validation + text sync, auto dark mode generator, template apply, test button, logo upload via file input

The full file contents are in the spec document. Each file should be replaced entirely.

- [ ] **Step 2: Commit**

```bash
git add packages/frontend-webapp/modules/admin-skins/
git commit -m "feat(skin-v2): admin UI v2 — advanced mode, color text inputs, expanded preview, templates, test button, logo upload"
```

---

### Task 9: Final Verification

- [ ] **Step 1: Run all backend tests**

Run: `cd packages/api-postgres && pytest -v`
Expected: ALL PASS

- [ ] **Step 2: Verify Python syntax**

Run: `cd packages/api-postgres && python -m py_compile app/routers/theme_router.py app/services/theme_service.py app/models/theme_history.py`
Expected: No errors

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat(skin-v2): complete implementation"
```
