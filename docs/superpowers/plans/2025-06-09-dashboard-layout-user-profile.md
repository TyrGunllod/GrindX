# Dashboard Layout & User Profile — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardize logo+company name, make logo clickable for user menu, create profile module, remove standalone theme toggles, add auto-logout on token expiry.

**Architecture:** Frontend changes in dashboard shell (HTML/CSS/JS) + new profile module + skinLoader fix + API 401 interception. Backend: new `PUT /v1/auth/me` endpoint with `AuthService.update_profile`.

**Tech Stack:** Vanilla JS, FastAPI, SQLAlchemy, pytest

---

## File Structure

### Modified Files
| File | Change |
|------|--------|
| `apps/frontend-webapp/dashboard.html` | Simplify logos, remove user-pill sidebar, remove theme toggles, remove topbar user-pill |
| `apps/frontend-webapp/dashboard.css` | Remove sidebar user-pill styles, add logo-clickable dropdown styles |
| `apps/frontend-webapp/dashboard.js` | Replace logo click handlers, remove theme toggle events, remove updateThemeIcon |
| `apps/frontend-webapp/shared/apiService.js` | Add 401 interception → redirect to login |
| `apps/frontend-webapp/shared/skinLoader.js` | Update `_updateBranding` to also update `.topbar-logo` |
| `apps/api-postgres/app/auth/service.py` | Add `update_profile` method |
| `apps/api-postgres/app/auth/router.py` | Add `PUT /v1/auth/me` endpoint |

### Created Files
| File | Purpose |
|------|---------|
| `apps/frontend-webapp/modules/profile/index.html` | Profile page HTML |
| `apps/frontend-webapp/modules/profile/style.css` | Profile page styles |
| `apps/frontend-webapp/modules/profile/script.js` | Profile controller (load/save user data, password, theme) |

---

### Task 1: Backend — Add `update_profile` to AuthService

**Files:**
- Modify: `apps/api-postgres/app/auth/service.py` (add method after `change_password`)
- Modify: `apps/api-postgres/app/auth/router.py` (add endpoint)

- [ ] **Step 1: Add `update_profile` method to AuthService**

  Add after `change_password` (line 198):

```python
def update_profile(self, user_id: int, email: str | None = None, nome_completo: str | None = None) -> Usuario:
    usuario = self.usuario_repo.buscar_por_id(user_id)
    if not usuario:
        raise NotFoundError(resource="Usuário", identifier=user_id)

    dados: dict[str, str] = {}
    if email is not None:
        if email != usuario.email:
            existing = self.usuario_repo.buscar_por_email(email)
            if existing:
                raise ConflictError(f"E-mail '{email}' já está em uso")
        dados["email"] = email
    if nome_completo is not None:
        dados["nome_completo"] = nome_completo

    if not dados:
        return usuario

    return self.usuario_repo.atualizar(usuario, dados)
```

- [ ] **Step 2: Add email lookup to UsuarioRepository**

  Check if `buscar_por_email` exists:

```python
# In app/repositories/usuario_repository.py, add method:
def buscar_por_email(self, email: str) -> Usuario | None:
    return self.db.query(Usuario).filter(Usuario.email == email).first()
```

  Run: `python -c "from app.repositories.usuario_repository import UsuarioRepository; print(dir(UsuarioRepository))"` to verify the method exists. If it already exists, skip this step.

- [ ] **Step 3: Add PUT /v1/auth/me endpoint**

  Add before the `change_password` route (line 165) in `apps/api-postgres/app/auth/router.py`:

```python
from app.schemas.usuario import UsuarioUpdate  # add to existing imports

@router.put(
    "/me",
    response_model=UsuarioResponse,
    summary="Atualizar próprio perfil",
    description="Permite que o usuário autenticado atualize seu próprio email e/ou nome completo.",
)
def update_me(
    dados: UsuarioUpdate,
    current_user: TokenPayload = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.update_profile(
        int(current_user.sub),
        email=dados.email,
        nome_completo=dados.nome_completo,
    )
```

