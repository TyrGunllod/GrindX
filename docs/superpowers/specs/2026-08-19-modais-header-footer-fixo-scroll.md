# Design — Modais com header/footer fixos e scroll apenas no conteúdo central

**Data:** 2026-08-19
**Status:** Aprovado pelo usuário
**Escopo:** `apps/frontend-webapp/` (módulos padrão) + skill `create-standalone-module`

---

## 1. Contexto e problema

Os modais dos módulos padrão do GrindX não têm um padrão único de scroll interno. Alguns já seguem o layout correto (header/footer fixos, conteúdo central scrollável), outros scrollam o card inteiro (header/footer somem) ou não têm limite de altura (o modal estoura a viewport).

**Objetivo:** em todos os modais dos módulos padrão e nos módulos gerados pela skill `create-standalone-module`, o header e o footer devem permanecer sempre visíveis (não somem no scroll) e apenas o conteúdo entre eles deve rolar.

---

## 2. Estado atual — inventário

### 2.1 Modais que JÁ seguem o padrão
| Módulo | Modal | Onde |
|---|---|---|
| `users` | `permissoesModal` | `#permissoesContent` com `flex:1; overflow-y:auto` (`modules/users/style.css:124-138`) |
| `users` | `userModal` | `.modal-scroll` com `flex:1; overflow-y:auto` (`modules/users/style.css:290-302`) |
| `admins` | `userModal` | reusa `modules/users/style.css` |
| `structure` | `pickerModal` (dinâmico) | `.picker-list` com `flex:1; overflow-y:auto` (`modules/structure/style.css:155-176`) |

### 2.2 Modais que NÃO seguem o padrão
| Módulo | Modal | Problema | Referência |
|---|---|---|---|
| `structure` | `abaModal`, `moduloModal` | `.structure-modal` com `max-height:90vh; overflow-y:auto` no card inteiro (header/footer somem) | `modules/structure/style.css:114-118` |
| `importer` | `importModal` | `.modal-body` sem max-height; usa `.modal` (raiz) sem scroll | `modules/importer/index.html:74-86` |
| `profile` | `passwordModal`, `preferencesModal` | `.modal-dialog` com `max-height:90vh; overflow-y:auto` no diálogo inteiro | `modules/profile/style.css:234-242` |
| `admin-skins` | `skinModal` | `.skin-modal` com `max-height:90vh; overflow-y:auto` no card inteiro | `modules/admin-skins/style.css:75-80` |
| `admin-skins` | `templateModal` | `.template-modal` sem max-height (pode estourar a tela) | `modules/admin-skins/style.css:396-398` |
| `index.html` (login) | `forgotModal` | usa `.modal` (raiz) sem limite de altura; sem footer | `index.html:76-99`, `style.css:98-106` |

### 2.3 Classes de container de modal em uso
- `.modal-card` — `shared/core.css` (módulos em geral)
- `.modal` — `style.css` raiz (login, importer) — cantos `1.5rem`, `max-width: 400px`, borda, padding `space-4`
- `.modal-dialog` — `modules/profile/style.css` — `max-width: 440px`

---

## 3. Decisões (confirmadas com o usuário)

1. **Escopo:** padronizar TODOS os modais dos módulos padrão, inclusive os que já funcionam (`users`, `admins`, picker do `structure`).
2. **Abordagem:** padrão compartilhado no `shared/core.css` (não fixes por módulo, não via JS no `ReusableModal.js`).
3. **Mobile:** em telas `< 768px`, os modais viram bottom-sheet full-screen (overlay sem padding, card alinhado à base, cantos superiores arredondados, altura ~92vh).
4. **`.modal` (login/importer):** manter o visual atual (cantos `1.5rem`, `max-width: 400px`, borda), aplicando apenas o padrão de layout (flex + scroll central). O `forgotModal` do login também vira bottom-sheet no mobile.
5. **Classe única:** o container central scrollável passa a ser uma classe única compartilhada `.modal-content`.
6. **Skill `create-standalone-module`:** aplicar o mesmo padrão nos templates e documentar no `SKILL.md`.
7. **Skill standalone — estrutura `shared`:** o fallback do frontend (core.css, config.js, app.js) sai de `frontend/{tab}/shared/` e passa a **coexistir na pasta `shared/` da raiz do módulo**, junto do pacote Python (`__init__.py`, `exceptions/`, `schemas/`). O `make dev-frontend` passa a servir a raiz do módulo.

