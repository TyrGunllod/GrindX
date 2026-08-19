# Modais com header/footer fixos — Plano de Implementação

> **Para workers agenticos:** SUB-SKILL OBRIGATÓRIA: use `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para implementar este plano task por task. Passos usam checkbox (`- [ ]`).

**Goal:** Padronizar todos os modais dos módulos padrão do frontend e os gerados pela skill `create-standalone-module` para que header e footer fiquem fixos e apenas o conteúdo central role, com bottom-sheet no mobile.

**Architecture:** Padrão CSS compartilhado no `shared/core.css` — `.modal-card`/`.modal`/`.modal-dialog` viram flex column com `max-height`, `.modal-header`/`.modal-footer` com `flex-shrink:0`, e uma nova classe `.modal-content` é o container central scrollável (`flex:1; min-height:0; overflow-y:auto`). Media query `< 768px` transforma os modais em bottom-sheet. Cada módulo adiciona `.modal-content` ao elemento central e remove overrides duplicados; `max-width`/`border-radius` específicos migram para media query desktop. A skill espelha o padrão e move o fallback `shared/` para a raiz do módulo standalone.

**Tech Stack:** CSS puro (design system via `var(--...)`), HTML vanilla, JS vanilla. Sem frameworks.

**Spec:** `docs/superpowers/specs/2026-08-19-modais-header-footer-fixo-scroll.md`

---

## Visão geral dos arquivos

**Monorepo frontend**
- `apps/frontend-webapp/shared/core.css` — padrão compartilhado + bottom-sheet mobile + `.modal-overlay.hidden`
- `apps/frontend-webapp/style.css` — login: base `.modal` + overrides visuais em media query desktop
- `apps/frontend-webapp/index.html` — `forgotModal`: `<form>` vira `.modal-content`
- `apps/frontend-webapp/modules/users/index.html` + `style.css` — `permissoesModal` e `userModal`
- `apps/frontend-webapp/modules/admins/index.html` — `userModal` (reusa `users/style.css`)
- `apps/frontend-webapp/modules/structure/index.html` + `script.js` + `style.css` — `abaModal`, `moduloModal`, `pickerModal`
- `apps/frontend-webapp/modules/profile/index.html` + `style.css` — `passwordModal`, `preferencesModal`
- `apps/frontend-webapp/modules/admin-skins/index.html` + `style.css` — `skinModal`, `templateModal`
- `apps/frontend-webapp/modules/importer/index.html` + `style.css` — `importModal`

**Skill `create-standalone-module`**
- `templates/shared/standalone/shared/{core.css,config.js,app.js}` — movidos de `templates/shared/frontend/shared/`
- `templates/shared/frontend/index.html` — `form` vira `.modal-content`
- `templates/shared/support/Makefile` — `dev-frontend` serve a raiz
- `SKILL.md` — estrutura `shared/` na raiz + padrão de modal

**Cross-impact**
- `apps/api-postgres/scripts/import_module.py` — nota/regra do `shared`
- `AGENTS.md` (monorepo) — nota do `frontend/shared/`

> **Decisão de verificação:** não há testes automatizados para CSS/HTML neste repositório. Cada task usa **verificação manual** (`make dev-frontend`) + **grep de consistência** para garantir que não sobrou classe antiga.

---

## PARTE A — Frontend do monorepo

### Task 1: Padrão compartilhado no `shared/core.css`

**Files:**
- Modify: `apps/frontend-webapp/shared/core.css:300-407`

- [ ] **Step 1: Adicionar `.modal-overlay.hidden` após o bloco `.modal-overlay`**

No final do bloco `.modal-overlay` (linha ~314), adicione:

```css
.modal-overlay.hidden {
    display: none;
}
```

> Necessário porque `core.css` não tem utilitário `.hidden`; login (`forgotModal`) e importer (`importModal`) usam `class="modal-overlay hidden"`.

- [ ] **Step 2: Tornar os containers de modal flex column**

Após o bloco `.modal-card` (linha ~323), adicione:

```css
/* Layout de modal: header/footer fixos, conteúdo central scrollável */
.modal-card,
.modal,
.modal-dialog {
    display: flex;
    flex-direction: column;
    max-height: 90vh;
}
```

> `.modal` (login/importer) e `.modal-dialog` (profile) mantêm seus `max-width`/`border-radius`/`padding` atuais — só ganham o layout flex.

- [ ] **Step 3: Header/footer com `flex-shrink: 0` e nova classe `.modal-content`**

No bloco `.modal-header` (linhas 397-401) adicione `flex-shrink: 0;`. No bloco `.modal-footer` (linhas 403-407) adicione `flex-shrink: 0;`. Após o bloco `.modal-footer`, adicione:

```css
.modal-content {
    flex: 1;
    min-height: 0;                /* obrigatório para o flex scroll funcionar */
    overflow-y: auto;
    scrollbar-gutter: stable;     /* evita layout shift ao abrir a scrollbar */
}
```

- [ ] **Step 4: Media query bottom-sheet mobile**

Após o bloco `.modal-content`, adicione:

```css
/* Modal bottom-sheet (mobile) */
@media (max-width: 767px) {
    .modal-overlay {
        padding: 0;
        align-items: flex-end;
    }
    .modal-card,
    .modal,
    .modal-dialog {
        width: 100%;
        max-width: 100%;
        max-height: 92vh;
        border-radius: 1rem 1rem 0 0;   /* apenas cantos superiores */
    }
}
```

- [ ] **Step 5: Verificar que nada quebrou antes dos próximos tasks**

Run: `make dev-frontend` e abrir no browser o login e o importer. Expected: modais ainda centralizados e funcionando (os módulos ainda não têm `.modal-content`, mas os overrides atuais de `overflow-y:auto`/`max-height` continuam ativos). Verificar no DevTools que `.modal-card` agora exibe `flex-direction: column`.

- [ ] **Step 6: Commit**

```bash
git add apps/frontend-webapp/shared/core.css
git commit -m "fix: shared modal layout with fixed header/footer and mobile bottom-sheet"
```

---

### Task 2: Login — `index.html` + `style.css`

**Files:**
- Modify: `apps/frontend-webapp/index.html:76-99`
- Modify: `apps/frontend-webapp/style.css:82-132`

- [ ] **Step 1: Adicionar `.modal-content` ao formulário do `forgotModal`**

Em `apps/frontend-webapp/index.html:82`, altere:

```html
<form id="forgotForm" class="grid" novalidate>
```
para:
```html
<form id="forgotForm" class="modal-content grid" novalidate>
```

- [ ] **Step 2: Reestruturar o bloco Modal em `style.css`**

Substitua todo o bloco `/* Modal Styles */` (linhas 82-132: `.modal-overlay`, `.modal-overlay.hidden`, `.modal`, `.modal-header`, `.modal-header h2`, `.modal-close`, `.modal-close:hover`) por:

```css
/* Modal — base .modal (overlay, header, close e bottom-sheet vêm do core.css) */
.modal {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    padding: var(--space-4);
    width: 100%;
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2);
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.modal-header h2 {
    font-size: 1.25rem;
    font-weight: 600;
}

.modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: var(--text-muted);
    padding: 0.25rem;
    line-height: 1;
}

.modal-close:hover {
    color: var(--text-main);
}

/* Desktop: visual próprio do .modal (mobile é bottom-sheet full-width via core.css) */
@media (min-width: 768px) {
    .modal {
        max-width: 400px;
        border-radius: 1.5rem;
    }
}
```

> **Por que manter `.modal-header`/`.modal-close`:** o `core.css` do monorepo NÃO define `display:flex` no `.modal-header` (só margin/borda/padding). Removê-los quebraria o espaçamento título × botão fechar. Os blocos realmente removidos são `.modal-overlay` e `.modal-overlay.hidden` (agora no core.css). O `max-width:400px` e o `border-radius:1.5rem` migraram para media query desktop para o bottom-sheet do mobile valer.

- [ ] **Step 3: Verificar manualmente**

Run: `make dev-frontend`, abrir o login, clicar em "Esqueceu a senha?". Expected: modal centralizado no desktop (400px, cantos 1.5rem), header com título e botão fechar lado a lado. No DevTools em `400px` de largura: modal full-width na base, cantos superiores arredondados, form central com scroll próprio.

- [ ] **Step 4: Commit**

```bash
git add apps/frontend-webapp/index.html apps/frontend-webapp/style.css
git commit -m "fix: login forgot modal uses shared modal-content scroll pattern"
```

---

### Task 3: users + admins

**Files:**
- Modify: `apps/frontend-webapp/modules/users/index.html:49-62` e `:64-213`
- Modify: `apps/frontend-webapp/modules/users/style.css:121-138` e `:287-341`
- Modify: `apps/frontend-webapp/modules/admins/index.html:44-192`

> `admins` carrega `../users/style.css` — mudanças no CSS de `users` afetam os dois.

- [ ] **Step 1: `permissoesModal` — adicionar `.modal-content`**

Em `apps/frontend-webapp/modules/users/index.html:54`, altere:

```html
<div id="permissoesContent" class="py-4">
```
para:
```html
<div id="permissoesContent" class="modal-content py-4">
```

- [ ] **Step 2: `userModal` — converter `.modal-scroll` para `.modal-content`**

Em `apps/frontend-webapp/modules/users/index.html:70`:

```html
<div class="modal-scroll">
```
para:
```html
<div class="modal-content">
```

Em `apps/frontend-webapp/modules/admins/index.html:49`:

```html
<div class="modal-scroll">
```
para:
```html
<div class="modal-content">
```

- [ ] **Step 3: Limpar `users/style.css` — bloco `#permissoesModal`**

Remova o bloco (linhas 121-138):

```css
#permissoesModal .modal-card {
    max-height: 80vh;
    display: flex;
    flex-direction: column;
}

#permissoesModal #permissoesContent {
    overflow-y: auto;
    flex: 1;
    min-height: 0;
}

#permissoesModal .modal-footer {
    flex-shrink: 0;
}
```

