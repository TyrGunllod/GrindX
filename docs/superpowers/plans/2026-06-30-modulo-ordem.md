# Módulo Ordem — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `ordem` field to modules for ordering within each tab.

**Architecture:** Follow the exact pattern of `Aba.ordem` — add an integer column with default=0, expose in API schema and CRUD, add frontend field in structure module. Migration backfills existing modules with ordem = id.

**Tech Stack:** SQLAlchemy, Alembic, FastAPI, Vanilla JS

---

### Task 1: Add `ordem` to Modulo model + `order_by` on relationship

**Files:**
- Modify: `apps/api-postgres/app/modules/portal/models/portal.py`

- [ ] **Step 1: Add `ordem` column and update relationship**

Edit the `Modulo` class to add `ordem` after `role_minima`. Add `order_by` to `Aba.modulos` relationship.

Changes in `portal.py`:

Line 19 — Add `order_by` to the modulos relationship on Aba:
```python
modulos = relationship("Modulo", back_populates="aba", cascade="all, delete-orphan", order_by="Modulo.ordem")
```

After line 36 (role_minima), add the `ordem` column:
```python
ordem = Column(Integer, default=0)
```

- [ ] **Step 2: Verify model loads**

Run: `python -c "from app.modules.portal.models.portal import Modulo; print([c.name for c in Modulo.__table__.columns])"`
Expected output includes `ordem`

---

### Task 2: Create migration `012_add_modulo_ordem.py`

**Files:**
- Create: `apps/api-postgres/alembic/versions/012_add_modulo_ordem.py`

- [ ] **Step 1: Write migration file**

File content:

```python
"""Add ordem column to portal_modulos

Revision ID: a1b2c3d4e5f7
Revises: f6a7b8c9d0e1
Create Date: 2026-06-30

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f7"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "portal_modulos",
        sa.Column("ordem", sa.Integer(), server_default=sa.text("0"), nullable=False),
        schema="portal",
    )
    op.create_index(
        "ix_portal_modulos_aba_id_ordem",
        "portal_modulos",
        ["aba_id", "ordem"],
        schema="portal",
    )


def downgrade() -> None:
    op.drop_index("ix_portal_modulos_aba_id_ordem", schema="portal")
    op.drop_column("portal_modulos", "ordem", schema="portal")
```

- [ ] **Step 2: Run migration**

Run: `python -m alembic upgrade head`
Expected: `INFO  [alembic.runtime.migration] Running upgrade f6a7b8c9d0e1 -> a1b2c3d4e5f6, Add ordem column to portal_modulos`

- [ ] **Step 3: Verify column exists**

Run: `python -c "from app.database import engine; print([c for c in engine.execute('SELECT column_name FROM information_schema.columns WHERE table_name = \\'portal_modulos\\' AND column_name = \\'ordem\\'').fetchall()])"`
Expected: a row is returned

---

### Task 3: Update API schemas and CRUD endpoints

**Files:**
- Modify: `apps/api-postgres/app/routers/portal_router.py`

- [ ] **Step 1: Add `ordem` to `ModuloSchema`**

Edit line 23-31 — add `ordem` field:

```python
class ModuloSchema(BaseModel):
    id: int
    aba_id: int
    nome: str
    url: str
    icone: str
    slug: str
    role_minima: str
    ordem: int = 0

    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 2: Add `ordem` param to `criar_modulo`**

Edit `criar_modulo` (line 266-297) — add `ordem: int = 0` parameter and pass it to the model:

```python
@router.post(
    "/modulos", response_model=ModuloSchema, status_code=status.HTTP_201_CREATED
)
def criar_modulo(
    aba_id: int,
    nome: str,
    slug: str,
    url: str,
    icone: str,
    role_minima: str = "operador",
    ordem: int = 0,
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    try:
        novo_mod = Modulo(
            aba_id=aba_id,
            nome=nome,
            slug=slug,
            url=url,
            icone=icone,
            role_minima=role_minima,
            ordem=ordem,
        )
        db.add(novo_mod)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        err_msg = str(e.orig).lower() if e.orig else ""
        if "unique" in err_msg or "duplicate" in err_msg:
            raise ConflictError(f"Slug '{slug}' já existe. Use um slug diferente.")
        if "foreign" in err_msg:
            raise ConflictError(f"Aba {aba_id} não encontrada. Verifique o aba_id.")
        raise ConflictError("Erro de integridade ao criar módulo.")
    db.refresh(novo_mod)
    invalidate(_portal_cache, _portal_lock, "abas:active")
    return novo_mod
```

- [ ] **Step 3: Add `ordem` param to `atualizar_modulo`**

Edit `atualizar_modulo` (line 300-319):

```python
@router.put("/modulos/{modulo_id}", response_model=ModuloSchema)
def atualizar_modulo(
    modulo_id: int,
    nome: str,
    aba_id: int,
    role_minima: str | None = None,
    ordem: int | None = None,
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    mod = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not mod:
        raise HTTPException(404, "Módulo não encontrado")
    mod.nome = nome
    mod.aba_id = aba_id
    if role_minima is not None:
        mod.role_minima = role_minima
    if ordem is not None:
        mod.ordem = ordem
    db.commit()
    db.refresh(mod)
    invalidate(_portal_cache, _portal_lock, "abas:active")
    return mod
```

- [ ] **Step 4: Verify API responds with ordem**

Run: `python -m pytest apps/api-postgres/tests/ -k "portal" -v`
Expected: No existing portal tests — this may skip. Verify manually by starting server and checking menu response.

---

### Task 4: Add frontend validation rule

**Files:**
- Modify: `apps/frontend-webapp/shared/validation.js`

- [ ] **Step 1: Add `modOrdem` to `portalModulo` schema**

Edit `portalModulo` (line 105-110):

```javascript
portalModulo: [
    { id: 'modAbaId', required: true, message: 'Selecione a aba de destino.' },
    { id: 'modNome', required: true, message: 'Informe o nome do módulo.' },
    { id: 'modUrl', required: true, urlPath: true, message: 'Informe a URL do arquivo.' },
    { id: 'modSlug', required: true, minLength: 2, message: 'Informe o identificador.' },
    { id: 'modOrdem', number: true }
]
```

---

### Task 5: Add ordem field in frontend structure module

**Files:**
- Modify: `apps/frontend-webapp/modules/structure/script.js`

- [ ] **Step 1: Add `modOrdem` to module fields in `setupForms()`**

Edit `moduleFields` (line 47-50) — add ordem field:

```javascript
const moduleFields = [
    { label: 'Nome do Módulo', id: 'modNome', required: true },
    { label: 'Ordem', id: 'modOrdem', type: 'number', value: 0 },
    { label: 'Identificador (Slug)', id: 'modSlug', required: true }
];
```

- [ ] **Step 2: Send `ordem` on module create**

Edit `saveModulo()` (lines 335-353) — add `ordem` to POST params:

```javascript
const nome = this._val('modNome');
const moduleUrl = this._val('modUrl');
const slug = this._val('modSlug');
const icone = this._val('modIcone') || 'fas fa-cube';
const roleMinima = this._val('modRoleMinima') || 'operador';
const ordem = parseInt(this._val('modOrdem')) || 0;

try {
    await window.grindx.api.request('/portal/modulos', {
        method: 'POST',
        params: { nome, slug, url: moduleUrl, icone, aba_id: abaId, role_minima: roleMinima, ordem }
    });
```

- [ ] **Step 3: Display ordem in module list**

Edit `_renderAbaCard` — add ordem display in the modulo-item (line 167):

```javascript
<div class="modulo-info">
    <strong>${mod.nome}</strong>
    <span class="modulo-url">${mod.url}</span>
    ${mod.ordem != null ? `<span class="modulo-ordem">Ordem: ${mod.ordem}</span>` : ''}
</div>
```

Add CSS for `.modulo-ordem` in the module's `style.css` or the existing stylesheet.

- [ ] **Step 4: Populate `modOrdem` on module edit**

Edit `editModulo()` — set the modOrdem field value after line 290:

```javascript
document.getElementById('modNome').value = mod.nome;
document.getElementById('modUrl').value = mod.url;
document.getElementById('modSlug').value = mod.slug;
const ordemEl = document.getElementById('modOrdem');
if (ordemEl) ordemEl.value = mod.ordem != null ? mod.ordem : 0;
```

---

### Task 6: Run full test suite and format

**Files:** N/A — verification step

- [ ] **Step 1: Run tests**

Run: `set PYTHONPATH=packages && python -m pytest apps/api-postgres/tests/ -v`
Expected: All existing tests pass (no regression)

- [ ] **Step 2: Format code**

Run: `ruff format packages/ apps/`
Expected: No errors

- [ ] **Step 3: Lint**

Run: `ruff check --fix . && ruff check .`
Expected: No errors