- [ ] **Step 4: Commit**

```bash
git add apps/api-postgres/app/auth/service.py apps/api-postgres/app/auth/router.py
git commit -m "feat(auth): adicionar endpoint PUT /v1/auth/me para autoatualizacao de perfil"
```

---

### Task 2: Frontend — Fix skinLoader to update topbar logo

**Files:**
- Modify: `apps/frontend-webapp/shared/skinLoader.js`

- [ ] **Step 1: Add topbar-logo update to `_updateBranding`**

  In `_updateBranding` (line 275), after the sidebar logo update (line 285), add:

```javascript
// Atualiza logo no topbar
const topbarLogoEl = document.querySelector('.topbar-logo');
if (topbarLogoEl) {
    topbarLogoEl.innerHTML = companyName.substring(0, 1) + '<span class="logo-full">' + companyName.substring(1) + '</span>';
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/shared/skinLoader.js
git commit -m "fix(skinloader): atualizar tambem topbar-logo no _updateBranding"
```

---

### Task 3: Frontend — Update dashboard.html layout

**Files:**
- Modify: `apps/frontend-webapp/dashboard.html`

- [ ] **Step 1: Replace sidebar logo to be clickable**

  Replace lines 29-31 (the `logo-grindx` div):

```html
<div class="logo-grindx font-display logo-clickable" style="font-size: 1.3rem; letter-spacing: 3px; color: var(--text-main);padding: 5px" tabindex="0" role="button" aria-label="Menu do usuário" aria-haspopup="true">
    G<span class="logo-full">RIND</span><span style="color: var(--brand-is);">X</span>
    <div class="user-dropdown logo-user-dropdown" id="userDropdownSidebar" role="menu">
        <div class="dropdown-user-info">
            <strong class="dropdown-user-name" id="userNameSidebar">...</strong>
            <span class="dropdown-user-role" id="userRoleSidebar">...</span>
        </div>
        <div class="nav-dropdown-divider"></div>
        <button class="nav-dropdown-item" role="menuitem" data-profile="true">
            <i class="fas fa-user"></i> Meu Perfil
        </button>
        <div class="nav-dropdown-divider"></div>
        <button class="nav-dropdown-item danger" role="menuitem" id="logoutBtnSidebar">
            <i class="fas fa-power-off"></i> Sair
        </button>
    </div>
</div>
```

- [ ] **Step 2: Remove sidebar user-pill footer**

  Replace lines 69-81 (the `sidebar-footer`):

```html
<footer class="sidebar-footer">
    <div class="copyright-text">© 2026 GrindX. Desenvolvido por Alex Grellet.</div>
</footer>
```

- [ ] **Step 3: Replace topbar logo to be clickable + remove theme toggle + remove user pill**

  Replace lines 85-117 (the entire `topbar` header):

```html
<header class="topbar" id="topbar" style="display:none;" role="banner">
    <div class="topbar-logo logo-clickable" tabindex="0" role="button" aria-label="Menu do usuário" aria-haspopup="true">
        G<span class="logo-full">RIND</span><span style="color: var(--brand-is);">X</span>
        <div class="user-dropdown logo-user-dropdown" id="userDropdownTopbar" role="menu">
            <div class="dropdown-user-info">
                <strong class="dropdown-user-name" id="userNameTopbarDropdown">...</strong>
                <span class="dropdown-user-role" id="userRoleTopbarDropdown">...</span>
            </div>
            <div class="nav-dropdown-divider"></div>
            <button class="nav-dropdown-item" role="menuitem" data-profile="true">
                <i class="fas fa-user"></i> Meu Perfil
            </button>
            <div class="nav-dropdown-divider"></div>
            <button class="nav-dropdown-item danger" role="menuitem" id="logoutBtnTopbar">
                <i class="fas fa-power-off"></i> Sair
            </button>
        </div>
    </div>
    <nav class="topbar-nav" id="topbarNav" aria-label="Navegação Principal">
        <!-- Renderizado dinamicamente por renderTopbarNav() -->
    </nav>
    <div class="topbar-right" id="topbarRight">
        <!-- Espaço reservado para futuras abas -->
    </div>
</header>
```

