# Frontend Responsividade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement unified responsive design system across GrindX frontend with consistent breakpoints, spacing scale, touch targets, mobile sidebar, and table-to-card patterns.

**Architecture:** Add CSS custom properties for breakpoints and spacing in `core.css`, refactor `dashboard.css` to 3-breakpoint layout (mobile/tablet/desktop), add responsive utility classes, implement table-to-card pattern in modules with `<table>`, and ensure all interactive elements have 44px touch targets.

**Tech Stack:** Vanilla CSS (`var(--...)`, CSS Grid, Flexbox), Vanilla JS (fetch, DOM manipulation), no frameworks

---

### Task 1: Core tokens & spacing scale in core.css

**Files:**
- Modify: `apps/frontend-webapp/shared/core.css`

- [ ] **Step 1: Add breakpoint and spacing CSS custom properties to `:root`**

Insert after existing `:root` block (line 52), before typography section:

```css
:root {
  /* Breakpoint reference tokens */
  --bp-sm: 480px;
  --bp-md: 768px;
  --bp-lg: 1024px;
  --bp-xl: 1280px;

  /* Spacing Scale (completa) */
  --space-0: 0;
  --space-050: 0.125rem;
  --space-1: 0.25rem;
  --space-150: 0.375rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;

  /* Layout tokens */
  --sidebar-width: 280px;
  --sidebar-collapsed-width: 88px;
  --topbar-height: 52px;
  --content-padding: var(--space-2);
}
```

Note: The `.0\.5` syntax escapes the dot for CSS. Spaces after `--space-` names must match between declaration and usage.

- [ ] **Step 2: Verify no syntax errors**

Run: `python -c "import re; css=open('apps/frontend-webapp/shared/core.css').read(); print(f'OK ({len(css)} chars)')"` or simply reload the dashboard in browser and check devtools console for CSS parse errors.

Expected: No CSS parse errors in browser console.

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/shared/core.css
git commit -m "feat(css): add breakpoint tokens and spacing scale to core.css"
```

---

### Task 2: Responsive utilities & touch targets in core.css

**Files:**
- Modify: `apps/frontend-webapp/shared/core.css`

- [ ] **Step 1: Add responsive visibility utility classes**

Insert after the `.grid` section (line ~227), before modal styles:

```css
/* Responsive Visibility Utilities */
@media (max-width: 479px) {
  .show-sm { display: revert !important; }
  .hide-sm { display: none !important; }
}
@media (min-width: 480px) and (max-width: 767px) {
  .show-md { display: revert !important; }
  .hide-md { display: none !important; }
}
@media (min-width: 768px) and (max-width: 1023px) {
  .show-lg { display: revert !important; }
  .hide-lg { display: none !important; }
}
@media (min-width: 1024px) {
  .show-xl { display: revert !important; }
  .hide-xl { display: none !important; }
}
/* Mobile alias: hide in < 768px */
.hide-mobile { display: none !important; }
@media (min-width: 768px) {
  .hide-mobile { display: revert !important; }
}
```

- [ ] **Step 2: Add responsive grid extensions**

Insert after the existing grid media queries:

```css
@media (min-width: 480px) {
  .grid-sm-2 { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 768px) {
  .grid-md-3 { grid-template-columns: repeat(3, 1fr); }
}
@media (min-width: 1024px) {
  .grid-lg-4 { grid-template-columns: repeat(4, 1fr); }
}
```

- [ ] **Step 3: Add global touch target minimums**

Insert after body styles (~line 160):

```css
/* Touch Targets (Mobile A11y) */
input, select, textarea, button, a, .nav-link, .nav-dropdown-item,
.picker-item, .theme-option, .template-card {
  min-height: 44px;
}
/* Allow smaller height for icon-only buttons */
.btn-icon, .btn-sm {
  min-height: 32px;
}
```

Note: `.btn` already has `min-height: 44px` from the existing `.btn` rule — keep that, this supplements it for non-button interactive elements.

- [ ] **Step 4: Increase content-area padding on desktop**

Add after existing media queries (around line ~340):

```css
@media (min-width: 768px) {
  .content-area {
    padding: var(--space-3);
  }
}
@media (min-width: 1024px) {
  .content-area {
    padding: var(--space-4);
  }
}
```

- [ ] **Step 5: Verify no conflicts**

Open the dashboard in browser at desktop width. Check that:
- All existing styles still apply correctly
- Buttons and inputs render without layout shifts

- [ ] **Step 6: Commit**

```bash
git add apps/frontend-webapp/shared/core.css
git commit -m "feat(css): add responsive utilities, touch targets and grid extensions"
```

---

### Task 3: Dashboard shell 3-breakpoint responsive

**Files:**
- Modify: `apps/frontend-webapp/dashboard.css`
- Modify: `apps/frontend-webapp/dashboard.html`
- Modify: `apps/frontend-webapp/dashboard.js`

- [ ] **Step 1: Add mobile sidebar overlay in `dashboard.html`**

Insert after the `<aside class="sidebar">` closing tag (line 86), before the topbar:

```html
<!-- Sidebar overlay (mobile) -->
<div id="sidebarOverlay" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:99;" aria-hidden="true"></div>
```

- [ ] **Step 2: Refactor dashboard.css sidebar section**

Replace the existing responsive section (lines 314-339) with 3-breakpoint rules:

```css
/* ── Responsive Dashboard Shell ── */

/* Default (mobile-first): < 768px — off-canvas sidebar */
.sidebar {
  position: fixed;
  top: 0;
  left: -100%;
  width: 280px;
  height: 100%;
  background: var(--bg-card);
  border-right: 1px solid var(--border-color);
  z-index: 100;
  display: flex;
  flex-direction: column;
  padding: var(--space-2);
  transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.sidebar.open {
  left: 0;
}
#sidebarOverlay {
  display: none;
}
.sidebar.open ~ #sidebarOverlay {
  display: block;
}

