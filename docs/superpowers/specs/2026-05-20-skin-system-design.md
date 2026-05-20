# Skin System — Design Spec

**Date:** 2026-05-20
**Status:** Draft
**Author:** opencode

---

## 1. Overview

Sistema de skins/theming para o GrindX que permite personalizar cores, fontes, ícones, logos, nome da empresa e tokens visuais extras. Cada empresa pode ter sua skin própria, gerenciada via módulo admin e persistida no banco de dados. JSON files servem como fallback/default.

### Pré-requisitos

- O JWT payload deve incluir `company_id` (string UUID). Se o backend atual não inclui este campo, é necessário adicionar na geração do token.
- Este spec cobre apenas `api-postgres`. `api-sqlserver` pode receber o mesmo modelo e endpoints em implementação futura.

### Decisões de Design

- **Abordagem:** CSS Custom Properties + Skin Loader (runtime)
- **Escopo:** Skin parcial com overrides — a skin padrão do GrindX é a base, skins de empresa sobrescrevem variáveis específicas
- **Persistência:** Ambos — JSON como fallback, DB para overrides por empresa
- **Skin por:** Empresa (todos os usuários da empresa veem o mesmo tema)
- **Ativação:** Módulo admin em "Gestão" com seleção manual, persistida no database

---

## 2. Architecture

### Estrutura de Arquivos

```
packages/frontend-webapp/
├── shared/
│   ├── core.css              # modificado: skin tokens + semantic aliases
│   └── skinLoader.js         # novo: runtime do skin system
├── skins/                    # novo: JSON files
│   ├── grindx-default.json   # skin padrão (valores atuais)
│   └── _template.json        # template para novas skins
└── modules/
    └── admin-skins/          # novo: módulo de gestão de skins
        ├── index.html
        ├── style.css
        └── script.js

packages/api-postgres/app/models/
└── theme.py                  # novo: modelo SQLAlchemy CompanyTheme

packages/api-postgres/app/routers/
└── themes.py                 # novo: endpoints REST para skins
```

### Fluxo de Resolução de Skin

```
1. Usuário loga → API retorna company_id no JWT payload
2. Dashboard boot → skinLoader.js extrai company_id do token
3. skinLoader chama GET /v1/themes/active
4. API busca company_themes WHERE company_id = X AND is_active = true
5. Se encontrou → retorna JSON com colors/fonts/tokens/icons/branding
6. Se não encontrou (404) → skinLoader carrega skins/grindx-default.json
7. skinLoader aplica todas as variáveis via setProperty() no :root
8. Carrega ícones e fontes dinamicamente
9. Atualiza logos e textos de branding no DOM
```

---

## 3. Data Model

### Tabela: `company_themes`

| Coluna | Tipo | Nullable | Descrição |
|--------|------|----------|-----------|
| `id` | UUID PK | NO | Identificador único |
| `company_id` | UUID FK → companies | NO | Empresa dona do tema |
| `name` | VARCHAR(100) | NO | Nome da skin (ex: "Acme Corp Blue") |
| `is_active` | BOOLEAN | NO | Skin ativa para esta empresa (default: false) |
| `colors` | JSONB | YES | Overrides de cores: `{"--skin-primary": "#ff0000", ...}` |
| `fonts` | JSONB | YES | Overrides de fontes: `{"heading": "Inter", "body": "Roboto"}` |
| `icon_library` | VARCHAR(50) | NO | Biblioteca: `"fontawesome"`, `"lucide"`, `"material"` (default: `"fontawesome"`) |
| `tokens` | JSONB | YES | Tokens extras: `{"--radius-md": "8px", "--shadow-sm": "..."}` |
| `logo_url` | VARCHAR(500) | YES | URL do logo (SVG/PNG) |
| `logo_short_url` | VARCHAR(500) | YES | URL do logo curto (favicon/sidebar collapsed) |
| `company_name` | VARCHAR(100) | YES | Nome exibido no sistema (substitui "GrindX") |
| `copyright_text` | VARCHAR(200) | YES | Texto do rodapé |
| `created_at` | TIMESTAMP | NO | Criação (auto) |
| `updated_at` | TIMESTAMP | NO | Última alteração (auto) |