---

## 4. Design

### 4.1 Padrão compartilhado em `apps/frontend-webapp/shared/core.css`

Regras de layout adicionadas às classes de container de modal existentes (mantendo `max-width`, `border-radius` e `padding` atuais de cada uma):

```css
.modal-card, .modal, .modal-dialog {
    display: flex;
    flex-direction: column;
    max-height: 90vh;
}

.modal-header, .modal-footer {
    flex-shrink: 0;   /* nunca somem no scroll */
}

.modal-content {
    flex: 1;
    min-height: 0;                 /* obrigatório para o flex scroll funcionar */
    overflow-y: auto;
    scrollbar-gutter: stable;      /* evita layout shift ao abrir scrollbar */
}
```

**Mobile bottom-sheet (`< 768px`):**

```css
@media (max-width: 767px) {
    .modal-overlay {
        padding: 0;
        align-items: flex-end;     /* alinha à base da tela */
    }
    .modal-card, .modal, .modal-dialog {
        width: 100%;
        max-width: 100%;
        max-height: 92vh;
        border-radius: 1rem 1rem 0 0;   /* apenas cantos superiores */
    }
}
```

> **Specificity — login:** `apps/frontend-webapp/style.css` é carregado depois do `core.css` e redefine `.modal-overlay { padding: var(--space-4); }`. O media query do bottom-sheet no `core.css` precisa vencer essa regra. Estratégia escolhida: **remover do `style.css` do login os blocos duplicados** de `.modal-overlay`, `.modal-header` e `.modal-close` (que são cópias do `core.css`), deixando no `style.css` apenas os overrides visuais de `.modal` (`max-width: 400px`, `border-radius: 1.5rem`, `border`, `padding: var(--space-4)`). Assim o media query do `core.css` vale para o login sem conflito.

> **Comportamento com conteúdo curto:** com flex column, o footer fica logo após o conteúdo (não fixo na base da tela). Isso é o comportamento esperado — header/footer ficam fixos (não somem) e só o meio rola quando o conteúdo excede `max-height`.

### 4.2 Alterações HTML por módulo (adicionar `.modal-content` ao elemento central)

| Módulo/arquivo | Modal | Elemento central |
|---|---|---|
| `index.html` (login) | `forgotModal` | `<form id="forgotForm">` → `class="modal-content"` |
| `modules/structure/index.html` | `abaModal`, `moduloModal` | `<form id="abaForm">` e `<form id="moduloForm">` (hoje `class="p-4"`) → `.modal-content` |
| `modules/structure/script.js` | `pickerModal` (dinâmico) | `#pickerList` → adicionar `.modal-content` |
| `modules/users/index.html` | `permissoesModal` | `#permissoesContent` (mantém `py-4`) → adicionar `.modal-content` |
| `modules/users/index.html` | `userModal` | `.modal-scroll` → converter para `.modal-content` |
| `modules/admins/index.html` | `userModal` | `.modal-scroll` → converter para `.modal-content` (herda `users/style.css`) |
| `modules/importer/index.html` | `importModal` | `#modalBody` → adicionar `.modal-content` |
| `modules/profile/index.html` | `passwordModal`, `preferencesModal` | `.modal-body` → converter para `.modal-content` |
| `modules/admin-skins/index.html` | `skinModal` | `#skinForm.skin-form` → adicionar `.modal-content` |
| `modules/admin-skins/index.html` | `templateModal` | `.modal-body` (contém `.template-grid`) → converter para `.modal-content` |

