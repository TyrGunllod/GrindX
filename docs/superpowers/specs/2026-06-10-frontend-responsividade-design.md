# Frontend Responsividade — Design System

> **Fase 4:** GrindX Frontend Responsiveness
> **Data:** 2026-06-10
> **Status:** Aprovado

## Resumo

Implementar um sistema unificado de responsividade mobile-first no frontend GrindX, com breakpoints padronizados, spacing scale ampliada, utilities responsivas centralizadas em `core.css`, dashboard shell adaptável em 3 breakpoints, e padrão table-to-card para módulos com dados tabulares.

## Abordagem

**Unified Breakpoint System + CSS Custom Properties** — Adicionar variáveis CSS de breakpoint, spacing scale completa, e utilities responsivas no `core.css`. Cada módulo herda sem media queries próprias.

## Tokens CSS

### Breakpoints

| Variável | Valor | Alvo |
|----------|-------|------|
| `--bp-sm` | 480px | Mobile landscape |
| `--bp-md` | 768px | Tablet portrait |
| `--bp-lg` | 1024px | Desktop |
| `--bp-xl` | 1280px | Wide |

### Spacing Scale

Ampliar de `--space-1/2/4/8` para escala completa: `space-0, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 16`.

### Layout Tokens

| Variável | Default | Descrição |
|----------|---------|-----------|
| `--sidebar-width` | 280px | Largura sidebar expandida |
| `--sidebar-collapsed-width` | 88px | Largura sidebar colapsada |
| `--topbar-height` | 52px | Altura topbar |
| `--content-padding` | `--space-2` | Padding conteúdo (responsivo) |

## Utilities Responsivas

Centralizar em `core.css` classes de visibility por breakpoint:
- `.hide-sm`, `.show-sm`, `.hide-md`, `.show-md`, `.hide-lg`, `.show-lg`, `.hide-xl`, `.show-xl`
- Manter `.hide-mobile` como alias para `.hide-sm` + `.hide-md`
- Grid extensions: `.grid-sm-2`, `.grid-md-3`, `.grid-lg-4`

## Dashboard Shell

### Mobile (< 768px)
- Sidebar off-canvas com overlay escuro
- Topbar oculto
- Botão hamburger no content-area
- Content padding reduzido

### Tablet (768px - 1023px)
- Sidebar overlay sem backdrop, largura 240px
- Navegação compacta (font-size menor, padding reduzido)
- Topbar oculto

### Desktop (>= 1024px)
- Sidebar estática (comportamento atual)
- Topbar visível em `layout-topbar`
- Collapse sidebar funciona normalmente

## Table-to-Card Pattern

Tables se transformam em cards no mobile usando `display: block` + pseudo-elemento `::before` com `data-label`.

```css
@media (max-width: 767px) {
  .table-responsive thead { display: none; }
  .table-responsive tr {
    display: block;
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    padding: var(--space-3);
    margin-bottom: var(--space-3);
  }
  .table-responsive td {
    display: flex;
    justify-content: space-between;
    padding: var(--space-2) 0;
  }
  .table-responsive td::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-muted);
    font-size: 0.75rem;
    text-transform: uppercase;
  }
}
```

## Touch Targets

Garantir `min-height: 44px` em todos elementos interativos:
- `.btn` (já existe)
- `input`, `select`, `textarea`
- Dropdown items (`.nav-dropdown-item`)
- Navigation links (`.nav-link`)
- Picker items (`.picker-item`)

## Adaptação por Módulo

| Módulo | Mudanças |
|--------|----------|
| **Users** | Adicionar `data-label` nas `<td>`, table-to-card |
| **Profile** | Mínima (já tem 600px breakpoint), touch targets |
| **Admin-Skins** | `color-grid` → 1 col no mobile, remover `max-width` fixos |
| **Structure** | Cards já empilham verticalmente, touch targets |
| **Importer** | Adicionar `data-label` nas `<td>`, table-to-card |
| **Home** | Verificar conteúdo existente e adaptar |

## Arquivos Afetados

- `apps/frontend-webapp/shared/core.css` — tokens, spacing, utilities, touch targets
- `apps/frontend-webapp/dashboard.css` — shell responsivo
- `apps/frontend-webapp/dashboard.js` — overlay sidebar toggle
- `apps/frontend-webapp/dashboard.html` — overlay element
- `apps/frontend-webapp/modules/users/index.html` — data-label
- `apps/frontend-webapp/modules/users/style.css` — table-to-card
- `apps/frontend-webapp/modules/importer/index.html` — data-label
- `apps/frontend-webapp/modules/importer/style.css` — table-to-card
- `apps/frontend-webapp/modules/admin-skins/style.css` — responsive color-grid
- `apps/frontend-webapp/modules/profile/style.css` — touch targets
- `apps/frontend-webapp/modules/structure/style.css` — touch targets

## Não Escopo

- Migração para framework JS
- Async SQLAlchemy
- Redis cache
- Novos módulos
- Mudanças no backend
