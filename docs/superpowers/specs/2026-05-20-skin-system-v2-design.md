# Skin System v2 — Design Specification

> **Date:** 2026-05-20
> **Status:** Approved
> **Based on:** Skin System v1 (tasks 1-12 completed)

## Overview

Enhancements to the existing skin/theming system across 3 areas:
1. **Backend** — Theme history tracking, logo upload, skin templates
2. **Frontend Admin UI** — Advanced mode, color text input, auto dark mode, expanded preview
3. **Frontend UX** — Template picker, test button, localStorage cache

---

## Section 1: Backend

### 1.1 Theme History

**Table:** `theme_history`

| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK, autoincrement |
| theme_id | Integer | FK → company_themes.id (CASCADE) |
| action | String(20) | NOT NULL (create/update/delete/activate) |
| snapshot | JSONB | NULL (estado completo do tema antes da mudança) |
| changed_by | Integer | FK → usuarios.id (SET NULL) |
| changed_at | DateTime | server_default=now() |

**Endpoints:**
- `GET /v1/themes/{id}/history` — retorna histórico do tema (admin-only), ordenado por `changed_at DESC`
- Response: `[{ "id", "theme_id", "action", "snapshot", "changed_by", "changed_at" }]`

**Gatilhos (ThemeService):**
- `create_theme` → registra snapshot `{}` (estado vazio antes de existir)
- `update_theme` → registra snapshot com estado ANTES da atualização
- `activate_theme` → registra snapshot com estado antes (is_active=False)
- `delete_theme` → registra snapshot com estado completo antes de deletar

### 1.2 Logo Upload

**Endpoint:** `POST /v1/themes/{theme_id}/upload-logo`

- Content-Type: `multipart/form-data`
- Campo: `file` (imagem)
- Validação: max 2MB, tipos `png`, `jpg`, `jpeg`, `svg`, `webp`
- Salva em: `packages/api-postgres/static/uploads/logos/{theme_id}_{timestamp}_{filename}`
- Retorna: `{ "url": "/static/uploads/logos/..." }`
- Atualiza `logo_url` do tema automaticamente
- Role: admin-only
- Verifica que `theme_id` pertence à empresa do usuário

**Static serving:** FastAPI já serve `/static/` — confirmar mount em `main.py`.

### 1.3 Skin Templates

**Arquivos:** `packages/api-postgres/app/data/skin-templates/*.json`

Templates iniciais:
- `corporate-blue.json` — azul profissional
- `dark-minimal.json` — dark mode limpo
- `warm-earth.json` — tons terrosos
- `forest-green.json` — verdes naturais
- `sunset-orange.json` — laranjas vibrantes

**Formato do JSON:** Mesmo schema do `grindx-default.json` (colors, fonts, icon_library, tokens, company_name, copyright_text).

**Endpoints:**
- `GET /v1/themes/templates` — lista templates disponíveis (qualquer logado)
  - Response: `[{ "slug": "corporate-blue", "name": "Corporate Blue", "preview": { "primary": "#...", "bg": "#..." } }]`
- `POST /v1/themes/from-template` — cria tema a partir de template (admin-only)
  - Body: `{ "template_slug": "corporate-blue", "name": "Minha Skin" }`
  - Usa `current_user.company_id` como company_id
  - Retorna ThemeResponse

---

## Section 2: Frontend Admin UI

### 2.1 Modo Avançado (Toggle)

Checkbox "Modo Avançado" no topo do modal, abaixo do título.

**Quando ativo, expande:**

**Cores adicionais:**
- `--skin-primary-hover`
- `--skin-text-main`
- `--skin-text-muted`
- `--skin-border-color`
- `--skin-focus-ring`

**Dark mode tokens:**
- `--skin-bg-main-dark`
- `--skin-bg-card-dark`
- `--skin-text-main-dark`
- `--skin-text-muted-dark`
- `--skin-border-color-dark`

**Tokens extras:**
- `--skin-shadow-card`
- `--skin-shadow-modal`

### 2.2 Color Picker + Input de Texto

Cada cor tem layout horizontal:
```
[Label]  [color picker #00c2e0] [text input #00c2e0]
```

**Comportamento:**
- Color picker muda → atualiza text input
- Text input muda:
  - Se valor é hex válido → atualiza color picker
  - Se valor não é hex (ex: `oklch(...)`, `color-mix(...)`) → color picker desabilitado, text funciona normalmente
- Placeholder no text input: `#hex, rgb(), oklch(), color-mix()...`

### 2.3 Dark Mode Automático

Botão "Gerar Dark Mode" — aparece só com modo avançado ativo.

**Algoritmo:**
1. Para cada cor light (`--skin-bg-main`, `--skin-bg-card`, `--skin-text-main`, etc.):
   - Se a cor é clara (luminosidade > 0.5) → escurecer (inverter para ~0.1-0.2)
   - Se a cor é escura (luminosidade < 0.5) → clarear (inverter para ~0.8-0.9)
   - Ajustar saturação: reduzir 10-20% para dark