- [ ] **Step 4: Remove theme toggle from main viewport header**

  Replace lines 131-140 (the `main-viewport` header with top-bar):

```html
<main class="main-viewport">
    <header class="top-bar" style="padding: 15px;">
        <button class="btn-icon md-hide" id="openSidebar" aria-label="Abrir menu">
            <i class="fas fa-bars"></i>
        </button>
        <div class="top-bar-title" id="activeModuleTitle">Painel de Controle</div>
    </header>
```

- [ ] **Step 5: Remove password modal**

  Remove lines 150-175 (the entire `#passwordModal` div), since password change will be in the profile module.

- [ ] **Step 6: Commit**

```bash
git add apps/frontend-webapp/dashboard.html
git commit -m "feat(dashboard): logos clicaveis, remover user-pill sidebar, theme toggles e modal senha"
```

---

### Task 4: Frontend — Update dashboard.css

**Files:**
- Modify: `apps/frontend-webapp/dashboard.css`

- [ ] **Step 1: Add .logo-clickable styles**

  Add to dashboard.css (after existing logo styles):

```css
.logo-clickable {
    cursor: pointer;
    position: relative;
    user-select: none;
}

.logo-clickable .logo-user-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    min-width: 200px;
    margin-top: 4px;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-4px);
    transition: opacity 0.2s ease, transform 0.2s ease, visibility 0.2s;
    pointer-events: none;
    z-index: 1000;
}

.logo-clickable.open .logo-user-dropdown {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
    pointer-events: auto;
}

.dropdown-user-info {
    padding: 10px 14px;
    text-align: center;
}

.dropdown-user-name {
    display: block;
    font-size: 0.85rem;
    color: var(--text-main);
}

.dropdown-user-role {
    display: block;
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 2px;
}

.sidebar.collapsed .logo-clickable .logo-user-dropdown {
    left: 100%;
    top: 0;
    margin-top: 0;
    margin-left: 4px;
}

.sidebar.collapsed .logo-clickable .dropdown-user-info {
    display: none;
}
```

- [ ] **Step 2: Remove sidebar user-pill styles**

  Find and remove the CSS block for `.user-pill` and related sidebar-footer user styles (lines ~69-100 in the original CSS). Replace them with simplified footer styling:

```css
.sidebar-footer {
    padding: 8px 12px;
    border-top: 1px solid var(--border-color);
}

.sidebar.collapsed .sidebar-footer {
    padding: 8px;
}

.sidebar.collapsed .sidebar-footer .copyright-text {
    display: none;
}

.copyright-text {
    font-size: 0.65rem;
    color: var(--text-muted);
    text-align: center;
    line-height: 1.4;
}
```

- [ ] **Step 3: Update topbar-right to have minimal width**

  Replace or update `.topbar-right` style:

```css
.topbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-left: auto;
    min-width: 0;
}
```

- [ ] **Step 4: Update topbar-logo to not have border-right when clickable**

  Update `.topbar-logo` to have the user-dropdown positioning context:

```css
.topbar-logo {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0 16px;
    font-family: var(--font-display, 'Barlow Condensed', sans-serif);
    font-size: 1.4rem;
    font-weight: 600;
    letter-spacing: 2.5px;
    border-right: 1px solid var(--border-color);
    color: var(--text-main);
    white-space: nowrap;
    cursor: pointer;
    position: relative;
    user-select: none;
}

.topbar-logo .logo-user-dropdown {
    top: 100%;
    left: 0;
}
```

- [ ] **Step 5: Reuse existing .user-dropdown styles for .logo-user-dropdown**

  The `.user-dropdown` class already has the correct styling (background, border, shadow, etc.). The `.logo-user-dropdown` uses the same class, so no additional base styles needed. Just ensure the positioning overrides are correct from Step 1.