### 4.3 Limpeza de CSS por módulo

Remover os overrides que duplicam o comportamento agora compartilhado (mantendo largura/padding específicos de cada módulo):

- `modules/structure/style.css:114-118` — `.structure-modal`: remover `overflow-y:auto` e `max-height:90vh` (regra compartilhada do `core.css` cobre), manter `scrollbar-gutter` se desejado
- `modules/admin-skins/style.css:75-80` — `.skin-modal`: remover `overflow-y:auto`, manter `max-width`
- `modules/admin-skins/style.css:396-398` — `.template-modal`: sem max-height (herda o compartilhado)
- `modules/profile/style.css:234-242` — `.modal-dialog`: remover `overflow-y:auto`/`max-height`, manter `max-width: 440px`
- `modules/users/style.css:124-138` (`#permissoesModal`) e `290-302` (`.modal-card-wide`/`.modal-scroll`) — remover regras que agora vêm do compartilhado; manter overrides de **largura** (`max-width: 720px`) e **padding** do header/footer do `userModal`
- `modules/structure/style.css:168-176` — `.picker-list`: remover `flex:1; overflow-y:auto; max-height:50vh` duplicados (mantém `flex-direction`/gap/padding)

**Cuidado:** `modules/admins/index.html` carrega `../users/style.css` — mudanças nesse arquivo afetam `admins` e `users` simultaneamente.

### 4.4 Skill `create-standalone-module` — padrão de modal

- `templates/shared/frontend/index.html`: o `<form id="form-entity">` passa a `class="modal-content grid grid-md-2"` (mantém `id` e grid)
- `templates/shared/standalone/shared/core.css` (fallback standalone — novo local, ver seção 4.5): espelhar o padrão da seção 4.1 — `.modal-card` com flex column + `max-height:90vh`, `.modal-header`/`.modal-footer` com `flex-shrink:0`, nova `.modal-content`, media query `< 768px` bottom-sheet
- `SKILL.md`: atualizar o snippet "Estrutura padrão do modal" (linhas ~347-364) para incluir `.modal-content`, e registrar que header/footer fixos + scroll central vêm do `core.css` (não duplicar no `style.css` do módulo)

### 4.5 Skill `create-standalone-module` — `shared/` na raiz do módulo (standalone)

**Estado atual (incorreto para o objetivo):**
- `SKILL.md` árvore (linhas ~135-143): fallback `shared/` **dentro de** `frontend/{tab}/shared/`
- `SKILL.md` nota (linha 27): fallback standalone dentro do frontend, "não copiado no export"
- `Makefile` template: `dev-frontend` → `cd frontend/{frontend_prefix}_* && python -m http.server 7080` (web root = aba do frontend)

**Estado desejado:**
- O fallback do frontend (`core.css`, `config.js`, `app.js`) fica na **raiz do módulo**, na pasta `shared/`, **coexistindo** com o pacote Python (`__init__.py`, `exceptions/`, `schemas/`). Ambos são fallbacks standalone e a pasta inteira é excluída do export.
- `Makefile` template: `dev-frontend` serve a **raiz do módulo** (`python -m http.server 7080` na raiz), para `/shared/core.css`, `/shared/config.js` e `/shared/app.js` resolverem para `{module_root}/shared/`.
- `SKILL.md`: atualizar árvore, notas (linha 27) e referências de template de `templates/shared/frontend/shared/*`
- Mover os templates de fallback de `templates/shared/frontend/shared/` para `templates/shared/standalone/shared/` (agrupando com os demais arquivos de raiz do standalone) e atualizar as referências no `SKILL.md`.

> **Observação:** servir a raiz do módulo expõe o código Python do backend via HTTP no `dev-frontend` standalone. Aceitável em ambiente de desenvolvimento standalone; registrar no `SKILL.md`.

---

## 5. Cross-impact no monorepo