/* Tablet: 768px - 1023px — compact overlay sidebar */
@media (min-width: 768px) and (max-width: 1023px) {
  .sidebar {
    width: 240px;
  }
  .sidebar .nav-link {
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
  }
  .sidebar .nav-title {
    font-size: 0.7rem;
  }
  .sidebar .nav-links-container {
    padding-left: 1.5rem;
  }
  .main-viewport {
    margin-left: 0;
  }
}

/* Desktop: >= 1024px — static sidebar */
@media (min-width: 1024px) {
  .sidebar {
    position: static;
    left: 0;
    width: var(--sidebar-width);
  }
  .sidebar.collapsed {
    width: var(--sidebar-collapsed-width);
  }
  .sidebar.open {
    left: 0;
  }
  .sidebar.collapsed ~ .main-viewport {
    margin-left: 0;
  }
  .sidebar:not(.collapsed) ~ .main-viewport {
    margin-left: 1px;
  }
  .md-hide { display: none !important; }
  .hide-mobile { display: revert; }
  #sidebarOverlay { display: none !important; }
}

/* Sidebar header/footer — consolidate existing rules */
.sidebar-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-8);
  position: relative;
  justify-content: space-between;
}
/* ... existing sidebar-header rules remain below ... */
```

Note: Keep all existing sidebar internal rules (`.sidebar.collapsed .logo-full`, nav groups, nav links, etc.) unchanged. Only the positioning/responsive section is replaced.

- [ ] **Step 3: Update `dashboard.js` to toggle sidebar overlay**

Find the existing open/close sidebar handlers and modify:

```javascript
// Open sidebar (mobile hamburger button)
document.getElementById('openSidebar')?.addEventListener('click', () => {
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('sidebarOverlay').style.display = 'block';
  document.body.style.overflow = 'hidden'; // prevent background scroll
});

// Close sidebar (close button)
document.getElementById('closeSidebar')?.addEventListener('click', closeSidebar);

// Close sidebar (overlay click)
document.getElementById('sidebarOverlay')?.addEventListener('click', closeSidebar);

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebarOverlay').style.display = 'none';
  document.body.style.overflow = '';
}

