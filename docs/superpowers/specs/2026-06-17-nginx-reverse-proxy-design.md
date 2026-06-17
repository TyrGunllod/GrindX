# Nginx Reverse Proxy Readiness

## Problem

O frontend do GrindX não está totalmente preparado para ser servido por nginx como reverse proxy em produção. APIs são chamadas em porta fixa (`:8002`) em vez de same-origin, o nginx.conf não tem proxy reverso, e faltam headers de segurança nos HTML estáticos.

## Escopo

Apenas configuração de proxy e ajustes no frontend para suportar same-origin API calls. Sem mudanças na lógica de negócio.

## Itens de Trabalho

### 1. API_URL suportar same-origin (`/v1`)

**Problema:** `apiService.js:20` sempre constrói `http://${hostname}:8002/v1`.

**Solução:** Detectar se `API_BASE_URL` começa com `/` (caminho relativo) e nesse caso usar `window.location.origin` como base.

```js
// shared/config.js
API_BASE_URL: window.__GRINDX_API_URL || '/v1',
```

```js
// shared/apiService.js - getBaseUrl()
if (baseUrl.startsWith('/')) {
  return window.location.origin + baseUrl;
}
```

### 2. Proxy reverso no nginx.conf

Adicionar location `/v1/` que proxy passa para `api-postgres:8002` e headers de segurança.

```nginx
location /v1/ {
    proxy_pass http://api-postgres:8002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Também adicionar CSP nos estáticos com `style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com` e `font-src 'self' https://fonts.gstatic.com`.

### 3. `<base>` tag nos HTMLs

Adicionar `<base href="/">` no `<head>` de `index.html` e `dashboard.html` para garantir que assets relativos funcionem mesmo se servidos em subpath futuramente.

### 4. CSP headers nos HTML estáticos

Adicionar `add_header Content-Security-Policy` no nginx.conf para os arquivos HTML, incluindo:
- `default-src 'self'`
- `script-src 'self' 'unsafe-inline'`
- `style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com`
- `img-src 'self' data: blob:`
- `connect-src 'self'`
- `font-src 'self' https://fonts.gstatic.com`

### 5. Ajustar CSP da API para cenário proxy

O `SecurityHeadersMiddleware` atualmente emite CSP com `connect-src` incluindo portas `:8001`, `:8002`. Quando atrás de proxy, basta `'self'`. Ajustar lógica para quando `PROXY_MODE=true`.

## Não Escopo

- Migração para HTTPS (certificates, SSL termination)
- Cache layer (Redis, CDN)
- Load balancing
- Health check endpoints no nginx
- Configuração de múltiplos upstreams (api-sqlserver)