- [ ] **Step 6: Commit**

```bash
git add apps/frontend-webapp/dashboard.css
git commit -m "feat(dashboard): estilos para logo-clicavel e ajustes pos-remocao user-pill"
```

---

### Task 5: Frontend — Update dashboard.js

**Files:**
- Modify: `apps/frontend-webapp/dashboard.js`

- [ ] **Step 1: Remove theme toggle event bindings**

  Remove lines 64-68 (themeToggle click) and lines 97-101 (themeToggleTopbar click) from `setupEvents()`.

  Also remove `updateThemeIcon()` method (lines 538-541) and its calls.

- [ ] **Step 2: Remove old user-pill click handlers**

  Remove lines 103-113 (userPillTopbar click handler + document click close).

- [ ] **Step 3: Remove password modal handlers**

  Remove line 84 (`userAvatar click → openPasswordModal`). Remove `openPasswordModal` (lines 543-556), `savePassword` (lines 558-586), `showPasswordError` (lines 588-597).

- [ ] **Step 4: Remove sidebar logoutBtn handler**

  Remove line 62 (`logoutBtn click → logout`), since the sidebar no longer has a standalone logout button.

- [ ] **Step 5: Add logo click handlers**

  Add to `setupEvents()` after the mainNav click handler:

```javascript
// Logo click handlers (sidebar + topbar)
document.querySelectorAll('.logo-clickable').forEach(el => {
    el.addEventListener('click', (e) => {
        e.stopPropagation();
        el.classList.toggle('open');
    });
});

// Close dropdowns when clicking outside
document.addEventListener('click', () => {
    document.querySelectorAll('.logo-clickable.open').forEach(el => {
        el.classList.remove('open');
    });
});

// Profile button in dropdowns
document.querySelectorAll('[data-profile="true"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.loadProfileModule();
        // Close all dropdowns
        document.querySelectorAll('.logo-clickable.open').forEach(el => {
            el.classList.remove('open');
        });
    });
});

// Logout buttons
document.getElementById('logoutBtnSidebar')?.addEventListener('click', () => this.logout());
document.getElementById('logoutBtnTopbar')?.addEventListener('click', () => this.logout());
```

- [ ] **Step 6: Add `loadProfileModule` method**

  Add after `loadInitialView` (line 642):

```javascript
loadProfileModule() {
    const viewport = document.getElementById('moduleViewport');
    if (!viewport) return;
    this.showLoader(true);
    const iframe = document.createElement('iframe');
    iframe.src = 'modules/profile/index.html';
    iframe.className = 'module-frame';
    iframe.setAttribute('frameborder', '0');
    iframe.setAttribute('aria-label', 'Meu Perfil');
    viewport.innerHTML = '';
    viewport.appendChild(iframe);
    document.getElementById('activeModuleTitle').textContent = 'Meu Perfil';
    iframe.addEventListener('load', () => {
        this.showLoader(false);
        this.applySkinToIframe(iframe);
    });
}
```

- [ ] **Step 7: Update `updateUserUI` to populate dropdowns**

  Replace the existing `updateUserUI` (line 502) and `updateTopbarUserUI`:

```javascript
updateUserUI(user) {
    const displayName = this.getUserDisplayName(user);
    const roleLabel = this.formatRole(user.role);

    // Sidebar dropdown
    document.getElementById('userNameSidebar').textContent = displayName;
    document.getElementById('userRoleSidebar').textContent = roleLabel;
    document.getElementById('userNameTopbarDropdown').textContent = displayName;
    document.getElementById('userRoleTopbarDropdown').textContent = roleLabel;
}
```

  Remove the `updateTopbarUserUI` method entirely (it was called from `updateUserUI`).

- [ ] **Step 8: Commit**

```bash
git add apps/frontend-webapp/dashboard.js
git commit -m "feat(dashboard): eventos de click no logo, remover theme toggle e password modal"
```

---