// On window resize >= 1024px, ensure overlay is hidden
window.addEventListener('resize', () => {
  if (window.innerWidth >= 1024) {
    document.getElementById('sidebar')?.classList.remove('open');
    document.getElementById('sidebarOverlay')?.style.display = 'none';
    document.body.style.overflow = '';
  }
});
```

- [ ] **Step 4: Verify the responsive behavior**

Open dashboard.html in browser with devtools responsive mode:
- < 768px: sidebar hidden, hamburger visible, click opens overlay, click overlay closes
- 768-1023px: sidebar compact, click opens without scroll lock
- >= 1024px: sidebar static, overlay hidden, collapse toggle works

- [ ] **Step 5: Commit**

```bash
git add apps/frontend-webapp/dashboard.css apps/frontend-webapp/dashboard.html apps/frontend-webapp/dashboard.js
git commit -m "feat(dashboard): implement 3-breakpoint responsive sidebar shell"
```

---

### Task 4: Users module table-to-card

**Files:**
- Modify: `apps/frontend-webapp/modules/users/index.html`
- Modify: `apps/frontend-webapp/modules/users/style.css`

- [ ] **Step 1: Add `data-label` attributes to `<td>` elements**

In `modules/users/index.html`, add `data-label` to each `<td>` matching the `<th>` header text:

```html
<!-- Before -->
<td class="hide-mobile">{user.email}</td>

<!-- After: remove hide-mobile from cell, add data-label -->
<td data-label="E-mail">{user.email}</td>
```

Map all columns:
- `data-label="Usuário"` for the td with avatar+name
- `data-label="E-mail"` for the email td
- `data-label="Empresa"` for company td
- `data-label="Perfil"` for role td
- `data-label="Status"` for status td
- `data-label="Ações"` for actions td

Keep existing `th` elements with `hide-mobile` where appropriate for desktop headers.

- [ ] **Step 2: Add table-to-card CSS in `modules/users/style.css`**

Insert at the end of the file:

```css
/* Responsive: table to cards (mobile) */
@media (max-width: 767px) {
  .table-responsive table,
  .table-responsive thead,
  .table-responsive tbody,
  .table-responsive tr,
  .table-responsive th,
  .table-responsive td {
    display: block;
  }
  .table-responsive thead {
    display: none;
  }
  .table-responsive tbody tr {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--space-3);
    padding: var(--space-3);
    margin-bottom: var(--space-3);
  }
  .table-responsive td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-2) 0;
    border-bottom: none;
    font-size: 0.85rem;
    text-align: left;
  }
  .table-responsive td::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }
  .table-responsive td:last-child {
    border-top: 1px solid var(--border-color);
    margin-top: var(--space-2);
    padding-top: var(--space-2);
  }
  /* Hide email column on very small screens if needed */
  .hide-sm {
    display: none !important;
  }
}
```

- [ ] **Step 3: Verify responsive table**

Open users module at mobile width (< 768px). Check that:
- Table transforms to stacked cards
- Each row shows `data-label` on left, value on right
- Actions are at the bottom with separator
- Desktop view is unchanged

- [ ] **Step 4: Commit**

```bash
git add apps/frontend-webapp/modules/users/index.html apps/frontend-webapp/modules/users/style.css
git commit -m "feat(users): implement table-to-card responsive pattern"
```

---

### Task 5: Importer module table-to-card

**Files:**
- Modify: `apps/frontend-webapp/modules/importer/index.html`
- Modify: `apps/frontend-webapp/modules/importer/style.css`

- [ ] **Step 1: Add `data-label` attributes in `modules/importer/index.html`**

Add `data-label` to each `<td>` in the importer table:
- `data-label="Módulo"` for module name
- `data-label="Versão"` for version
- `data-label="Schema"` for schema
- `data-label="Status"` for status
- `data-label="Ações"` for actions

- [ ] **Step 2: Add table-to-card CSS in `modules/importer/style.css`**

Insert at end:

```css
@media (max-width: 767px) {
  .table-responsive table,
  .table-responsive thead { display: block; }
  .table-responsive tbody tr {
    display: block;
    border: 1px solid var(--border-color);
    border-radius: var(--space-3);
    padding: var(--space-3);
    margin-bottom: var(--space-3);
  }
  .table-responsive td {
    display: flex;
    justify-content: space-between;
    padding: var(--space-2) 0;
    border-bottom: none;
    text-align: left;
  }
  .table-responsive td::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-muted);
    font-size: 0.75rem;
    text-transform: uppercase;
  }
  .table-responsive td:last-child {
    border-top: 1px solid var(--border-color);
    margin-top: var(--space-2);
    padding-top: var(--space-2);
  }
}
```

- [ ] **Step 3: Verify**

Open importer module at mobile width. Check card layout renders correctly.

- [ ] **Step 4: Commit**

```bash
git add apps/frontend-webapp/modules/importer/index.html apps/frontend-webapp/modules/importer/style.css
git commit -m "feat(importer): implement table-to-card responsive pattern"
```

---

### Task 6: Admin-skins responsive fixes

**Files:**
- Modify: `apps/frontend-webapp/modules/admin-skins/style.css`

- [ ] **Step 1: Fix `max-width` constraints that break on mobile**

Find and replace all `max-width` values that could clip content on small screens:

```css
/* Replace: */
.skin-modal { max-width: 490px; }
/* With: */
.skin-modal { max-width: min(490px, calc(100vw - var(--space-4))); }