2. Preenche os campos `*-dark` no formulário
3. Aplica preview imediatamente

**Implementação:** Usar `color-mix()` ou conversão HSL via JS para cálculo de luminosidade.

### 2.4 Preview Expandido

Substituir o card simples por mini-dashboard:

```
┌─────────────────────────────────────────┐
│ ☰  Mini Dashboard              🌙      │  ← top-bar simulada
├──────┬──────────────────────────────────┤
│      │  ┌──────────┐  ┌──────────┐     │
│  📋  │  │  1,234   │  │  567     │     │  ← stat cards
│  Menu│  │  Vendas  │  │  Estoque │     │
│      │  └──────────┘  └──────────┘     │
│  Dash│                                  │
│  Users│ ┌──────────────────────────┐    │
│  Skins│ │ Nome    │ Status │ Valor │    │  ← mini tabela
│      │ ├─────────┼────────┼───────┤    │
│  ────│ │ Item A  │ Ativo  │ R$100 │    │
│  User│ │ Item B  │ Pend.  │ R$200 │    │
│  Pill│ └──────────────────────────┘    │
│      │  [Botão Primary] [Botão Danger] │  ← botões
│      │  [Input de texto...]            │  ← input
└──────┴──────────────────────────────────┘
```

Todos os elementos usam as CSS variables da skin — mudam em tempo real conforme o usuário edita.

---

## Section 3: Frontend UX

### 3.1 Template Picker

**Local:** Botão "Usar Template" no modal de criação (ao lado de "Nova Skin").

**Comportamento:**
1. Abre sub-modal com grid de cards (um por template)
2. Cada card: nome do template + preview de 4 faixas de cor
3. Clique → preenche formulário com valores do template → fecha sub-modal
4. Usuário pode editar antes de salvar

### 3.2 Botão "Testar"

**Local:** Card de cada skin no grid principal.

**Comportamento:**
1. Abre `dashboard.html?skin_preview={theme_id}` em nova aba
2. `dashboard.js` detecta `skin_preview` query param
3. Busca tema via `GET /v1/themes/{theme_id}` (não usa `/active`)
4. Aplica cores via `skinLoader.applyPreviewColors()` — sem salvar no cache
5. Banner no topo do dashboard:
   ```
   ┌────────────────────────────────────────────────────────┐
   │ 🔍 Preview da skin 'Corporate Blue'                    │
   │    [Aplicar Permanentemente]  [Fechar Preview]         │
   └────────────────────────────────────────────────────────┘
   ```
   - "Aplicar Permanentemente" → `POST /v1/themes/{id}/activate` → recarrega
   - "Fechar Preview" → fecha a aba (ou volta para skin original via `window.close()`)

### 3.3 Cache localStorage

**Fluxo do `skinLoader.load(companyId)`:**

```
1. Ler localStorage['skin_cache_{companyId}']
   → Se existe e timestamp < 5 min atrás:
     → Aplicar cache IMEDIATAMENTE (zero flash)

2. Fetch API /v1/themes/active (background)
   → Se sucesso e dados diferentes do cache:
     → Re-aplicar novas cores
     → Atualizar cache com novo timestamp

3. Se API falhar:
   → Manter cores do cache (mesmo antigo)
   → Se não houver cache → fallback skins/grindx-default.json
```

**Formato do cache:**
```json
{
  "timestamp": 1716249286000,
  "data": { "name": "...", "colors": {...}, "fonts": {...}, "tokens": {...}, ... }
}
```

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `packages/api-postgres/app/models/theme_history.py` | Create |
| `packages/api-postgres/app/models/__init__.py` | Modify |
| `packages/api-postgres/app/services/theme_service.py` | Modify (add history logging) |
| `packages/api-postgres/app/routers/theme_router.py` | Modify (add history, upload, template endpoints) |
| `packages/api-postgres/app/data/skin-templates/*.json` | Create (5 templates) |
| `packages/api-postgres/alembic/versions/004_add_theme_history.py` | Create |
| `packages/api-postgres/static/uploads/logos/.gitkeep` | Create |
| `packages/frontend-webapp/modules/admin-skins/index.html` | Modify (advanced mode, expanded preview, template button) |
| `packages/frontend-webapp/modules/admin-skins/style.css` | Modify (advanced mode styles, expanded preview) |
| `packages/frontend-webapp/modules/admin-skins/script.js` | Modify (all new logic) |
| `packages/frontend-webapp/shared/skinLoader.js` | Modify (cache logic, preview mode) |
| `packages/frontend-webapp/dashboard.js` | Modify (skin_preview query param handling) |
| `packages/frontend-webapp/dashboard.html` | Modify (preview banner container) |