### Constraints

- Apenas UMA skin ativa por empresa: `UNIQUE(company_id) WHERE is_active = true`
- FK `company_id` referencia tabela `companies` com `ON DELETE CASCADE`

---

## 4. CSS Architecture

### Reorganização do `core.css`

Duas camadas de variáveis:

**Camada 1 — SKIN TOKENS (overrideáveis pelo skinLoader):**

```css
:root {
  /* Colors */
  --skin-primary: #00c2e0;
  --skin-primary-hover: #00a8c4;
  --skin-danger: #ef4444;
  --skin-success: #10b981;
  --skin-warning: #f59e0b;
  --skin-bg-main: #f8fafc;
  --skin-bg-card: #ffffff;
  --skin-text-main: #1e293b;
  --skin-text-muted: #64748b;
  --skin-border-color: #e2e8f0;
  --skin-focus-ring: rgba(0, 194, 224, 0.35);

  /* Fonts */
  --skin-font-heading: 'Barlow Condensed', 'Arial Narrow', sans-serif;
  --skin-font-body: 'DM Sans', system-ui, -apple-system, sans-serif;

  /* Tokens */
  --skin-radius-sm: 0.25rem;
  --skin-radius-md: 0.5rem;
  --skin-radius-lg: 0.75rem;
  --skin-radius-xl: 1.5rem;
  --skin-shadow-card: 0 10px 25px rgba(0,0,0,0.1);
  --skin-shadow-modal: 0 20px 25px -5px rgba(0,0,0,0.2);
}
```

**Camada 2 — SEMANTIC ALIASES (usados pelo resto do CSS, não sobrescrever diretamente):**

```css
:root {
  --primary: var(--skin-primary);
  --primary-hover: var(--skin-primary-hover);
  --danger: var(--skin-danger);
  --success: var(--skin-success);
  --warning: var(--skin-warning);
  --bg-main: var(--skin-bg-main);
  --bg-card: var(--skin-bg-card);
  --text-main: var(--skin-text-main);
  --text-muted: var(--skin-text-muted);
  --border-color: var(--skin-border-color);
  --focus-ring: var(--skin-focus-ring);
}
```

Dark mode continua funcionando via `@media (prefers-color-scheme: dark)` e `.dark-theme`, sobrescrevendo as semantic aliases (não os skin tokens).

### Dark Mode Compatibility

```css
@media (prefers-color-scheme: dark) {
  :root:not(.light-theme) {
    --bg-main: var(--skin-bg-main-dark, #0f172a);
    --bg-card: var(--skin-bg-card-dark, #1e293b);
    --text-main: var(--skin-text-main-dark, #f8fafc);
    --text-muted: var(--skin-text-muted-dark, #94a3b8);
    --border-color: var(--skin-border-color-dark, rgba(255, 255, 255, 0.05));
  }
}
```

Skin tokens podem incluir variantes dark (`--skin-bg-main-dark`), se não existirem usa o fallback hardcoded.

---

## 5. skinLoader.js — Runtime

### Classe Principal