### Task 6: Frontend — Add 401 interception to apiService.js

**Files:**
- Modify: `apps/frontend-webapp/shared/apiService.js`

- [ ] **Step 1: Add 401 redirect in `parseResponse`**

  In `parseResponse` (line 44), add 401 handling before the existing `if (!response.ok)` check:

```javascript
// Handle 401 Unauthorized — redirect to login
if (response.status === 401) {
    const url = response.url || '';
    // Don't redirect for login/refresh endpoints (they don't use auth)
    if (!url.includes('/auth/token') && !url.includes('/auth/refresh')) {
        window.grindx.session.clear();
        window.location.href = 'index.html';
        throw new Error('Sessão expirada. Faça login novamente.');
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/shared/apiService.js
git commit -m "feat(api): redirecionar para login ao receber 401 em chamadas autenticadas"
```

---

### Task 7: Frontend — Create profile module (HTML)

**Files:**
- Create: `apps/frontend-webapp/modules/profile/index.html`

- [ ] **Step 1: Create index.html**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meu Perfil</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="../../shared/core.css">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="module-page">
        <div class="profile-container">
            <div class="profile-card">
                <h2><i class="fas fa-user-circle"></i> Meus Dados</h2>
                <form id="profileForm">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Nome de Usuário</label>
                            <input type="text" id="profileUsername" class="form-control" disabled>
                        </div>
                        <div class="form-group">
                            <label>Perfil</label>
                            <input type="text" id="profileRole" class="form-control" disabled>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Nome Completo</label>
                        <input type="text" id="profileName" class="form-control" disabled>
                    </div>
                    <div class="form-group">
                        <label for="profileEmail">E-mail</label>
                        <input type="email" id="profileEmail" class="form-control" required>
                        <span class="field-error" id="emailError" style="display:none;"></span>
                    </div>
                </form>
            </div>

            <div class="profile-card">
                <h2><i class="fas fa-key"></i> Alterar Senha</h2>
                <form id="passwordForm">
                    <div class="form-group">
                        <label for="currentPassword">Senha Atual</label>
                        <input type="password" id="currentPassword" class="form-control" minlength="1">
                    </div>
                    <div class="form-group">
                        <label for="newPassword">Nova Senha</label>
                        <input type="password" id="newPassword" class="form-control" minlength="6">
                    </div>
                    <div class="form-group">
                        <label for="confirmPassword">Confirmar Nova Senha</label>
                        <input type="password" id="confirmPassword" class="form-control" minlength="6">
                    </div>
                    <span class="field-error" id="passwordError" style="display:none;"></span>
                </form>
            </div>

            <div class="profile-card">
                <h2><i class="fas fa-palette"></i> Preferências</h2>
                <div class="form-group">
                    <label>Tema</label>
                    <div class="theme-toggle-group">
                        <button type="button" class="theme-option" data-theme="light">
                            <i class="fas fa-sun"></i> Claro
                        </button>
                        <button type="button" class="theme-option" data-theme="dark">
                            <i class="fas fa-moon"></i> Escuro
                        </button>
                    </div>
                </div>
            </div>

            <div class="profile-actions">
                <button id="saveProfileBtn" class="btn btn-primary"><i class="fas fa-save"></i> Salvar Alterações</button>
            </div>
        </div>
    </div>

    <script src="../../shared/app.js"></script>
    <script src="../../shared/apiService.js"></script>
    <script src="script.js"></script>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/modules/profile/index.html
git commit -m "feat(profile): criar pagina de perfil (HTML)"
```

---

### Task 8: Frontend — Create profile module (CSS)

**Files:**
- Create: `apps/frontend-webapp/modules/profile/style.css`

- [ ] **Step 1: Create style.css**

```css
.module-page {
    padding: 24px;
    max-width: 720px;
    margin: 0 auto;
}