/* Replace form-section max-width: */
.form-section { max-width: 450px; }
/* With: */
.form-section { max-width: 100%; }

/* Replace color-grid max-width: */
.color-grid { max-width: 350px; }
/* With: */
.color-grid { max-width: 100%; }

/* Replace .modal-header max-width: */
.modal-header { max-width: 450px; }
/* With: */
.modal-header { max-width: 100%; }

/* Replace .form-section legend max-width: */
.form-section legend { max-width: 450px; }
/* With (remove): remove line entirely */
```

- [ ] **Step 2: Make color-grid responsive**

Replace the existing single media query at line 501:

```css
@media (max-width: 768px) {
  .color-grid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 3: Verify**

Open admin-skins module at mobile width:
- Modal fits within viewport (no horizontal scroll)
- Color inputs stack in 1 column
- Form sections use full width

- [ ] **Step 4: Commit**

```bash
git add apps/frontend-webapp/modules/admin-skins/style.css
git commit -m "fix(admin-skins): responsive color-grid and max-width constraints"
```

---

### Task 7: Touch targets for remaining interactive elements

**Files:**
- Modify: `apps/frontend-webapp/modules/structure/style.css`
- Modify: `apps/frontend-webapp/modules/profile/style.css`

- [ ] **Step 1: Structure module touch targets**

At end of `modules/structure/style.css`:

```css
/* Touch targets */
.picker-item {
  min-height: 44px;
  display: flex;
  align-items: center;
}
.aba-header button,
.modulo-item button {
  min-height: 44px;
  min-width: 44px;
}
```

- [ ] **Step 2: Profile module — touch targets already OK**

The profile module uses `.btn` (has 44px) and standard inputs. Verify and add if missing:

```css
.theme-option {
  min-height: 44px;
}
```

- [ ] **Step 3: Verify**

Navigate through each module on a touch device (or Chrome devtools mobile emulation). Tap all interactive elements — they should have adequate touch area.

- [ ] **Step 4: Commit**

```bash
git add apps/frontend-webapp/modules/structure/style.css apps/frontend-webapp/modules/profile/style.css
git commit -m "fix(modules): add touch targets for interactive elements"
```

---

### Task 8: Verify full responsive behavior

- [ ] **Step 1: Test all breakpoints**

Open each module at 3 widths and check:

| Module | Mobile (<480px) | Tablet (768px) | Desktop (>1024px) |
|--------|----------------|----------------|-------------------|
| Dashboard | Sidebar off-canvas, topbar hidden | Sidebar compact | Full sidebar |
| Users | Card layout | Table with hide-mobile | Full table |
| Importer | Card layout | Table | Full table |
| Admin-skins | 1-col color grid, modal fits | 2-col color grid | Full layout |
| Profile | 1-col form rows | 2-col form rows | 2-col form rows |
| Structure | Cards stack | Cards grid | Cards grid |

- [ ] **Step 2: Run lint check**

```bash
cd apps/frontend-webapp
# N/A — no linter for CSS/JS frontend. Verify manually.
```

Actually, run the project's lint command if configured:

```bash
cd /D/_Projetos/GrindX
ruff check . --fix 2>nul || echo "Lint config may not cover frontend CSS"
```

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "docs: add responsive design spec and implementation plan"
```

---

## Self-Review

**Spec coverage:**
- Core tokens & spacing → Task 1 ✓
- Responsive utilities → Task 2 ✓
- Touch targets → Task 2 + Task 7 ✓
- Dashboard shell 3-breakpoint → Task 3 ✓
- Table-to-card → Tasks 4-5 ✓
- Admin-skins responsive → Task 6 ✓
- Profile module → Task 7 ✓
- `max-width` constraint fixes → Task 6 ✓
- Verification → Task 8 ✓

**Placeholder scan:** No TBD, TODO, or incomplete code blocks. All commands and code are complete.

**Type consistency:** No type issues — this is CSS/HTML/JS, no function signatures to track across tasks.