- `apps/api-postgres/scripts/import_module.py:200-202` — `copy_frontend` ignora `frontend/shared`. Com o fallback na raiz, a pasta `shared/` da raiz do módulo **não é copiada** (o backend copiado é apenas `app/modules/{module_name}`); verificar se o `copy_backend`/estrutura do zip já exclui `shared/` da raiz (o `export.py` da skill exclui). Ajustar o log/regra conforme necessário.
- `templates/shared/export.py` da skill já exclui `shared/` inteiro do zip — manter.
- `AGENTS.md` do monorepo (seção "Import para api-sqlserver": "`frontend/shared/` é ignorado durante a cópia") — atualizar a descrição para refletir que o fallback vive na raiz `shared/` do módulo e não é copiado.

---

## 6. Fora de escopo

- Refatoração do `ReusableModal.js` (abertura/foco/escape) — sem mudanças necessárias
- Mudança de visual dos modais além do layout flex/scroll (cores, larguras, bordas dos módulos são preservadas)
- Modais de módulos que não são padrão (ex.: módulos importados via zip) — herdam o padrão do `core.css` automaticamente quando usam `.modal-card`/`.modal`

---

## 7. Verificação

1. `make dev-frontend` (ou `scripts/dev-frontend.ps1`) e abrir cada modal em **desktop**:
   - Login (`forgotModal`), structure (`abaModal`, `moduloModal`, `pickerModal`), users (`permissoesModal`, `userModal`), admins (`userModal`), importer (`importModal`), profile (`passwordModal`, `preferencesModal`), admin-skins (`skinModal`, `templateModal`)
   - Header e footer sempre visíveis; scroll apenas no meio; largura/padding visual preservados
2. Repetir em **mobile** (`< 768px`, DevTools): bottom-sheet full-width, cantos superiores arredondados, header/footer fixos
3. Testar com conteúdo longo (userModal do users/admins, importModal com log grande) e conteúdo curto (forgotModal, passwordModal)
4. Gerar um módulo de exemplo com a skill `create-standalone-module` e rodar standalone (`make dev-backend` + `make dev-frontend`): confirmar `/shared/core.css` e `/shared/config.js` resolvem para a raiz `shared/` do módulo e que o modal usa o padrão
5. Conferir que o zip gerado pelo export não contém a pasta `shared/`
6. Sem regressão de temas (testar com pelo menos 2 skins)

---

## 8. Arquivos afetados (resumo)

**Frontend monorepo**
- `apps/frontend-webapp/shared/core.css` — padrão compartilhado + media query mobile
- `apps/frontend-webapp/style.css` — remover blocos duplicados de modal (`.modal-overlay`, `.modal-header`, `.modal-close`); manter overrides visuais de `.modal` (ver seção 4.1)
- `apps/frontend-webapp/index.html` — `forgotModal` (`.modal-content`)
- `apps/frontend-webapp/modules/{structure,users,admins,importer,profile,admin-skins}/index.html` — `.modal-content`
- `apps/frontend-webapp/modules/structure/script.js` — `pickerModal` (`.modal-content`)
- `apps/frontend-webapp/modules/{structure,users,profile,admin-skins}/style.css` — limpeza de overrides
- `apps/api-postgres/scripts/import_module.py` — ajuste da regra de ignore do `shared`
- `AGENTS.md` (monorepo) — nota do `frontend/shared/`

**Skill `create-standalone-module`**
- `.opencode/skills/create-standalone-module/templates/shared/frontend/index.html` — `.modal-content`
- `.opencode/skills/create-standalone-module/templates/shared/standalone/shared/{core.css,config.js,app.js}` — mover de `templates/shared/frontend/shared/`; `core.css` espelha padrão + bottom-sheet
- `.opencode/skills/create-standalone-module/templates/shared/support/Makefile` — `dev-frontend` serve raiz
- `.opencode/skills/create-standalone-module/SKILL.md` — estrutura do modal + estrutura `shared/` na raiz