```javascript
class SkinLoader {
  constructor() {
    this.defaults = {
      colors: { /* todos os --skin-* tokens de core.css */ },
      fonts: { heading: 'Barlow Condensed', body: 'DM Sans' },
      icon_library: 'fontawesome',
      tokens: { /* radius, shadows */ },
      company_name: 'GrindX',
      copyright_text: '© 2026 GrindX. Desenvolvido por Alex Grellet.',
      logo_url: null,
      logo_short_url: null
    };
  }

  async load(companyId) { /* ... */ }
  async fetchFromAPI(companyId) { /* ... */ }
  async fetchFromJSON(skinName) { /* ... */ }
  merge(defaults, overrides) { /* deep merge */ }
  applyColors(colors) { /* setProperty para cada --skin-* */ }
  applyTokens(tokens) { /* setProperty para cada --skin-* token */ }
  applyFonts(fonts) { /* injeta @font-face ou Google Fonts link */ }
  loadIconLibrary(library) { /* injeta <link> CDN dinâmico */ }
  updateBranding(companyName, copyrightText) { /* atualiza DOM */ }
  updateLogos(logoUrl, logoShortUrl) { /* atualiza <img> e <link rel="icon"> */ }
  async reload(companyId) { /* re-aplica sem refresh */ }
}
```

### Execução

- `index.html`: `<script src="shared/skinLoader.js"></script>` antes do `</body>`. No boot do login:
  1. Lê `localStorage.getItem('last_skin_company_id')`
  2. Se existir → busca skin do DB (ou JSON fallback) e aplica
  3. Se não existir → usa skin default (GrindX)
  4. Após login bem-sucedido → salva `localStorage.setItem('last_skin_company_id', companyId)`
- `dashboard.html`: `<script src="shared/skinLoader.js"></script>` no `<head>`, chama `load(companyId)` extraído do JWT no boot (antes do DOM paint para evitar flash)
- Se o JWT não tiver `company_id`, usa skin default
- A skin do login só atualiza no próximo acesso (persistida no localStorage)

### Live Preview (Admin Module)

O admin module importa `skinLoader` e chama `loader.applyColors(previewColors)` em tempo real enquanto o usuário edita os color pickers, sem salvar no DB.

---

## 6. Skin JSON Format

### `skins/grindx-default.json`

```json
{
  "name": "GrindX Default",
  "colors": {
    "--skin-primary": "#00c2e0",
    "--skin-primary-hover": "#00a8c4",
    "--skin-danger": "#ef4444",
    "--skin-success": "#10b981",
    "--skin-warning": "#f59e0b",
    "--skin-bg-main": "#f8fafc",
    "--skin-bg-card": "#ffffff",
    "--skin-text-main": "#1e293b",
    "--skin-text-muted": "#64748b",
    "--skin-border-color": "#e2e8f0",
    "--skin-focus-ring": "rgba(0, 194, 224, 0.35)"
  },
  "fonts": {
    "heading": "Barlow Condensed",
    "body": "DM Sans"
  },
  "icon_library": "fontawesome",
  "tokens": {
    "--skin-radius-sm": "0.25rem",
    "--skin-radius-md": "0.5rem",
    "--skin-radius-lg": "0.75rem",
    "--skin-radius-xl": "1.5rem",
    "--skin-shadow-card": "0 10px 25px rgba(0,0,0,0.1)",
    "--skin-shadow-modal": "0 20px 25px -5px rgba(0,0,0,0.2)"
  },
  "company_name": "GrindX",
  "copyright_text": "© 2026 GrindX. Desenvolvido por Alex Grellet.",
  "logo_url": null,
  "logo_short_url": null
}
```

### `skins/_template.json`

Mesma estrutura, com valores placeholder e comentários explicando cada campo.

---

## 7. Admin Module — `admin-skins/`

### UI Layout

```
┌──────────────────────────────────────────────────┐
│  Gestão de Skins                                 │
│  [+ Nova Skin]                                   │
├──────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ GrindX Def. │  │ Acme Blue   │  │ + Criar  │ │
│  │ [Ativa]     │  │ [Preview]   │  │          │ │
│  │ [Editar]    │  │ [Ativar]    │  │          │ │
│  │ [Excluir]   │  │ [Editar]    │  │          │ │
│  └─────────────┘  └─────────────┘  └──────────┘ │
└──────────────────────────────────────────────────┘
```

### Modal de Edição — Seções

