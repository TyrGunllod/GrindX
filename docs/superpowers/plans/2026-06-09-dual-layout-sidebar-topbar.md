# Dual Layout (Sidebar + Topbar) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Suportar dois modos de layout no dashboard — sidebar (atual) e topbar (novo) — intercambiáveis via configurações da empresa, com persistência no banco.

**Architecture:** Adiciona coluna `layout_mode` ao model `CompanyTheme`. O frontend detecta o layout da skin ativa e renderiza o shell correspondente (sidebar vertical ou topbar com hover dropdowns). A navegação via iframe e o sistema de skins permanecem inalterados.

**Tech Stack:** SQLAlchemy + Alembic (backend), Vanilla JS + CSS (frontend), Pydantic (schemas)

---

## File Map

### Backend — Criar
| Arquivo | Responsabilidade |
|---|---|
| `apps/api-postgres/alembic/versions/009_add_layout_mode.py` | Migration: adiciona coluna `layout_mode` |

### Backend — Modificar
| Arquivo | Responsabilidade |
|---|---|
| `apps/api-postgres/app/modules/org/models/theme.py:88` | Adicionar coluna `layout_mode` no model |
| `apps/api-postgres/app/schemas/theme.py:9-70` | Adicionar `layout_mode` nos schemas Create/Update/Response |
| `apps/api-postgres/app/services/theme_service.py:42-54,82-102,162-181` | Incluir `layout_mode` em create/update/_to_dict |
| `apps/api-postgres/app/routers/theme_router.py:229-240` | Incluir `layout_mode` no create_theme_from_template |

### Frontend — Criar
| Arquivo | Responsabilidade |
|---|---|
| `apps/frontend-webapp/dashboard-topbar.html` | Shell do layout topbar (extrair do preview-topbar.html) |

### Frontend — Modificar
| Arquivo | Responsabilidade |
|---|---|
| `apps/frontend-webapp/dashboard.html` | Adicionar estrutura topbar + wrapper condicional |
| `apps/frontend-webapp/dashboard.css` | Separar estilos em `.layout-sidebar` e `.layout-topbar` |
| `apps/frontend-webapp/dashboard.js` | Adicionar `applyLayout()`, `renderTopbarNav()`, carregar layout da skin |
| `apps/frontend-webapp/shared/skinLoader.js` | Incluir `layout_mode` no fluxo, setar classe no `<html>`, disparar evento |

### Testes — Modificar
| Arquivo | Responsabilidade |
|---|---|
| `apps/api-postgres/tests/unit/test_theme_service.py` | Testar `layout_mode` em create/update/get |
| `apps/api-postgres/tests/integration/test_theme_router.py` | Testar `layout_mode` via API |

---

## Task 1: Migration — Adicionar coluna `layout_mode`

**Files:**
- Create: `apps/api-postgres/alembic/versions/009_add_layout_mode.py`

- [ ] **Step 1: Criar migration**

```python
"""Add layout_mode column to company_themes

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "company_themes",
        sa.Column(
            "layout_mode",
            sa.String(20),
            nullable=False,
            server_default="topbar",
        ),
        schema="org",
    )
    # Themes existentes ganham 'sidebar' (preserva comportamento atual)
    op.execute(
        "UPDATE org.company_themes SET layout_mode = 'sidebar' WHERE layout_mode = 'topbar'"
    )


def downgrade() -> None:
    op.drop_column("company_themes", "layout_mode", schema="org")
```

- [ ] **Step 2: Verificar migration**

Run: `cd apps/api-postgres && python -m alembic upgrade head`
Expected: Migration aplica sem erros

- [ ] **Step 3: Verificar downgrade**

Run: `cd apps/api-postgres && python -m alembic downgrade -1`
Expected: Coluna removida

- [ ] **Step 4: Re-aplicar upgrade para manter estado**

Run: `cd apps/api-postgres && python -m alembic upgrade head`

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/alembic/versions/009_add_layout_mode.py
git commit -m "feat(theme): add layout_mode column to company_themes"
```

---

## Task 2: Model — Adicionar `layout_mode` ao CompanyTheme

**Files:**
- Modify: `apps/api-postgres/app/modules/org/models/theme.py:88-90`

- [ ] **Step 1: Adicionar coluna no model**

Inserir após a coluna `copyright_text` (linha 90):

```python
    layout_mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'topbar'"),
        comment="Modo de layout: 'sidebar' ou 'topbar'",
    )
