<!-- title: Skills — GrindX | updated: 2026-05-26 -->

# GrindX — Skills do Assistente

Referência de skills úteis para desenvolvimento no projeto GrindX.

---

## Skills por Categoria

### Frontend Development

| Skill | Uso |
|-------|-----|
| `frontend-design` | Criar novos módulos, componentes e interfaces |
| `create-module` | **CRUD completo** (backend + frontend + banco) com templates prontos |

### Documentação e Relatórios

| Skill | Uso |
|-------|-----|
| `docx` | Gerar manuais e guias em Word |
| `pdf` | Criar relatórios em PDF |

### Processamento de Dados

| Skill | Uso |
|-------|-----|
| `xlsx` | Importar/exportar planilhas Excel |
| `file-reading` | Processar e validar uploads |
| `pdf-reading` | Extrair dados de documentos PDF |

---

## Design System — Referência Rápida

### Tokens CSS

Disponíveis em `packages/frontend-webapp/shared/core.css`:

```css
--color-primary: #5D63F5
--color-success: #10B981
--color-warning: #F59E0B
--color-error: #EF4444
--spacing-sm: 8px
--spacing-md: 16px
--spacing-lg: 24px
--border-radius: 8px
--font-family: 'Inter', sans-serif
```

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

### Uso

```html
<!-- 1. Incluir design system -->
<link rel="stylesheet" href="../../shared/core.css">

<!-- 2. Usar componentes via UIFactory -->
<script src="../../shared/app.js"></script>

<!-- 3. Criar elementos programaticamente -->
<script>
const botao = window.grindx.ui.createButton({
    label: 'Salvar',
    type: 'primary',
    onClick: () => console.log('Clicado!')
});
document.body.appendChild(botao);
</script>
```

---

## Matriz: Skills × Funcionalidades

| Funcionalidade | Skill Principal | Skills Suporte |
|----------------|-----------------|----------------|
| Criar módulo novo | `create-module` | `frontend-design` |
| Design System | `frontend-design` | — |
| Componentes UI | `frontend-design` | — |
| Dashboard Visual | `frontend-design` | — |
| Guia de Usuário | `docx` | `file-reading` |
| Relatório Executivo | `docx` | `xlsx` |
| Exportar para PDF | `pdf` | `xlsx` |
| Importar Excel | `xlsx` | `file-reading` |
| Processar PDF | `pdf-reading` | `file-reading` |
| Validar Dados | `file-reading` | — |

---

## Ordem de Prioridade

### Crítico

1. `create-module` — Essencial para criar módulos completos
2. `frontend-design` — UI components e design system
3. `file-reading` — Essencial para imports

### Importante

3. `docx` — Documentação
4. `xlsx` — Exportação de dados
5. `pdf` — Relatórios
6. `pdf-reading` — Processamento de docs

### Opcional

7. `web-artifacts-builder` — Artifacts avançados
8. `skill-creator` — Skills customizadas
