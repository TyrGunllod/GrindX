# Nginx Reverse Proxy Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preparar frontend e nginx.conf para produção com reverse proxy (same-origin API, proxy pass, CSP estático, base tag).

**Architecture:** Nginx serve frontend estático e faz proxy reverso de `/v1/*` para api-postgres:8002. Frontend usa `API_BASE_URL` relativo (`/v1`) que apiService.js detecta e resolve contra `window.location.origin`. CSP é aplicado pelo nginx nos HTMLs, não mais apenas pela API.

**Tech Stack:** nginx, vanilla JS, FastAPI, Python

---

### Task 1: API service suportar URL relativa (same-origin)

**Files:**
- Modify: `apps/frontend-webapp/shared/config.js:16`
- Modify: `apps/frontend-webapp/shared/apiService.js:6-21`

- [ ] **Step 1: Mudar default do API_BASE_URL para caminho relativo**

Em `shared/config.js:16`, trocar:

```js
API_BASE_URL: window.__GRINDX_API_URL || `http://${window.location.hostname}:8002/v1`,
```

para:

```js
API_BASE_URL: window.__GRINDX_API_URL || `/v1`,
```

- [ ] **Step 2: Adicionar detecção de same-origin no apiService.js**

Em `shared/apiService.js`, função `getBaseUrl()`, após a validação de `window.grindx?.config?.API_BASE_URL`, adicionar:

```js
const baseUrl = // result from config checks

// Se começa com /, é caminho relativo — resolve contra origin atual
if (baseUrl.startsWith('/')) {
    return window.location.origin + baseUrl;
}

return baseUrl;
```

O trecho completo da função deve ficar:

```js
const getBaseUrl = () => {
    if (window.GRINDX_CONFIG?.API_BASE_URL) {
        const url = window.GRINDX_CONFIG.API_BASE_URL;
        return url.startsWith('/') ? window.location.origin + url : url;
    }
    if (window.grindx?.config?.API_BASE_URL) {
        const url = window.grindx.config.API_BASE_URL;
        return url.startsWith('/') ? window.location.origin + url : url;
    }
    const hostname = window.location.hostname;
    return `http://${hostname}:8002/v1`;
};
```

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/shared/config.js apps/frontend-webapp/shared/apiService.js
git commit -m "feat(proxy): suportar API_BASE_URL relativo para same-origin"
```

---

### Task 2: Adicionar `<base>` tag nos HTMLs

**Files:**
- Modify: `apps/frontend-webapp/index.html:8`
- Modify: `apps/frontend-webapp/dashboard.html:8`

- [ ] **Step 1: Adicionar base tag no index.html**

Em `apps/frontend-webapp/index.html`, após a linha `<meta name="viewport" ...>`, adicionar:

```html
    <base href="/">
```

- [ ] **Step 2: Adicionar base tag no dashboard.html**

Em `apps/frontend-webapp/dashboard.html`, após a linha `<meta name="viewport" ...>`, adicionar:

```html
    <base href="/">
```

- [ ] **Step 3: Commit**

```bash
git add apps/frontend-webapp/index.html apps/frontend-webapp/dashboard.html
git commit -m "feat(proxy): adicionar base href=/ nos HTMLs"
```

---

### Task 3: Configurar proxy reverso e CSP no nginx.conf

**Files:**
- Modify: `apps/frontend-webapp/nginx.conf`

- [ ] **Step 1: Reescrever nginx.conf com proxy reverso e CSP**

Substituir todo o conteúdo de `apps/frontend-webapp/nginx.conf` por:

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip
    gzip on;
    gzip_types text/css application/javascript text/html image/svg+xml;
    gzip_min_length 256;

    # Segurança
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # CSP para páginas HTML
    add_header Content-Security-Policy "
        default-src 'self';
        script-src 'self' 'unsafe-inline';
        style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com;
        img-src 'self' data: blob:;
        connect-src 'self';
        font-src 'self' https://fonts.gstatic.com;
    " always;

    # Proxy reverso para API
    location /v1/ {
        proxy_pass http://api-postgres:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # assets com cache longo
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|webp|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Mapeamento de rotas SPA
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/frontend-webapp/nginx.conf
git commit -m "feat(proxy): configurar proxy reverso /v1/ e CSP no nginx"
```

---

### Task 4: CSP da API simplificar quando atrás de proxy

**Files:**
- Modify: `apps/api-postgres/app/core/config.py:147-153`

- [ ] **Step 1: Adicionar flag PROXY_MODE no settings**

Em `apps/api-postgres/app/core/config.py`, na classe `Settings`, adicionar:

```python
PROXY_MODE: bool = False
```

E ajustar a property `csp_connect_srcs`:

```python
    @property
    def csp_connect_srcs(self) -> list[str]:
        """URLs permitidas no CSP connect-src."""
        if self.PROXY_MODE:
            return ["'self'"]
        srcs = ["'self'", "http://localhost:8001", "http://localhost:8002"]
        if self.DEV_NETWORK_IP:
            srcs.append(f"http://{self.DEV_NETWORK_IP}:8001")
            srcs.append(f"http://{self.DEV_NETWORK_IP}:8002")
        return srcs
```

- [ ] **Step 2: Commit**

```bash
git add apps/api-postgres/app/core/config.py
git commit -m "feat(proxy): adicionar PROXY_MODE para simplificar CSP da API"
```

---

### Task 5: Verificar lint

- [ ] **Step 1: Rodar ruff**

```powershell
ruff check apps/frontend-webapp/ apps/api-postgres/
```

Expected: sem erros.

- [ ] **Step 2: Se houver erros, corrigir e commitar**

```bash
git add -A
git commit -m "fix: corrigir lint apos ajustes de proxy"
```