```

- [ ] **Step 2: Verificar que o model carrega sem erros**

Run: `cd apps/api-postgres && python -c "from app.models.theme import CompanyTheme; print(CompanyTheme.layout_mode)"`
Expected: `<Column('layout_mode', String(20), ...)>`

- [ ] **Step 3: Commit**

```bash
git add apps/api-postgres/app/modules/org/models/theme.py
git commit -m "feat(theme): add layout_mode field to CompanyTheme model"
```

---

## Task 3: Schemas — Adicionar `layout_mode` aos Pydantic schemas

**Files:**
- Modify: `apps/api-postgres/app/schemas/theme.py:9-70`

- [ ] **Step 1: Adicionar field em ThemeCreate**

Inserir após `copyright_text` (linha 28):

```python
    layout_mode: str = Field(
        default="topbar",
        pattern="^(sidebar|topbar)$",
        description="Modo de layout: 'sidebar' ou 'topbar'",
    )
```

- [ ] **Step 2: Adicionar field em ThemeUpdate**

Inserir após `copyright_text` (linha 42):

```python
    layout_mode: Optional[str] = Field(
        default=None,
        pattern="^(sidebar|topbar)$",
        description="Modo de layout: 'sidebar' ou 'topbar'",
    )
```

- [ ] **Step 3: Adicionar field em ThemeResponse**

Inserir após `copyright_text` (linha 65):

```python
    layout_mode: str = "topbar"
```

- [ ] **Step 4: Verificar schemas**

Run: `cd apps/api-postgres && python -c "from app.schemas.theme import ThemeCreate, ThemeUpdate, ThemeResponse; print('OK')"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add apps/api-postgres/app/schemas/theme.py
git commit -m "feat(theme): add layout_mode to Pydantic schemas"
```

---

## Task 4: Service — Incluir `layout_mode` na lógica de negócio

**Files:**
- Modify: `apps/api-postgres/app/services/theme_service.py:42-54,82-102,162-181`

- [ ] **Step 1: Adicionar `layout_mode` ao parâmetro de `create_theme`**

Na assinatura (linha 42-54), adicionar `layout_mode: str = "topbar"`:

```python
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
        layout_mode: str = "topbar",
    ) -> dict:
```

E incluir no `CompanyTheme(...)` constructor (linha 57-68):

```python
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
            layout_mode=layout_mode,
        )
```

- [ ] **Step 2: Adicionar `layout_mode` ao dict de `original_values` em `update_theme`**

Na linha 91-102, adicionar:

```python
            "layout_mode": theme.layout_mode,
```

- [ ] **Step 3: Adicionar `layout_mode` ao `_to_dict`**

Na linha 162-181, adicionar:

```python
            "layout_mode": theme.layout_mode,
```

- [ ] **Step 4: Commit**

```bash
git add apps/api-postgres/app/services/theme_service.py
git commit -m "feat(theme): include layout_mode in service layer"
```

---

## Task 5: Router — Incluir `layout_mode` no template creation

**Files:**
- Modify: `apps/api-postgres/app/routers/theme_router.py:220-240`

- [ ] **Step 1: Adicionar `layout_mode` ao create_theme_from_template**

No bloco onde `layout_mode` é extraído do template (após linha 227), adicionar:

```python
    layout_mode = template_data.get("layout_mode", "topbar")
```

E incluir no `service.create_theme(...)` (linha 229-240):

```python
    return service.create_theme(
        company_id=company_id,
        name=dados.name,
        colors=colors,
        fonts=fonts,
        icon_library=icon_library,
        tokens=tokens,
        logo_url=logo_url,
        logo_short_url=logo_short_url,
        company_name=company_name,
        copyright_text=copyright_text,
        layout_mode=layout_mode,
    )