.profile-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.profile-card {
    background: var(--bg-card, #fff);
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: var(--radius-lg, 0.75rem);
    padding: 24px;
    box-shadow: var(--shadow-card, 0 4px 12px rgba(0,0,0,0.06));
}

.profile-card h2 {
    font-size: 1.1rem;
    margin: 0 0 20px;
    color: var(--text-main, #1e293b);
    display: flex;
    align-items: center;
    gap: 8px;
}

.profile-card h2 i {
    color: var(--primary, #00c2e0);
    font-size: 1.2rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.form-group {
    margin-bottom: 16px;
}

.form-group label {
    display: block;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted, #64748b);
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.form-control {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: var(--radius-md, 0.5rem);
    background: var(--bg-main, #f8fafc);
    color: var(--text-main, #1e293b);
    font-size: 0.9rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-sizing: border-box;
}

.form-control:focus {
    outline: none;
    border-color: var(--primary, #00c2e0);
    box-shadow: 0 0 0 3px var(--focus-ring, rgba(0, 194, 224, 0.2));
}

.form-control:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.field-error {
    display: block;
    font-size: 0.78rem;
    color: var(--danger, #ef4444);
    margin-top: 4px;
}

.theme-toggle-group {
    display: flex;
    gap: 12px;
}

.theme-option {
    flex: 1;
    padding: 12px 16px;
    border: 2px solid var(--border-color, #e2e8f0);
    border-radius: var(--radius-md, 0.5rem);
    background: var(--bg-card, #fff);
    color: var(--text-main, #1e293b);
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.theme-option:hover {
    border-color: var(--primary, #00c2e0);
    background: color-mix(in srgb, var(--primary, #00c2e0) 8%, transparent);
}

.theme-option.active {
    border-color: var(--primary, #00c2e0);
    background: color-mix(in srgb, var(--primary, #00c2e0) 12%, transparent);
    color: var(--primary, #00c2e0);
}

.profile-actions {
    display: flex;
    justify-content: flex-end;
    padding-top: 8px;
}

.btn-primary {
    padding: 10px 28px;
    background: var(--primary, #00c2e0);
    color: #fff;
    border: none;
    border-radius: var(--radius-md, 0.5rem);
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s ease;
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-primary:hover {
    background: var(--primary-hover, #00a8c4);
}

.btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

@media (max-width: 600px) {
    .module-page {
        padding: 16px;
    }
    .form-row {
        grid-template-columns: 1fr;
    }
    .profile-card {
        padding: 16px;
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/modules/profile/style.css
git commit -m "feat(profile): criar estilos da pagina de perfil"
```

---

### Task 9: Frontend — Create profile module (script.js)

**Files:**
- Create: `apps/frontend-webapp/modules/profile/script.js`

- [ ] **Step 1: Create script.js**

```javascript
(function initProfile() {
    let currentUser = {};

    async function loadProfile() {
        const profile = await window.grindx.api.get('/auth/me');
        if (!profile) return;
        currentUser = profile;

        document.getElementById('profileUsername').value = profile.username || '';
        document.getElementById('profileRole').value = formatRole(profile.role);
        document.getElementById('profileName').value = profile.nome_completo || '';
        document.getElementById('profileEmail').value = profile.email || '';

        // Set active theme
        const currentTheme = window.grindx.theme.theme;
        document.querySelectorAll('.theme-option').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === currentTheme);
        });
    }

    function formatRole(role) {
        const labels = { admin: 'Administrador', operador: 'Operador', leitura: 'Leitura' };
        return labels[role] || role || 'Usuário';
    }

    function showError(elementId, message) {
        const el = document.getElementById(elementId);
        if (el) {
            el.textContent = message;
            el.style.display = message ? 'block' : 'none';
        }
    }

    async function handleSave() {
        const saveBtn = document.getElementById('saveProfileBtn');
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';

        showError('emailError', '');
        showError('passwordError', '');

        try {
            // 1. Update email if changed
            const newEmail = document.getElementById('profileEmail').value.trim();
            if (newEmail !== currentUser.email) {
                await window.grindx.api.put('/auth/me', { email: newEmail });
                currentUser.email = newEmail;
            }

            // 2. Update password if provided
            const currentPassword = document.getElementById('currentPassword').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            if (currentPassword || newPassword || confirmPassword) {
                if (newPassword !== confirmPassword) {
                    showError('passwordError', 'Nova senha e confirmação não conferem.');
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<i class="fas fa-save"></i> Salvar Alterações';
                    return;
                }
                if (newPassword.length < 6) {
                    showError('passwordError', 'Nova senha deve ter no mínimo 6 caracteres.');
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<i class="fas fa-save"></i> Salvar Alterações';
                    return;
                }
                await window.grindx.api.post('/auth/change-password', {
                    current_password: currentPassword,
                    new_password: newPassword,
                });
                document.getElementById('passwordForm').reset();
            }

            // 3. Update theme
            const selectedTheme = document.querySelector('.theme-option.active')?.dataset.theme;
            if (selectedTheme && selectedTheme !== window.grindx.theme.theme) {
                window.grindx.theme.toggle();
                // If toggle went the wrong way, toggle again
                if (window.grindx.theme.theme !== selectedTheme) {
                    window.grindx.theme.toggle();
                }
            }

            window.parent.postMessage('profile-saved', '*');
            showToast('Alterações salvas com sucesso!', 'success');
        } catch (err) {
            const msg = err.message || 'Erro ao salvar alterações.';
            if (msg.toLowerCase().includes('email') || msg.toLowerCase().includes('e-mail')) {
                showError('emailError', msg);
            } else if (msg.toLowerCase().includes('senha') || msg.toLowerCase().includes('password')) {
                showError('passwordError', msg);
            } else {
                showToast(msg, 'error');
            }
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Salvar Alterações';
        }
    }

    function showToast(message, type) {
        const region = document.getElementById('toastRegion') || (() => {
            const r = document.createElement('div');
            r.id = 'toastRegion';
            r.className = 'toast-region';
            document.body.appendChild(r);
            return r;
        })();
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        region.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    function setupEvents() {
        document.getElementById('saveProfileBtn').addEventListener('click', handleSave);

        document.querySelectorAll('.theme-option').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.theme-option').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        // Keyboard: Enter to save
        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleSave();
                }
            });
        });
    }

    // Listen for theme sync from parent
    window.addEventListener('message', (e) => {
        if (e.data === 'theme-changed') {
            const currentTheme = window.grindx.theme.theme;
            document.querySelectorAll('.theme-option').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.theme === currentTheme);
            });
        }
    });

    document.addEventListener('DOMContentLoaded', () => {
        setupEvents();
        loadProfile();
    });

    // Also run immediately if DOM already loaded
    if (document.readyState !== 'loading') {
        setupEvents();
        loadProfile();
    }
})();
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/modules/profile/script.js
git commit -m "feat(profile): controller do perfil com email, senha e tema"
```

---

### Task 10: Remove password modal from dashboard.html (already done in Task 3 Step 5)

- [ ] **Step 1: Verify password modal is removed**

  Confirm that `#passwordModal` no longer exists in `dashboard.html`. It was removed in Task 3 Step 5.

---

### Task 11: Verify end-to-end

- [ ] **Step 1: Check backend compiles**

Run: `cd apps/api-postgres && python -c "from app.auth.service import AuthService; from app.auth.router import router; print('OK')"`
Expected: `OK`

- [ ] **Step 2: Check frontend files exist**

Run: `Test-Path "apps/frontend-webapp/modules/profile/index.html" -and Test-Path "apps/frontend-webapp/modules/profile/script.js" -and Test-Path "apps/frontend-webapp/modules/profile/style.css"`
Expected: `True`

- [ ] **Step 3: Run lint**

Run: `ruff check --fix apps/` and `ruff format apps/`
Expected: No errors

- [ ] **Step 4: Run backend tests**

Run: `cd apps/api-postgres && set PYTHONPATH=..\..\packages && python -m pytest tests/ -v`
Expected: All existing tests pass