> Comportamento agora vem do padrão compartilhado (`.modal-card` flex + `.modal-content` scroll). `#permissoesContent` mantém `py-4` (padding) do HTML.

- [ ] **Step 4: Limpar `users/style.css` — bloco `#userModal`**

Substitua o bloco (linhas 287-341):

```css
#userModal .modal-card-wide {
    max-width: 720px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
}

#userModal .modal-scroll {
    overflow-y: auto;
    flex: 1;
    min-height: 0;
    padding: 0;
}
```
por:
```css
#userModal .modal-card-wide {
    max-width: 720px;
}
```
E renomeie os seletores restantes de `.modal-scroll` para `.modal-content` neste mesmo bloco (linhas ~304, 313, 322, 327):

```css
#userModal .modal-content .profile-card { ... }
#userModal .modal-content .profile-card h2 { ... }
#userModal .modal-content .profile-card h2 i { ... }
#userModal .modal-content .field-divider { ... }
```

> No mobile o `max-width:720px` do `.modal-card-wide` seria maior que a viewport e venceria o `max-width:100%` do core (stylesheets de módulo carregam depois do core). Por isso o `max-width` precisa ser restrito a desktop. **Step 5 cobre isso.**

- [ ] **Step 5: Restringir `max-width:720px` a desktop**

No `users/style.css`, envolva o bloco `#userModal .modal-card-wide` em media query:

```css
@media (min-width: 768px) {
    #userModal .modal-card-wide {
        max-width: 720px;
    }
}
```

- [ ] **Step 6: Verificar manualmente**

Run: `make dev-frontend`, abrir `modules/users/` e `modules/admins/`. Expected: abrir o `userModal` (form longo) — header "Cadastrar Usuário" e footer (Cancelar/Salvar) fixos, scroll apenas no meio; `permissoesModal` idem. No DevTools `400px`: full-width bottom-sheet, header/footer fixos.

- [ ] **Step 7: Commit**

```bash
git add apps/frontend-webapp/modules/users/index.html apps/frontend-webapp/modules/users/style.css apps/frontend-webapp/modules/admins/index.html
git commit -m "fix: users and admins modals use shared modal-content scroll pattern"
```

---

### Task 4: structure

**Files:**
- Modify: `apps/frontend-webapp/modules/structure/index.html:39-64`
- Modify: `apps/frontend-webapp/modules/structure/script.js:516-526`
- Modify: `apps/frontend-webapp/modules/structure/style.css:114-118` e `:155-176`

- [ ] **Step 1: `abaModal` e `moduloModal` — adicionar `.modal-content` aos forms**

Em `apps/frontend-webapp/modules/structure/index.html:44`:

```html
<form id="abaForm" class="p-4"></form>
```
para:
```html
<form id="abaForm" class="modal-content p-4"></form>
```

Em `apps/frontend-webapp/modules/structure/index.html:58`:

```html
<form id="moduloForm" class="p-4"></form>
```
para:
```html
<form id="moduloForm" class="modal-content p-4"></form>
```

- [ ] **Step 2: `pickerModal` dinâmico — adicionar `.modal-content` ao `#pickerList`**

Em `apps/frontend-webapp/modules/structure/script.js:522`:

```js
<div id="pickerList" class="picker-list"></div>
```
para:
```js
<div id="pickerList" class="picker-list modal-content"></div>
```

- [ ] **Step 3: Limpar `structure/style.css` — `.structure-modal`**

Remova o bloco (linhas 114-118):

```css
.structure-modal {
    max-height: 90vh;
    overflow-y: auto;
    scrollbar-gutter: stable;
}
```

> Regra compartilhada do core.css cobre (`max-height` + scroll no `.modal-content`). A classe `.structure-modal` continua no HTML sem regra própria.

- [ ] **Step 4: Limpar `structure/style.css` — `.picker-modal` e `.picker-list`**

Remova o bloco (linhas 155-159):

```css
.picker-modal {
    max-height: 80vh;
    display: flex;
    flex-direction: column;
}
```

E no bloco `.picker-list` (linhas 168-176), remova `flex: 1; overflow-y: auto; max-height: 50vh;` — mantendo `display:flex; flex-direction:column; gap:0.375rem; padding:0.5rem 0;`:

```css
.picker-list {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
    padding: 0.5rem 0;
}
```

> `.picker-list` mantém `display:flex` para empilhar os itens; o scroll agora vem do `.modal-content`.

- [ ] **Step 5: Verificar manualmente**

Run: `make dev-frontend`, abrir `modules/structure/`. Expected: `abaModal`/`moduloModal` com header e footer fixos e form scrollando; `pickerModal` (botão de busca de módulo) com header (título + busca) fixo, lista com scroll, footer fixo.

- [ ] **Step 6: Commit**

```bash
git add apps/frontend-webapp/modules/structure/index.html apps/frontend-webapp/modules/structure/script.js apps/frontend-webapp/modules/structure/style.css
git commit -m "fix: structure modals use shared modal-content scroll pattern"
```

---

### Task 5: profile