```

- [ ] **Step 2: Commit**

```bash
git add apps/api-postgres/app/routers/theme_router.py
git commit -m "feat(theme): include layout_mode in template creation"
```

---

## Task 6: Testes Unitários — Validar `layout_mode`

**Files:**
- Modify: `apps/api-postgres/tests/unit/test_theme_service.py`

- [ ] **Step 1: Adicionar teste de create com layout_mode**

Adicionar no final do arquivo:

```python
def test_create_theme_with_layout_mode(theme_service: ThemeService, empresa: Empresa):
    """Testa criação de tema com layout_mode."""
    result = theme_service.create_theme(
        company_id=empresa.id,
        name="Layout Test",
        icon_library="fontawesome",
        layout_mode="topbar",
    )
    assert result["layout_mode"] == "topbar"


def test_create_theme_default_layout_mode(theme_service: ThemeService, empresa: Empresa):
    """Testa que layout_mode padrão é 'topbar'."""
    result = theme_service.create_theme(
        company_id=empresa.id,
        name="Default Layout",
        icon_library="fontawesome",
    )
    assert result["layout_mode"] == "topbar"


def test_update_theme_layout_mode(theme_service: ThemeService, empresa: Empresa):
    """Testa atualização de layout_mode."""
    created = theme_service.create_theme(
        company_id=empresa.id,
        name="Update Layout",
        icon_library="fontawesome",
        layout_mode="topbar",
    )
    updated = theme_service.update_theme(
        created["id"], company_id=empresa.id, layout_mode="sidebar"
    )
    assert updated["layout_mode"] == "sidebar"
