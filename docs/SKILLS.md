<!-- title: Skills — GrindX | updated: 2026-08-14 -->

# GrindX — Skills do Assistente

Referência de skills úteis para desenvolvimento no projeto GrindX.

---

## Skills Disponíveis

### Módulos e Frontend

| Skill | Local | Uso |
|-------|-------|-----|
| `create-standalone-module` | `.opencode/skills/create-standalone-module/` | **Módulo completo** (backend FastAPI + frontend vanilla JS + testes + migration Alembic) desenvolvido fora do monorepo e exportado via `export.py` |
| `extrair-manual-modulo` | `.opencode/skills/extrair-manual-modulo/` | Gera manuais de uso (perspectiva do usuário final) dos módulos para o Agente de IA, com questionamentos e ciclo de revisão |
| `frontend-design` | `.agents/skills/` | Criar interfaces e componentes com alto padrão de design |

### Qualidade Web

| Skill | Local | Uso |
|-------|-------|-----|
| `accessibility` | `.agents/skills/` | Auditoria e melhoria de acessibilidade (WCAG 2.2) |
| `seo` | `.agents/skills/` | Otimização para buscas |

### Python / Automação

| Skill | Local | Uso |
|-------|-------|-----|
| `python-executor` | `.agents/skills/` | Executar Python em ambiente sandbox (dados, scraping, automação) |
| `python-testing-patterns` | `.agents/skills/` | Estratégias de teste com pytest, fixtures e mocks |

> Skills registradas em `skills-lock.json` (fonte canônica): `accessibility`, `frontend-design`, `python-executor`, `python-testing-patterns`, `seo` (em `.agents/skills/`), além de `create-standalone-module` e `extrair-manual-modulo` (em `.opencode/skills/`).

---

## Design System — Referência Rápida

### Tokens CSS

Disponíveis em `apps/frontend-webapp/shared/core.css`:

```css
--brand-natt: #06090f
--brand-fjord: #0d1e35
--brand-is: #00c2e0
--brand-eld: #ff4d00
--brand-rimfrost: #ddeaf2
--brand-askr: #4a5e72

--skin-primary: #00c2e0
--skin-primary-hover: #00a8c4
--skin-danger: #ef4444
--skin-success: #10b981
--skin-warning: #f59e0b
--skin-bg-main: #f8fafc
--skin-bg-card: #ffffff
--skin-text-main: #1e293b
--skin-text-muted: #64748b

--space-1: 0.25rem
--space-2: 0.5rem
--space-4: 1rem
--space-8: 2rem

--skin-radius-sm: 0.25rem
--skin-radius-md: 0.5rem
--skin-radius-lg: 0.75rem
--skin-radius-xl: 1.5rem

--skin-font-heading: 'Barlow Condensed', 'Arial Narrow', sans-serif
--skin-font-body: 'DM Sans', system-ui, -apple-system, sans-serif
```

Fontes self-hosted em `apps/frontend-webapp/shared/fonts/`: **Barlow Condensed** (400, 700) e **DM Sans** (400, 500, 700).

### Componentes

- `Buttons` — primary, secondary, danger
- `Inputs` — text, email, password
- `Cards` — com glassmorphism
- `Modals` — acessíveis
- `DataTables` — com paginação
- `LoadingSpinners`
- `ToastNotifications`

### Funcionalidades

- Dark/Light mode automático
- Responsivo (mobile, tablet, desktop)
- WCAG AAA compliant
- Glassmorphism effects

### Uso via UIFactory

O `app.js` expõe `window.grindx.ui` com métodos `createButton` e `createInput`:

```html
<!-- 1. Incluir design system -->
<link rel="stylesheet" href="../../shared/core.css">

<!-- 2. Usar componentes via UIFactory -->
<script src="../../shared/config.js"></script>
<script src="../../shared/app.js"></script>

<!-- 3. Criar elementos programaticamente -->
<script>
const botao = window.grindx.ui.createButton({
    text: 'Salvar',
    icon: 'check',
    variant: 'primary',
    onClick: () => console.log('Clicado!'),
    ariaLabel: 'Salvar alterações'
});
document.body.appendChild(botao);

const input = window.grindx.ui.createInput({
    type: 'text',
    label: 'Nome',
    id: 'nome',
    placeholder: 'Digite o nome',
    required: true,
    value: ''
});
document.body.appendChild(input);
</script>
```

---

## Matriz: Skills × Funcionalidades

| Funcionalidade | Skill Principal | Skills Suporte |
|----------------|-----------------|----------------|
| Criar módulo novo | `create-standalone-module` | `frontend-design` |
| Design System | `frontend-design` | — |
| Componentes UI | `frontend-design` | — |
| Dashboard Visual | `frontend-design` | — |
| Acessibilidade | `accessibility` | `frontend-design` |
| SEO | `seo` | — |
| Testes Python | `python-testing-patterns` | — |
| Automação/Scraping | `python-executor` | — |

---

## Ordem de Prioridade

### Crítico

1. `create-standalone-module` — Essencial para criar módulos completos
2. `frontend-design` — UI components e design system

### Importante

3. `python-testing-patterns` — Qualidade dos testes
4. `accessibility` — Acessibilidade (WCAG)
5. `seo` — Otimização para buscas

### Opcional

6. `python-executor` — Automação e processamento de dados