1. **Identidade**
   - Nome da skin (input text)
   - Nome da empresa no sistema (input text)
   - Copyright (input text)
   - Logo URL (input file com upload para `/v1/themes/:id/logo`)
   - Logo Short URL (input file)

2. **Cores**
   - Color pickers para cada token: primary, primary-hover, danger, success, warning, bg-main, bg-card, text-main, text-muted, border-color, focus-ring
   - Preview ao vivo: mini card com as cores aplicadas

3. **Fontes**
   - Dropdown Heading: lista de fontes disponíveis (Barlow Condensed, Inter, Roboto, etc.)
   - Dropdown Body: mesma lista
   - Preview ao vivo: texto de exemplo com a fonte selecionada

4. **Ícones**
   - Radio buttons: Font Awesome / Lucide / Material Icons
   - Preview: grid de ícones de exemplo

5. **Tokens Extras**
   - Inputs para radius (sm, md, lg, xl)
   - Inputs para shadows (card, modal)

### Ações

- **Preview:** aplica skin no sidebar em tempo real (sem salvar) via `skinLoader.apply*()`
- **Salvar:** POST/PUT para API
- **Ativar:** POST `/v1/themes/:id/activate` — desativa outras skins da mesma empresa
- **Excluir:** DELETE (não pode excluir skin ativa)

---

## 8. API Endpoints

| Method | Path | Auth | Body | Descrição |
|--------|------|------|------|-----------|
| `GET` | `/v1/themes` | JWT Admin | — | Lista todas as skins da empresa |
| `GET` | `/v1/themes/active` | JWT | — | Skin ativa da empresa logada |
| `GET` | `/v1/themes/:id` | JWT Admin | — | Detalhes de uma skin |
| `POST` | `/v1/themes` | JWT Admin | ThemeCreate | Cria nova skin |
| `PUT` | `/v1/themes/:id` | JWT Admin | ThemeUpdate | Atualiza skin |
| `POST` | `/v1/themes/:id/activate` | JWT Admin | — | Ativa skin (desativa outras da mesma empresa) |
| `DELETE` | `/v1/themes/:id` | JWT Admin | — | Remove skin (erro se ativa) |
| `POST` | `/v1/themes/:id/logo` | JWT Admin | multipart/form-data | Upload de logo |

### Request/Response Schemas

**ThemeCreate:**
```json
{
  "name": "string (required)",
  "colors": { "--skin-primary": "string", ... },
  "fonts": { "heading": "string", "body": "string" },
  "icon_library": "fontawesome | lucide | material",
  "tokens": { "--skin-radius-md": "string", ... },
  "logo_url": "string | null",
  "logo_short_url": "string | null",
  "company_name": "string | null",
  "copyright_text": "string | null"
}
```

**ThemeUpdate:** mesmo schema, todos os campos opcionais.

**ThemeResponse:**
```json
{
  "id": "uuid",
  "company_id": "uuid",
  "name": "string",
  "is_active": true,
  "colors": { ... },
  "fonts": { ... },
  "icon_library": "fontawesome",
  "tokens": { ... },
  "logo_url": "string | null",
  "logo_short_url": "string | null",
  "company_name": "string | null",
  "copyright_text": "string | null",
  "created_at": "2026-05-20T00:00:00",
  "updated_at": "2026-05-20T00:00:00"
}
```

---

## 9. Icon Library Switching

### Mecanismo

O `skinLoader.loadIconLibrary(library)` injeta dinamicamente:

- **Font Awesome:** `<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">` (já usado)
- **Lucide:** `<script src="https://unpkg.com/lucide@latest"></script>` + `lucide.createIcons()` após DOM ready
- **Material Icons:** `<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">`

### Compatibilidade

Os ícones no HTML existente usam classes Font Awesome hardcoded (`fas fa-home`, etc.). A troca de biblioteca funciona assim:

- **Fase 1 (esta implementação):** Font Awesome continua sendo o padrão. Trocar para Lucide/Material aplica-se apenas a ícones registrados no `iconMap`. Ícones não mapeados mantêm Font Awesome.
- **Fase 2 (futuro):** Novos módulos devem usar `data-icon="home"` em vez de classes hardcoded. O skinLoader varre `[data-icon]` e aplica a classe correta da biblioteca ativa.
- O `iconMap` cobre apenas ícones do sidebar e módulos existentes (`home`, `users`, `box`, `cog`, `th-large`, `power-off`, `bars`, `moon`, `sun`, `chevron-left`, `chevron-down`, `times`).

---

## 10. Font Loading

### Self-Hosted vs CDN

- Fontes padrão (Barlow Condensed, DM Sans) já são self-hosted em `shared/fonts/`
- Novas fontes podem ser:
  - **Self-hosted:** adicionar arquivos `.woff2` em `shared/fonts/` + `@font-face` em `core.css`
  - **CDN (Google Fonts):** injetar `<link>` dinamicamente via `skinLoader.applyFonts()`

### Registry de Fontes Disponíveis

```javascript
const availableFonts = {
  'Barlow Condensed': { source: 'local', weights: [400, 700] },
  'DM Sans': { source: 'local', weights: [400, 500, 700] },
  'Inter': { source: 'google', weights: [400, 500, 600, 700] },
  'Roboto': { source: 'google', weights: [400, 500, 700] },
  'Open Sans': { source: 'google', weights: [400, 600, 700] },
};
```

---

## 11. Error Handling

| Cenário | Comportamento |
|---------|---------------|
| API indisponível no boot | Fallback para `grindx-default.json` |
| JSON default não encontrado | Usa valores hardcoded no `skinLoader.defaults` |
| Skin ativa deletada do DB | Nenhuma skin aplicada (usa defaults do CSS) |
| Upload de logo falha | Mostra erro no UI, não salva skin |
| Fonte CDN indisponível | Fallback para system fonts (font-family já tem fallback) |
| Biblioteca de ícones falha | Ícones não renderizam, mas layout não quebra |

---

## 12. Migration

### Alembic Migration

```python
def upgrade():
    op.create_table(
        'company_themes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('colors', postgresql.JSONB, nullable=True),
        sa.Column('fonts', postgresql.JSONB, nullable=True),
        sa.Column('icon_library', sa.String(50), nullable=False, server_default='fontawesome'),
        sa.Column('tokens', postgresql.JSONB, nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('logo_short_url', sa.String(500), nullable=True),
        sa.Column('company_name', sa.String(100), nullable=True),
        sa.Column('copyright_text', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_company_themes_company_id', 'company_themes', ['company_id'])
    op.create_index('ix_company_themes_active', 'company_themes', ['company_id'], unique=True,
                    postgresql_where=sa.text('is_active = true'))
```

---

## 13. Testing

### Frontend

- `skinLoader.load()` com companyId válido → aplica skin do DB
- `skinLoader.load()` com companyId sem skin → fallback JSON
- `skinLoader.load()` sem API → fallback JSON
- `skinLoader.reload()` → re-aplica sem refresh
- Color pickers → preview ao vivo funciona
- Icon library switch → ícones trocam corretamente
- Font switch → fontes carregam e aplicam

### Backend

- GET `/v1/themes/active` → retorna skin ativa ou 404
- POST `/v1/themes` → cria skin, valida JSONB
- POST `/v1/themes/:id/activate` → ativa skin, desativa outras da mesma empresa
- DELETE `/v1/themes/:id` → erro 409 se skin ativa
- Upload logo → salva arquivo, retorna URL
- RBAC → apenas admin pode CRUD skins

---

## 14. Security

- Upload de logos: validar MIME type (image/png, image/svg+xml, image/jpeg), max 2MB
- Logo URLs: sanitizar antes de injetar no DOM (prevenir XSS)
- Endpoints de skin: protegidos por JWT, CRUD requer role admin
- JSON files: read-only, sem execução de código

---
