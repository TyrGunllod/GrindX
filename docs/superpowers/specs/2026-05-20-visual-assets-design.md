# Visual Assets Design — Favicon & Fontes

**Data:** 2026-05-20
**Status:** Aprovado pelo usuário
**Projeto:** GrindX — Sistema de Gestão Integrado

---

## Contexto

O GrindX está 97% completo. O único item pendente são assets visuais: favicon e fontes. Atualmente as fontes são carregadas via CDN (jsdelivr) e não há favicon definido.

## Decisões de Design

### Favicon

| Propriedade | Valor |
|-------------|-------|
| **Estilo** | Diamante geométrico com "GX" no centro |
| **Cor primária** | `#00c2e0` (brand-is) |
| **Cor de fundo** | `#0f172a` (brand-natt / dark bg) |
| **Formatos** | `.ico` (16×16, 32×32), `.png` (32×32, 180×180), `site.webmanifest`, `mask-icon.svg` (Safari pinned tab) |
| **Localização** | `packages/frontend-webapp/assets/` |

### Fontes

| Fonte | Pesos | Formato | Origem | Licença |
|-------|-------|---------|--------|---------|
| Barlow Condensed | 400, 700 | .woff2 | Self-hosted | SIL OFL 1.1 (Jeremy Tribby) |
| DM Sans | 400, 500, 700 | .woff2 | Self-hosted | SIL OFL 1.1 (Google) |
| **Localização** | | `packages/frontend-webapp/shared/fonts/` | | |

**Nota de Licença:** Ambas as fontes usam SIL Open Font License 1.1 — uso comercial, modificação, distribuição e self-hosting são permitidos sem restrições. A única limitação é não vender a fonte isoladamente, o que não se aplica a este projeto.

---

## Arquitetura

### Estrutura de Arquivos

```
packages/frontend-webapp/
├── assets/
│   ├── favicon.ico              # 16×16 + 32×32 multi-icon
│   ├── favicon-32.png           # 32×32 PNG
│   ├── apple-touch-icon.png     # 180×180 PNG (iOS)
│   ├── mask-icon.svg            # Monocromático (Safari pinned tab)
│   └── site.webmanifest         # PWA manifest
├── shared/
│   ├── fonts/
│   │   ├── barlow-condensed-400.woff2
│   │   ├── barlow-condensed-700.woff2
│   │   ├── dm-sans-400.woff2
│   │   ├── dm-sans-500.woff2
│   │   └── dm-sans-700.woff2
│   └── core.css                 # @font-face definitions
├── index.html                   # + favicon meta tags
└── dashboard.html               # + favicon meta tags
```

### Favicon — SVG Source

O SVG source será gerado com:
- Fundo: retângulo `#0f172a` com `rx="12"` (cantos arredondados)
- Diamante: polígono com stroke `#00c2e0`, stroke-width 3
- Texto "GX": centralizado, `#00c2e0`, font-weight 700

### Mask Icon — SVG (Safari Pinned Tab)

Versão monocromática para Safari pinned tabs:
- Sem fundo (transparente)
- Apenas o contorno do diamante + "GX" em preenchimento sólido (`#00c2e0` via `color` attribute no `<link>`)
- Formato: SVG puro, sem CSS inline, com `fill="context-fill"` para respeitar a cor do tema

### Fontes — @font-face (com versionamento)

```css
@font-face {
  font-family: 'Barlow Condensed';
  src: url('./fonts/barlow-condensed-400.woff2?v=1.0.0') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
/* ... repeats for each weight ... */
```

O query string `?v=1.0.0` força o browser a re-baixar a fonte quando a versão muda. Isso garante que forks/instalações do projeto sempre recebam a versão correta após atualizações. O número da versão deve ser atualizado no `core.css` sempre que os arquivos `.woff2` forem substituídos.

### HTML — Meta Tags

```html
<link rel="icon" type="image/x-icon" href="assets/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">
<link rel="mask-icon" href="assets/mask-icon.svg" color="#00c2e0">
<link rel="manifest" href="assets/site.webmanifest">
```

---

## Fluxo de Implementação

1. **Gerar SVG** → criar favicon.svg source
2. **Converter favicon** → gerar .ico, .png nos tamanhos necessários
3. **Criar manifest** → site.webmanifest com nome, cores, ícones
4. **Baixar fontes** → obter .woff2 do @fontsource (npm ou download direto)
5. **Atualizar CSS** → substituir @import CDN por @font-face local
6. **Atualizar HTML** → adicionar meta tags de favicon em index.html e dashboard.html
7. **Verificar** → testar carregamento offline, validar favicon no browser

## Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| ~~Fontes .woff2 com licença restritiva~~ | ~~@fontsource usa OFL/SIL — livre para uso~~ ✅ Resolvido — ambas OFL 1.1 |
| ~~Favicon não renderiza em Safari~~ | ~~apple-touch-icon cobre iOS; mask-icon não incluído~~ ✅ Resolvido — `mask-icon.svg` monocromático incluído |
| Cache de fontes antigo | Adicionar cache-control headers ou versionamento se necessário |

## Critérios de Aceite

- [ ] Favicon aparece na aba do browser em login e dashboard
- [ ] Fontes carregam sem conexão com internet
- [ ] Nenhum request externo para jsdelivr.net ou googleapis
- [ ] `font-display: swap` aplicado (sem FOIT)
- [ ] PWA manifest válido (sem erros no DevTools)
- [ ] Safari pinned tab exibe ícone monocromático correto (`mask-icon.svg`)
