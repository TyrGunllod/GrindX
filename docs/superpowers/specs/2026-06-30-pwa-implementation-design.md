# PWA Implementation — Design

> Tornar o GrindX um Progressive Web App instalável com suporte offline básico.

## Service Worker

Criar `apps/frontend-webapp/sw.js` com:
- Estratégia **Network First** para `index.html`, `dashboard.html` e demais páginas (usuário autenticado sempre quer dado fresco)
- Estratégia **Cache First** para assets estáticos: CSS, JS, imagens, font-awesome, manifest
- Cache dinâmico para requisições de API (fallback para última resposta em caso de offline)
- Cache nomeado como `grindx-v1`

Registrar em `apps/frontend-webapp/shared/app.js` no bloco de inicialização:
```javascript
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js');
    });
}
```

## Ícones

Gerar dois ícones a partir do favicon existente:
- `assets/icon-192.png` (192x192)
- `assets/icon-512.png` (512x512)

Adicionar ao `assets/site.webmanifest`:
```json
{ "src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png" },
{ "src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
```

## Meta Tags

No `<head>` de `index.html` e `dashboard.html`:
```html
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
```

## start_url

Ajustar `start_url` no `site.webmanifest` de `/index.html` para `/dashboard.html` (usuário logado será redirecionado ao login se não autenticado).