**Files:**
- Modify: `apps/frontend-webapp/modules/profile/index.html:161-234`
- Modify: `apps/frontend-webapp/modules/profile/style.css:224-282`

- [ ] **Step 1: `passwordModal` e `preferencesModal` — converter `.modal-body` para `.modal-content`**

Em `apps/frontend-webapp/modules/profile/index.html:166` e `:193`, altere:

```html
<div class="modal-body">
```
para:
```html
<div class="modal-content">
```
(ambas as ocorrências — uma no `passwordModal`, outra no `preferencesModal`).

- [ ] **Step 2: Limpar `profile/style.css` — `.modal-dialog`**

Substitua o bloco `.modal-dialog` (linhas 234-242) por:

```css
.modal-dialog {
    background: var(--bg-card, #fff);
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

@media (min-width: 768px) {
    .modal-dialog {
        width: 90%;
        max-width: 440px;
        border-radius: var(--radius-lg, 0.75rem);
    }
}
```

> Removidos `max-height:90vh; overflow-y:auto` (agora compartilhados). `width`/`max-width`/`border-radius` foram para media query desktop para não conflitarem com o bottom-sheet do mobile (`width:100%`/`max-width:100%`/cantos superiores) — o stylesheet do módulo carrega depois do core.css.

- [ ] **Step 3: Renomear `.modal-body` para `.modal-content` no `profile/style.css`**

Em `apps/frontend-webapp/modules/profile/style.css:269`, altere:

```css
.modal-body {
    padding: 20px 24px;
}
```
para:
```css
.modal-content {
    padding: 20px 24px;
}
```

- [ ] **Step 4: Verificar manualmente**

Run: `make dev-frontend`, abrir `modules/profile/`. Expected: "Alterar Senha" e "Preferências" com header fixo, conteúdo central, footer fixo. No DevTools `400px`: bottom-sheet full-width.

- [ ] **Step 5: Commit**

```bash
git add apps/frontend-webapp/modules/profile/index.html apps/frontend-webapp/modules/profile/style.css
git commit -m "fix: profile modals use shared modal-content scroll pattern"
```

---

### Task 6: admin-skins

**Files:**
- Modify: `apps/frontend-webapp/modules/admin-skins/index.html:36-47` e `:432-452`
- Modify: `apps/frontend-webapp/modules/admin-skins/style.css:75-80` e `:395-398`

- [ ] **Step 1: `skinModal` — adicionar `.modal-content` ao form**

Em `apps/frontend-webapp/modules/admin-skins/index.html:49`:

```html
<form id="skinForm" class="skin-form">
```
para:
```html
<form id="skinForm" class="skin-form modal-content">
```

- [ ] **Step 2: `templateModal` — converter `.modal-body` para `.modal-content`**

Em `apps/frontend-webapp/modules/admin-skins/index.html:441`:

```html
<div class="modal-body">
```
para:
```html
<div class="modal-content">
```

- [ ] **Step 3: Limpar `admin-skins/style.css` — `.skin-modal`**

Substitua o bloco (linhas 75-80) por:

```css
@media (min-width: 768px) {
    .skin-modal {
        max-width: min(490px, calc(100vw - var(--space-4)));
    }
}
```

> No mobile o `max-width` seria menor que `100vw` e venceria o `max-width:100%` do core (stylesheet do módulo carrega depois); desktop-only resolve. Removidos `max-height:90vh; overflow-y:auto; scrollbar-gutter:stable` (compartilhados).

- [ ] **Step 4: Limpar `admin-skins/style.css` — `.template-modal`**

Substitua o bloco (linhas 396-398) por:

```css
@media (min-width: 768px) {
    .template-modal {
        max-width: 600px;
    }
}
```

> `max-width:600px` em mobile seria maior que a viewport e venceria o `max-width:100%` do core; desktop-only resolve.

- [ ] **Step 5: Verificar manualmente**

Run: `make dev-frontend`, abrir `modules/admin-skins/`. Expected: editar skin — header fixo (com toggle "Tokens Extras"), form com scroll central, footer fixo; template modal com grid de templates scrollando.

- [ ] **Step 6: Commit**

```bash
git add apps/frontend-webapp/modules/admin-skins/index.html apps/frontend-webapp/modules/admin-skins/style.css
git commit -m "fix: admin-skins modals use shared modal-content scroll pattern"
```

---

### Task 7: importer

**Files:**
- Modify: `apps/frontend-webapp/modules/importer/index.html:74-86`
- Modify: `apps/frontend-webapp/modules/importer/style.css:40-41`

- [ ] **Step 1: `importModal` — adicionar `.modal-content` ao `#modalBody`**

Em `apps/frontend-webapp/modules/importer/index.html:80`:

```html
<div class="modal-body" id="modalBody"></div>
```
para:
```html
<div class="modal-content" id="modalBody"></div>
```

- [ ] **Step 2: Renomear `.modal-body` para `.modal-content` no `importer/style.css`**

Em `apps/frontend-webapp/modules/importer/style.css:40`:

```css
.modal-body { padding: var(--space-4) 0; }
```
para:
```css
.modal-content { padding: var(--space-4) 0; }
```

> `.modal-footer` do importer (`style.css:41`) permanece — é override legítimo de padding/gap.

- [ ] **Step 3: Verificar manualmente**

Run: `make dev-frontend`, abrir `modules/importer/`, "Atualizar" e importar um módulo para gerar log. Expected: header (título + fechar) fixo, log de importação (`#importLog` com `max-height:300px` próprio) scrollando no meio, footer fixo. Verificar também que o modal NÃO estoura a tela quando o corpo cresce.

- [ ] **Step 4: Commit**

```bash
git add apps/frontend-webapp/modules/importer/index.html apps/frontend-webapp/modules/importer/style.css
git commit -m "fix: importer modal uses shared modal-content scroll pattern"
```

---

### Task 8: Verificação integrada da Parte A

- [ ] **Step 1: Checagem de consistência (grep)**

Run:

```powershell
rg -n "modal-scroll|modal-body" apps/frontend-webapp
```

Expected: NENHUM resultado. Se houver, ajustar as ocorrências restantes (exceto `#importLog` que usa `import-log`, não `modal-body`).

- [ ] **Step 2: Revisão visual completa**

Run: `make dev-frontend`. Abrir cada modal em desktop e em `400px` de largura (DevTools):
- Login `forgotModal`; structure `abaModal`/`moduloModal`/`pickerModal`; users `permissoesModal`/`userModal`; admins `userModal`; importer `importModal`; profile `passwordModal`/`preferencesModal`; admin-skins `skinModal`/`templateModal`.

Expected em todos: header e footer sempre visíveis; scroll apenas no `.modal-content`; desktop centralizado com larguras atuais preservadas; mobile bottom-sheet full-width com cantos superiores arredondados.

- [ ] **Step 3: Testar com 2 skins**

Trocar de tema (light/dark) no profile e repetir o passo 2 no `userModal` e `skinModal`. Expected: sem regressão visual.

- [ ] **Step 4: Commit (se houver ajustes)**

```bash
git add -A
git commit -m "fix: final visual review of modal scroll pattern"
```

---

## PARTE B — Skill `create-standalone-module`

### Task 9: Mover templates de fallback para `templates/shared/standalone/shared/`

**Files:**
- Move: `.opencode/skills/create-standalone-module/templates/shared/frontend/shared/core.css` → `.opencode/skills/create-standalone-module/templates/shared/standalone/shared/core.css`
- Move: `.opencode/skills/create-standalone-module/templates/shared/frontend/shared/config.js` → `.opencode/skills/create-standalone-module/templates/shared/standalone/shared/config.js`
- Move: `.opencode/skills/create-standalone-module/templates/shared/frontend/shared/app.js` → `.opencode/skills/create-standalone-module/templates/shared/standalone/shared/app.js`

- [ ] **Step 1: Criar o diretório de destino e mover os arquivos**

```powershell
New-Item -ItemType Directory -Force -Path ".opencode/skills/create-standalone-module/templates/shared/standalone/shared" | Out-Null
Move-Item ".opencode/skills/create-standalone-module/templates/shared/frontend/shared/core.css" ".opencode/skills/create-standalone-module/templates/shared/standalone/shared/core.css"
Move-Item ".opencode/skills/create-standalone-module/templates/shared/frontend/shared/config.js" ".opencode/skills/create-standalone-module/templates/shared/standalone/shared/config.js"
Move-Item ".opencode/skills/create-standalone-module/templates/shared/frontend/shared/app.js" ".opencode/skills/create-standalone-module/templates/shared/standalone/shared/app.js"
Remove-Item ".opencode/skills/create-standalone-module/templates/shared/frontend/shared" -Recurse -Force
```

> Estes arquivos são o fallback que agora vive na **pasta `shared/` da raiz do módulo standalone** (junto do pacote Python), não mais dentro de `frontend/{tab}/shared/`.

- [ ] **Step 2: Verificar**

Run: `Get-ChildItem -Recurse ".opencode/skills/create-standalone-module/templates/shared/standalone"`. Expected: a pasta `shared/` com os 3 arquivos existe e `templates/shared/frontend/shared/` não existe mais.

- [ ] **Step 3: Commit**

```bash
git add -A .opencode/skills/create-standalone-module/templates
git commit -m "refactor: move frontend fallback shared to module root in skill templates"
```

---

### Task 10: Espelhar o padrão de modal no fallback `core.css`

**Files:**
- Modify: `.opencode/skills/create-standalone-module/templates/shared/standalone/shared/core.css:181-205`

- [ ] **Step 1: Adicionar `.modal-overlay.hidden`**

Após o bloco `.modal-overlay` (linha ~188), adicione:

```css
.modal-overlay.hidden { display: none; }
```

- [ ] **Step 2: Tornar `.modal-card` flex column**

Em `.modal-card` (linhas 189-194), adicione `display: flex; flex-direction: column; max-height: 90vh;`:

```css
.modal-card {
    background: var(--bg-card);
    width: 100%; max-width: 600px;
    border-radius: var(--skin-radius-md);
    box-shadow: var(--skin-shadow-modal);
    display: flex; flex-direction: column; max-height: 90vh;
}
```

- [ ] **Step 3: Header/footer com `flex-shrink: 0` + nova `.modal-content`**

Em `.modal-header` (linhas 195-199) e `.modal-footer` (linhas 201-205), adicione `flex-shrink: 0;`. Após `.modal-footer`, adicione:

```css
.modal-content {
    flex: 1; min-height: 0; overflow-y: auto; scrollbar-gutter: stable;
}
```

- [ ] **Step 4: Media query bottom-sheet mobile**

Ao final da seção modal, adicione:

```css
@media (max-width: 767px) {
    .modal-overlay { padding: 0; align-items: flex-end; }
    .modal-card {
        width: 100%; max-width: 100%; max-height: 92vh;
        border-radius: 1rem 1rem 0 0;
    }
}
```

- [ ] **Step 5: Verificar**

Run: `Get-Content ".opencode/skills/create-standalone-module/templates/shared/standalone/shared/core.css" | Select-String -Pattern "modal-content","flex-shrink","92vh"`. Expected: todas presentes.

- [ ] **Step 6: Commit**

```bash
git add .opencode/skills/create-standalone-module/templates/shared/standalone/shared/core.css
git commit -m "fix: mirror shared modal scroll pattern in standalone fallback core.css"
```

---

### Task 11: Template `index.html` — `.modal-content`

**Files:**
- Modify: `.opencode/skills/create-standalone-module/templates/shared/frontend/index.html:52`

- [ ] **Step 1: Adicionar `.modal-content` ao form**

Em `templates/shared/frontend/index.html:52`:

```html
<form id="form-entity">
```
para:
```html
<form id="form-entity" class="modal-content grid grid-md-2">
```

> Módulos novos já nascem com o padrão: header fixo, form scrollável, footer fixo.

- [ ] **Step 2: Commit**

```bash
git add .opencode/skills/create-standalone-module/templates/shared/frontend/index.html
git commit -m "fix: skill template modal uses modal-content scroll pattern"
```

---

### Task 12: Template `Makefile` — `dev-frontend` serve a raiz

**Files:**
- Modify: `.opencode/skills/create-standalone-module/templates/shared/support/Makefile:32-35`

- [ ] **Step 1: Alterar `dev-frontend`**

Substitua (linhas 32-35):

```makefile
dev-frontend:
	@echo "Iniciando servidor frontend estatico..."
	@cd frontend/{frontend_prefix}_* && python -m http.server 7080
	@echo "Frontend em http://localhost:7080"
```
por:
```makefile
dev-frontend:
	@echo "Iniciando servidor frontend estatico (raiz do modulo)..."
	@python -m http.server 7080
	@echo "Frontend em http://localhost:7080"
```

> A raiz do módulo agora contém `shared/` (fallback) — servir a raiz faz `/shared/core.css`, `/shared/config.js` e `/shared/app.js` resolverem para `{module_root}/shared/`. O `version.js` de cada aba continua relativo (`frontend/{tab}/version.js`).

- [ ] **Step 2: Verificar**

Run: `Select-String -Path ".opencode/skills/create-standalone-module/templates/shared/support/Makefile" -Pattern "http.server"`. Expected: apenas `@python -m http.server 7080`.

- [ ] **Step 3: Commit**

```bash
git add .opencode/skills/create-standalone-module/templates/shared/support/Makefile
git commit -m "fix: standalone dev-frontend serves module root so /shared/ resolves"
```

---

### Task 13: Atualizar `SKILL.md`

**Files:**
- Modify: `.opencode/skills/create-standalone-module/SKILL.md`

- [ ] **Step 1: Atualizar a nota da linha 27**

Substitua:

> **Pasta `shared` do frontend**: o módulo referencia `/shared/core.css`, `/shared/config.js` e `/shared/app.js` (caminho absoluto a partir da raiz da webapp). No GrindX isso usa a **`shared` padrão**; a pasta `shared/` dentro do frontend é **apenas fallback standalone** (para `make dev-frontend`) e **não é copiada** no export/package. O `version.js` é específico do módulo e fica na **raiz** de cada frontend (carregado como `version.js`).

por:

> **Pasta `shared` na raiz do módulo**: o módulo referencia `/shared/core.css`, `/shared/config.js` e `/shared/app.js` (caminho absoluto a partir da raiz da webapp). No GrindX isso usa a **`shared` padrão** (`apps/frontend-webapp/shared/`); no **standalone**, o fallback (`core.css`, `config.js`, `app.js`) vive na pasta **`shared/` da raiz do módulo**, **coexistindo** com o pacote Python (`__init__.py`, `exceptions/`, `schemas/`). Toda a pasta `shared/` é **apenas fallback standalone** — o `export.py` a exclui do zip e o `make dev-frontend` serve a **raiz do módulo** (não a pasta de cada aba). O `version.js` é específico do módulo e fica na **raiz** de cada frontend (carregado como `version.js`).