```

- [ ] **Step 2: Rodar testes unitários**

Run: `cd apps/api-postgres && python -m pytest tests/unit/test_theme_service.py -v`
Expected: Todos os testes passam, incluindo os 3 novos

- [ ] **Step 3: Commit**

```bash
git add apps/api-postgres/tests/unit/test_theme_service.py
git commit -m "test(theme): add unit tests for layout_mode"
```

---

## Task 7: Testes de Integração — Validar `layout_mode` via API

**Files:**
- Modify: `apps/api-postgres/tests/integration/test_theme_router.py`

- [ ] **Step 1: Adicionar teste de create com layout_mode via API**

Adicionar no final do arquivo:

```python
def test_create_theme_with_layout_mode(client: TestClient, admin_auth_headers: dict):
    """Testa que layout_mode é retornando na criação."""
    response = client.post(
        "/v1/themes",
        json={
            "name": "Layout API Test",
            "icon_library": "fontawesome",
            "layout_mode": "topbar",
        },
        headers=admin_auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["layout_mode"] == "topbar"


def test_update_theme_layout_mode(client: TestClient, admin_auth_headers: dict):
    """Testa atualização de layout_mode via API."""
    # Criar tema
    create_resp = client.post(
        "/v1/themes",
        json={
            "name": "Layout Update Test",
            "icon_library": "fontawesome",
            "layout_mode": "topbar",
        },
        headers=admin_auth_headers,
    )
    theme_id = create_resp.json()["id"]

    # Atualizar layout_mode
    update_resp = client.put(
        f"/v1/themes/{theme_id}",
        json={"layout_mode": "sidebar"},
        headers=admin_auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["layout_mode"] == "sidebar"


def test_get_active_theme_includes_layout_mode(
    client: TestClient, admin_auth_headers: dict
):
    """Testa que tema ativo retorna layout_mode."""
    # Criar e ativar tema
    create_resp = client.post(
        "/v1/themes",
        json={
            "name": "Active Layout",
            "icon_library": "fontawesome",
            "layout_mode": "topbar",
        },
        headers=admin_auth_headers,
    )
    theme_id = create_resp.json()["id"]
    client.post(f"/v1/themes/{theme_id}/activate", headers=admin_auth_headers)

    # Buscar tema ativo
    get_resp = client.get("/v1/themes/active", headers=admin_auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["layout_mode"] == "topbar"
```

- [ ] **Step 2: Rodar testes de integração**

Run: `cd apps/api-postgres && python -m pytest tests/integration/test_theme_router.py -v`
Expected: Todos os testes passam, incluindo os 3 novos

- [ ] **Step 3: Commit**

```bash
git add apps/api-postgres/tests/integration/test_theme_router.py
git commit -m "test(theme): add integration tests for layout_mode"
```

---

## Task 8: SkinLoader — Carregar e aplicar `layout_mode`

**Files:**
- Modify: `apps/frontend-webapp/shared/skinLoader.js:184-190`

- [ ] **Step 1: Adicionar método `applyLayout` ao SkinLoader**

Adicionar após o método `_applySkin` (linha 190):

```javascript
    /**
     * Aplica a classe de layout no <html> e dispara evento
     * @param {string} mode - 'sidebar' ou 'topbar'
     */
    applyLayout(mode) {
        const root = document.documentElement;
        root.classList.remove('layout-sidebar', 'layout-topbar');
        const validMode = ['sidebar', 'topbar'].includes(mode) ? mode : 'topbar';
        root.classList.add(`layout-${validMode}`);
        window.dispatchEvent(new CustomEvent('layoutchange', {
            detail: { mode: validMode }
        }));
    }
```

- [ ] **Step 2: Chamar `applyLayout` dentro de `_applySkin`**

Na linha 184-190, adicionar chamada ao final de `_applySkin`:

```javascript
    _applySkin(skin) {
        this._applyColors(skin.colors);
        this._applyTokens(skin.tokens);
        this._applyFonts(skin.fonts);
        this._updateBranding(skin.company_name, skin.copyright_text);
        this._updateLogos(skin.logo_url, skin.logo_short_url);
        if (skin.layout_mode) {
            this.applyLayout(skin.layout_mode);
        }
    }
```

- [ ] **Step 3: Adicionar `layout_mode` ao `SKIN_DEFAULTS`**

Na linha 37, adicionar:

```javascript
    layout_mode: 'topbar',
```

- [ ] **Step 4: Commit**

```bash
git add apps/frontend-webapp/shared/skinLoader.js
git commit -m "feat(skin): apply layout_mode from active theme"
```

---

## Task 9: Dashboard HTML — Estrutura dual

**Files:**
- Modify: `apps/frontend-webapp/dashboard.html`

- [ ] **Step 1: Adicionar wrapper `layout-topbar` ao body**

Substituir `<body class="dashboard-layout">` por:

```html
<body class="dashboard-layout layout-topbar">
```

- [ ] **Step 2: Adicionar topbar após o sidebar**

Inserir após o `</aside>` (linha 82) e antes do preview banner (linha 84):

```html
    <!-- Navigation Topbar (Topbar Mode) -->
    <header class="topbar" id="topbar" style="display:none;" role="banner">
        <div class="topbar-logo" aria-hidden="true">
            G<span class="logo-full">RIND</span><span style="color: var(--brand-is);">X</span>
        </div>
        <nav class="topbar-nav" id="topbarNav" aria-label="Navegação Principal">
            <!-- Renderizado dinamicamente por renderTopbarNav() -->
        </nav>
        <div class="topbar-right">
            <button class="btn-icon" id="themeToggleTopbar" aria-label="Alternar tema">
                <i class="fas fa-moon"></i>
            </button>
            <div class="user-pill-compact" id="userPillTopbar" tabindex="0" role="button" aria-label="Menu do usuário" aria-haspopup="true">
                <div class="user-avatar-sm" id="userAvatarTopbar">...</div>
                <div class="user-pill-info">
                    <span class="user-pill-name" id="userNameTopbar">...</span>
                    <span class="user-pill-role" id="userRoleTopbar">...</span>
                </div>
                <i class="fas fa-chevron-down" style="font-size:0.6rem;color:var(--text-muted);margin-left:2px;"></i>
                <div class="user-dropdown" id="userDropdownTopbar" role="menu">
                    <button class="nav-dropdown-item" role="menuitem">
                        <i class="fas fa-user"></i> Meu Perfil
                    </button>
                    <button class="nav-dropdown-item" role="menuitem" id="passwordBtnTopbar">
                        <i class="fas fa-key"></i> Alterar Senha
                    </button>
                    <div class="nav-dropdown-divider"></div>
                    <button class="nav-dropdown-item danger" role="menuitem" id="logoutBtnTopbar">
                        <i class="fas fa-power-off"></i> Sair
                    </button>
                </div>
            </div>
        </div>
    </header>
```

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/dashboard.html
git commit -m "feat(dashboard): add topbar HTML structure"
```

---

## Task 10: Dashboard CSS — Estilos condicionais

**Files:**
- Modify: `apps/frontend-webapp/dashboard.css`

- [ ] **Step 1: Adicionar estilos do topbar**

Adicionar no final do arquivo (após linha 564):

```css
/* ==========================================
   TOPBAR MODE STYLES
   ========================================== */

/* ── TOPBAR ── */
.topbar {
    display: none;
    align-items: center;
    height: 52px;
    min-height: 52px;
    background: var(--bg-card);
    border-bottom: 1px solid var(--border-color);
    padding: 0 var(--space-4);
    z-index: 100;
}

.topbar-logo {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-family: var(--font-display);
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    color: var(--text-main);
    padding-right: var(--space-4);
    border-right: 1px solid var(--border-color);
    margin-right: var(--space-3);
    flex-shrink: 0;
    user-select: none;
}
.topbar-logo .brand-x { color: var(--brand-is); }

/* ── NAV GROUPS (hover dropdowns) ── */
.topbar-nav {
    display: flex;
    align-items: center;
    gap: 4px;
    flex: 1;
    overflow-x: auto;
    scrollbar-width: none;
}
.topbar-nav::-webkit-scrollbar { display: none; }

.nav-group-topbar {
    position: relative;
}

.nav-group-trigger {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 0.85rem;
    border-radius: 0.5rem;
    border: none;
    background: none;
    color: var(--text-muted);
    font: inherit;
    font-size: 0.82rem;
    font-weight: 500;
    white-space: nowrap;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
}
.nav-group-trigger i.icon { font-size: 0.9rem; }
.nav-group-trigger i.chevron {
    font-size: 0.6rem;
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    opacity: 0.5;
}
.nav-group-trigger:hover,
.nav-group-topbar.open .nav-group-trigger {
    background: rgba(79, 70, 229, 0.08);
    color: var(--text-main);
}
.nav-group-topbar.open .nav-group-trigger i.chevron {
    transform: rotate(180deg);
}

/* Active indicator dot */
.nav-group-trigger .active-dot {
    display: none;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--primary);
    position: absolute;
    top: 6px;
    right: 6px;
}
.nav-group-topbar.has-active .nav-group-trigger .active-dot {
    display: block;
}

/* ── DROPDOWN (top-down) ── */
.nav-dropdown {
    position: absolute;
    top: calc(100% + 6px);
    left: 0;
    min-width: 200px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
    padding: 0.35rem;
    z-index: 300;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-8px);
    transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: none;
}

.nav-group-topbar.open .nav-dropdown {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
    pointer-events: auto;
}

.nav-dropdown-item {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    width: 100%;
    padding: 0.55rem 0.75rem;
    border: none;
    background: none;
    color: var(--text-main);
    font: inherit;
    font-size: 0.82rem;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: background 0.15s;
    text-align: left;
    white-space: nowrap;
}
.nav-dropdown-item i {
    font-size: 0.85rem;
    width: 1.2rem;
    text-align: center;
    color: var(--text-muted);
    transition: color 0.15s;
}
.nav-dropdown-item:hover {
    background: rgba(79, 70, 229, 0.08);
}
.nav-dropdown-item:hover i {
    color: var(--primary);
}
.nav-dropdown-item.active {
    background: rgba(79, 70, 229, 0.12);
    color: var(--primary);
    font-weight: 600;
}
.nav-dropdown-item.active i {
    color: var(--primary);
}
.nav-dropdown-item.danger { color: #ef4444; }
.nav-dropdown-item.danger:hover { background: rgba(239, 68, 68, 0.08); }

.nav-dropdown-divider {
    height: 1px;
    background: var(--border-color);
    margin: 0.25rem 0;
}

/* ── NAV SEPARATOR ── */
.nav-separator {
    width: 1px;
    height: 20px;
    background: var(--border-color);
    margin: 0 4px;
    flex-shrink: 0;
}

/* ── RIGHT CLUSTER ── */
.topbar-right {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-left: auto;
    padding-left: var(--space-3);
    flex-shrink: 0;
}

/* User Pill (compact) */
.user-pill-compact {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.3rem 0.6rem 0.3rem 0.3rem;
    border-radius: 2rem;
    background: rgba(79, 70, 229, 0.06);
    border: 1px solid var(--border-color);
    cursor: pointer;
    transition: background 0.2s;
    position: relative;
}
.user-pill-compact:hover {
    background: rgba(79, 70, 229, 0.12);
}

.user-avatar-sm {
    width: 28px;
    height: 28px;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    background: var(--primary);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 700;
    flex-shrink: 0;
}

.user-pill-info {
    display: flex;
    flex-direction: column;
}
.user-pill-name {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-main);
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.user-pill-role {
    font-size: 0.65rem;
    color: var(--text-muted);
}

.user-dropdown {
    position: absolute;
    top: calc(100% + 6px);
    right: 0;
    min-width: 200px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
    padding: 0.35rem;
    z-index: 300;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-8px);
    transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: none;
}
.user-pill-compact.open .user-dropdown {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
    pointer-events: auto;
}

/* ── LAYOUT MODE SWITCHING ── */
.layout-sidebar .sidebar {
    display: flex;
}
.layout-sidebar .topbar {
    display: none !important;
}
.layout-sidebar .main-viewport {
    width: calc(100% - 280px);
}
.layout-sidebar .sidebar.collapsed ~ .main-viewport {
    width: calc(100% - 88px);
}

.layout-topbar .sidebar {
    display: none !important;
}
.layout-topbar .topbar {
    display: flex;
}
.layout-topbar .main-viewport {
    width: 100%;
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/dashboard.css
git commit -m "feat(dashboard): add topbar CSS styles with layout switching"
```

---

## Task 11: Dashboard JS — Lógica de layout dual

**Files:**
- Modify: `apps/frontend-webapp/dashboard.js`

- [ ] **Step 1: Adicionar propriedade `currentLayout` ao constructor**

Após `this.loader = ...` (linha 12), adicionar:

```javascript
        this.topbar = document.getElementById('topbar');
        this.topbarNav = document.getElementById('topbarNav');
        this.currentLayout = 'topbar';
```

- [ ] **Step 2: Adicionar listener do evento `layoutchange` no `setupEvents`**

Adicionar ao final de `setupEvents()` (após linha 86):

```javascript
            window.addEventListener('layoutchange', (e) => {
                this.applyLayout(e.detail.mode);
            });
```

- [ ] **Step 3: Adicionar método `applyLayout`**

Adicionar novo método ao final da classe (antes do `}` final):

```javascript
    applyLayout(mode) {
        this.currentLayout = mode;
        const body = document.body;
        body.classList.remove('layout-sidebar', 'layout-topbar');
        body.classList.add(`layout-${mode}`);

        if (mode === 'topbar') {
            this.sidebar.style.display = 'none';
            this.topbar.style.display = 'flex';
            // Sincronizar user info no topbar
            this.updateTopbarUserUI(this.user);
            // Re-renderizar nav se já tiver dados
            if (this._lastAbas) this.renderTopbarNav(this._lastAbas);
        } else {
            this.sidebar.style.display = '';
            this.topbar.style.display = 'none';
        }
    }
```

- [ ] **Step 4: Adicionar método `renderTopbarNav`**

Adicionar após `renderSidebar`:

```javascript
    renderTopbarNav(abas) {
        this._lastAbas = abas;
        if (this.currentLayout !== 'topbar') return;

        this.topbarNav.innerHTML = abas.map((aba, idx) => {
            const modulos = (aba.modulos || []).filter(mod => {
                if (mod.role_minima === 'admin' && this.user.role !== 'admin') return false;
                return true;
            });

            const childrenHtml = (aba.children || []).map(child => {
                const childMods = (child.modulos || []).filter(mod => {
                    if (mod.role_minima === 'admin' && this.user.role !== 'admin') return false;
                    return true;
                });
                return childMods.map(mod => `
                    <button class="nav-dropdown-item" data-module="${mod.slug}" data-url="${mod.url}">
                        <i class="${mod.icone || 'fas fa-cube'}"></i> ${mod.nome}
                    </button>
                `).join('');
            }).join('');

            const directModsHtml = modulos.map(mod => `
                <button class="nav-dropdown-item" data-module="${mod.slug}" data-url="${mod.url}">
                    <i class="${mod.icone || 'fas fa-cube'}"></i> ${mod.nome}
                </button>
            `).join('');

            const separator = idx < abas.length - 1 ? '<div class="nav-separator"></div>' : '';

            return `
                <div class="nav-group-topbar" data-group="${aba.id}">
                    <button class="nav-group-trigger" aria-haspopup="true" aria-expanded="false">
                        <i class="${aba.icone || 'fas fa-folder'} icon"></i>
                        <span>${aba.nome}</span>
                        <i class="fas fa-chevron-down chevron"></i>
                        <span class="active-dot"></span>
                    </button>
                    <div class="nav-dropdown" role="menu">
                        ${childrenHtml}
                        ${directModsHtml}
                    </div>
                </div>
                ${separator}
            `;
        }).join('');

        // Bind hover events
        this._bindTopbarDropdowns();
        // Bind item clicks
        this._bindTopbarNavClicks();
    }
```

- [ ] **Step 5: Adicionar método `_bindTopbarDropdowns`**

```javascript
    _bindTopbarDropdowns() {
        const groups = this.topbarNav.querySelectorAll('.nav-group-topbar');
        let closeTimeout = null;

        groups.forEach(group => {
            group.addEventListener('mouseenter', () => {
                clearTimeout(closeTimeout);
                groups.forEach(g => { if (g !== group) g.classList.remove('open'); });
                group.classList.add('open');
                group.querySelector('.nav-group-trigger').setAttribute('aria-expanded', 'true');
            });

            group.addEventListener('mouseleave', () => {
                closeTimeout = setTimeout(() => {
                    group.classList.remove('open');
                    group.querySelector('.nav-group-trigger').setAttribute('aria-expanded', 'false');
                }, 120);
            });
        });

        // Close on click outside
        document.addEventListener('click', () => {
            groups.forEach(g => {
                g.classList.remove('open');
                g.querySelector('.nav-group-trigger').setAttribute('aria-expanded', 'false');
            });
        });
    }
```

- [ ] **Step 6: Adicionar método `_bindTopbarNavClicks`**

```javascript
    _bindTopbarNavClicks() {
        this.topbarNav.querySelectorAll('.nav-dropdown-item[data-module]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();

                // Remove active from all, set on clicked
                this.topbarNav.querySelectorAll('.nav-dropdown-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');

                // Mark group as having active item
                this.topbarNav.querySelectorAll('.nav-group-topbar').forEach(g => g.classList.remove('has-active'));
                item.closest('.nav-group-topbar')?.classList.add('has-active');

                // Navigate
                this.navigateToModule(item.dataset.url);

                // Close dropdown
                const group = item.closest('.nav-group-topbar');
                if (group) {
                    group.classList.remove('open');
                    group.querySelector('.nav-group-trigger').setAttribute('aria-expanded', 'false');
                }

                // Update title
                document.getElementById('activeModuleTitle').textContent = item.textContent.trim();
            });
        });
    }
```

- [ ] **Step 7: Adicionar método `updateTopbarUserUI`**

```javascript
    updateTopbarUserUI(user) {
        if (!user) return;
        const displayName = this.getUserDisplayName(user);
        const userNameEl = document.getElementById('userNameTopbar');
        const userRoleEl = document.getElementById('userRoleTopbar');
        const avatarEl = document.getElementById('userAvatarTopbar');
        if (userNameEl) userNameEl.textContent = displayName;
        if (userRoleEl) userRoleEl.textContent = this.formatRole(user.role);
        if (avatarEl) {
            const initials = this.getInitials(displayName);
            avatarEl.textContent = initials;
        }
    }
```

- [ ] **Step 8: Modificar `loadDynamicMenu` para chamar ambos os renders**

Substituir o método `loadDynamicMenu` (linha 102-109):

```javascript
    async loadDynamicMenu() {
        try {
            const menuData = await window.grindx.api.get('/portal/menu');
            this.renderSidebar(menuData);
            this.renderTopbarNav(menuData);
        } catch (err) {
            console.error('Falha ao carregar menu dinâmico:', err);
        }
    }
```

- [ ] **Step 9: Modificar `loadInitialView` para funcionar em ambos os modos**

Substituir `loadInitialView` (linha 452-458):

```javascript
    loadInitialView() {
        setTimeout(() => {
            // Tenta nav-link (sidebar) ou nav-dropdown-item (topbar)
            const firstLink = this.mainNav.querySelector('.nav-link')
                || this.topbarNav.querySelector('.nav-dropdown-item');
            if (firstLink) firstLink.click();
        }, 500);
    }
```

- [ ] **Step 10: Modificar `updateUserUI` para sincronizar topbar**

No método `updateUserUI` (linha 319-325), adicionar ao final:

```javascript
        this.updateTopbarUserUI(user);
```

- [ ] **Step 11: Modificar `init` para aplicar layout inicial**

No método `init` (linha 17-25), adicionar após `this.checkSidebarState()`:

```javascript
        this.topbar = document.getElementById('topbar');
        this.topbarNav = document.getElementById('topbarNav');
```

- [ ] **Step 12: Bind eventos do topbar (logout, password, theme)**

Adicionar ao final de `setupEvents()`:

```javascript
            // Topbar events
            document.getElementById('logoutBtnTopbar')?.addEventListener('click', () => this.logout());
            document.getElementById('passwordBtnTopbar')?.addEventListener('click', () => this.openPasswordModal());
            document.getElementById('themeToggleTopbar')?.addEventListener('click', () => {
                window.grindx.theme.toggle();
                this.updateThemeIcon();
                this.viewport.querySelectorAll('iframe').forEach(f => this.applySkinToIframe(f));
            });

            // Topbar user pill dropdown
            const userPillTopbar = document.getElementById('userPillTopbar');
            if (userPillTopbar) {
                userPillTopbar.addEventListener('click', (e) => {
                    e.stopPropagation();
                    userPillTopbar.classList.toggle('open');
                });
            }
            document.addEventListener('click', () => {
                document.getElementById('userPillTopbar')?.classList.remove('open');
            });
```

- [ ] **Step 13: Commit**

```bash
git add apps/frontend-webapp/dashboard.js
git commit -m "feat(dashboard): implement dual layout switching logic"
```

---

## Task 12: Verificação Final

- [ ] **Step 1: Rodar migration**

Run: `cd apps/api-postgres && python -m alembic upgrade head`
Expected: Sem erros

- [ ] **Step 2: Rodar todos os testes do api-postgres**

Run: `cd apps/api-postgres && python -m pytest tests/ -v`
Expected: Todos passam

- [ ] **Step 3: Rodar lint**

Run: `cd apps/api-postgres && ruff check app/ tests/`
Expected: Sem erros

- [ ] **Step 4: Rodar lint no frontend**

Run: `ruff check apps/frontend-webapp/` (se aplicável)

- [ ] **Step 5: Testar manualmente**

1. Abrir `dashboard.html` no browser
2. Verificar que carrega no modo topbar (layout padrão)
3. Verificar hover dropdowns funcionam
4. Mudar `layout_mode` para `sidebar` via API (PUT /v1/themes/{id})
5. Recarregar dashboard — deve mostrar sidebar
6. Voltar para `topbar` — deve voltar ao topbar

- [ ] **Step 6: Commit final (se houver ajustes)**

---

## Resumo de Impacto

| Camada | Arquivos Criados | Arquivos Modificados |
|---|---|---|
| Backend Model | 0 | 1 (`theme.py`) |
| Backend Schema | 0 | 1 (`theme.py`) |
| Backend Service | 0 | 1 (`theme_service.py`) |
| Backend Router | 0 | 1 (`theme_router.py`) |
| Migration | 1 | 0 |
| Frontend HTML | 0 | 1 (`dashboard.html`) |
| Frontend CSS | 0 | 1 (`dashboard.css`) |
| Frontend JS | 0 | 2 (`dashboard.js`, `skinLoader.js`) |
| Testes | 0 | 2 |
| **Total** | **1** | **9** |