- [ ] **Step 2: Atualizar a árvore (linhas 127-143)**

Substitua:

```
├── shared/
│   ├── __init__.py
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── base.py                             # Templates/shared/standalone/shared_exceptions.py
│   └── schemas/
│       ├── __init__.py
│       └── base.py                             # Templates/shared/standalone/shared_schemas.py
├── frontend/
│   ├── {frontend_prefix}_{tab1}/
│   │   ├── index.html, script.js, style.css    # Templates/shared/frontend/*
│   │   ├── version.js                           # Templates/shared/frontend/version.js (raiz do frontend)
│   │   ├── shared/                              # fallback APENAS standalone — NÃO copiado no export/package
│   │   │   ├── core.css                         # Templates/shared/frontend/shared/core.css
│   │   │   └── app.js                           # Templates/shared/frontend/shared/app.js
│   │   └── (style.css importa /shared/core.css)
│   └── ...
```

por:

```
├── shared/
│   ├── __init__.py
│   ├── core.css, config.js, app.js             # Fallback frontend (raiz) — Templates/shared/standalone/shared/*
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── base.py                             # Templates/shared/standalone/shared_exceptions.py
│   └── schemas/
│       ├── __init__.py
│       └── base.py                             # Templates/shared/standalone/shared_schemas.py
├── frontend/
│   ├── {frontend_prefix}_{tab1}/
│   │   ├── index.html, script.js, style.css    # Templates/shared/frontend/*
│   │   ├── version.js                           # Templates/shared/frontend/version.js (raiz do frontend)
│   │   └── (style.css importa /shared/core.css — shared na raiz do módulo)
│   └── ...
```

- [ ] **Step 3: Atualizar a seção "1.0 Standalone Prerequisites" (linhas 199-203)**

Substitua:

```
### `frontend/shared/core.css` → `templates/shared/frontend/shared/core.css`
Variáveis CSS (`--primary`, `--bg-card`, `--border-color`, etc.) para standalone sem o monorepo. **Apenas fallback standalone** — no GrindX o módulo usa a `shared` padrão em `/shared/core.css` e a `shared/` do módulo **não é copiada** no export.

### `frontend/shared/app.js` → `templates/shared/frontend/shared/app.js`
Stub vazio — no GrindX fornece `window.grindx.session`, no standalone é vazio. **Apenas fallback standalone**, não é copiada no export.
```

por:

```
### `shared/core.css` → `templates/shared/standalone/shared/core.css`
Variáveis CSS (`--primary`, `--bg-card`, `--border-color`, etc.) + padrão de modal (header/footer fixos, `.modal-content`, bottom-sheet mobile) para standalone sem o monorepo. **Apenas fallback standalone** — no GrindX o módulo usa a `shared` padrão em `/shared/core.css` e a `shared/` da raiz do módulo **não é copiada** no export.

### `shared/config.js` → `templates/shared/standalone/shared/config.js`
Define `window.GRINDX_CONFIG.API_BASE_URL` para standalone. **Apenas fallback standalone**, não é copiado no export.

### `shared/app.js` → `templates/shared/standalone/shared/app.js`
Stub vazio — no GrindX fornece `window.grindx.session`, no standalone é vazio. **Apenas fallback standalone**, não é copiado no export.

> **Atenção `make dev-frontend`:** serve a **raiz do módulo** (não a pasta de cada aba), pois `/shared/...` resolve para `{module_root}/shared/`. Isso expõe o código Python do backend via HTTP — aceitável em ambiente de desenvolvimento standalone.
```

- [ ] **Step 4: Atualizar a "Estrutura padrão do modal" (linhas 347-364)**

Substitua:

```html
<div class="modal-overlay" id="modal-id" role="dialog" aria-modal="true" aria-labelledby="modal-title" style="display: none;">
  <div class="modal-card">
    <header class="modal-header flex justify-between">
      <h3 id="modal-title">Título</h3>
      <button class="btn-icon" id="close-modal" aria-label="Fechar">&times;</button>
    </header>
    <form id="form-id" class="grid grid-md-2">
      <!-- campos do formulário -->
    </form>
    <footer class="modal-footer flex justify-end gap-2">
      <button type="button" class="btn" id="btn-cancel">Cancelar</button>
      <button type="button" class="btn btn-primary" id="btn-save">Salvar</button>
    </footer>
  </div>
</div>
```

por:

```html
<div class="modal-overlay" id="modal-id" role="dialog" aria-modal="true" aria-labelledby="modal-title" style="display: none;">
  <div class="modal-card">
    <header class="modal-header flex justify-between">
      <h3 id="modal-title">Título</h3>
      <button class="btn-icon" id="close-modal" aria-label="Fechar">&times;</button>
    </header>
    <form id="form-id" class="modal-content grid grid-md-2">
      <!-- campos do formulário — container central, scroll próprio -->
    </form>
    <footer class="modal-footer flex justify-end gap-2">
      <button type="button" class="btn" id="btn-cancel">Cancelar</button>
      <button type="button" class="btn btn-primary" id="btn-save">Salvar</button>
    </footer>
  </div>
</div>
```

E adicione logo abaixo do snippet a regra:

> **Padrão de modal (obrigatório):** o elemento central (form, lista, div) recebe a classe `modal-content`. O `core.css` cuida do layout — `.modal-card` flex column, header/footer com `flex-shrink:0` (nunca somem), `.modal-content` com scroll próprio (`overflow-y:auto`), e bottom-sheet full-width em `<768px`. **Não duplicar** `max-height`/`overflow` no `style.css` do módulo; apenas `max-width`/padding específicos, em media query `@media (min-width: 768px)`.

- [ ] **Step 5: Atualizar a regra "Modal" na seção 3.1 (linha 299)**

Substitua:

```
- Modal usa `modal-overlay` + `modal-card` (NÃO `<dialog>` nativo)
```
por:
```
- Modal usa `modal-overlay` + `modal-card` (NÃO `<dialog>` nativo); elemento central com `class="modal-content"` (header/footer fixos, scroll só no meio — layout vem do `core.css`)
```

- [ ] **Step 6: Verificar**

Run: `Select-String -Path ".opencode/skills/create-standalone-module/SKILL.md" -Pattern "frontend/shared/core.css"`. Expected: nenhum resultado (todas as referências agora apontam para `templates/shared/standalone/shared/` ou "raiz do módulo").

- [ ] **Step 7: Commit**

```bash
git add .opencode/skills/create-standalone-module/SKILL.md
git commit -m "docs: update skill for root shared fallback and modal-content pattern"
```

---

### Task 14: Cross-impact no monorepo

**Files:**
- Modify: `apps/api-postgres/scripts/import_module.py:200-202`
- Modify: `AGENTS.md` (raiz)

- [ ] **Step 1: Ajustar o log/regra de `shared` no `import_module.py`**

Substitua (linhas 199-202):

```python
    for item in src.iterdir():
        if item.name == "shared":
            logger.info("Ignorando diretório shared/ — já existe no monorepo")
            continue
```
por:

```python
    for item in src.iterdir():
        if item.name == "shared":
            # Módulos antigos ainda podem trazer frontend/shared/ (fallback).
            # Módulos novos movem o fallback para shared/ na raiz (excluído no zip
            # pelo export.py), então este caso só ocorre por compatibilidade.
            logger.info("Ignorando frontend/shared/ (compatibilidade) — já existe no monorepo")
            continue
```

- [ ] **Step 2: Atualizar a nota no `AGENTS.md` (monorepo)**

Na seção "Import para api-sqlserver", substitua:

```
- `frontend/shared/` é ignorado durante a cópia (já existe no monorepo)
```
por:

```
- O fallback `shared/` (frontend + Python) vive na raiz do módulo standalone e é **excluído no export** e **ignorado durante a cópia** (o monorepo tem os `shared` padrão)
```

- [ ] **Step 3: Verificar**

Run: `python -m py_compile apps/api-postgres/scripts/import_module.py`. Expected: sem erro.

- [ ] **Step 4: Commit**

```bash
git add apps/api-postgres/scripts/import_module.py AGENTS.md
git commit -m "docs: align import notes with root shared fallback location"
```

---

### Task 15: Verificação integrada da Parte B

- [ ] **Step 1: Gerar módulo de exemplo com a skill e testar standalone**

Criar um módulo de exemplo seguindo `SKILL.md` (fora do monorepo) e rodar:

```powershell
make dev-backend   # terminal 1
make dev-frontend  # terminal 2
```

Expected: `http://localhost:7080` serve o frontend; `/shared/core.css` e `/shared/config.js` resolvem para `{module_root}/shared/` (DevTools → Network, status 200); o modal do módulo tem header/footer fixos e scroll central; no mobile (`<768px`) vira bottom-sheet.

- [ ] **Step 2: Conferir exclusão do `shared/` no zip**

Run: `make package` e listar o conteúdo do zip. Expected: NENHUM caminho contendo `shared/`.

- [ ] **Step 3: Rodar a suite (regressão geral)**

Run: `make test-all` (se aplicável ao estado atual do repo). Expected: tudo passando (as mudanças são frontend/CSS/skill — não afetam backend).

---

## Self-review do plano (checklist)

- **Cobertura da spec:** §4.1→Task 1; §4.2→Tasks 2-7; §4.3→Tasks 2-7 (limpeza); §4.4→Tasks 10-11, 13; §4.5→Tasks 9, 12, 13; §5→Task 14; §7→Tasks 8, 15. Todos os modais listados na spec estão cobertos.
- **Refinamento vs spec:** a spec sugeria remover `.modal-header`/`.modal-close` do login como "duplicados"; o plano os mantém (o core.css do monorepo não tem `display:flex` no `.modal-header`). Documentado no Task 2 Step 2.
- **Placeholders:** nenhum "TBD"/"similar to Task N" — cada passo tem código completo e comando de verificação.
- **Consistência de nomes:** `.modal-content` é a única classe central; seletores antigos (`.modal-scroll`, `.modal-body`) são renomeados/removidos em todas as ocorrências.