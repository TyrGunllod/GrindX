# HTTPS Implementation — Design

> Adicionar suporte HTTPS nos ambientes dev e produção do GrindX.

## Arquitetura

### Produção (Docker)

O nginx do container `grindx-frontend` será o terminador TLS. Todo tráfego externo chega em 443 com certificado, e o nginx faz proxy reverso para as APIs em HTTP interno (localhost:8001/8002).

**Mudanças no `apps/frontend-webapp/nginx.conf`:**
- Adicionar bloco `server` escutando na porta 443 com SSL
- Redirecionar HTTP (80) para HTTPS (443)
- Definir caminhos dos certificados como volumes montados via compose
- CSP `connect-src` atualizado para incluir `https://`

**Mudanças no `compose.yaml`:**
- Mapear porta 443:443
- Montar volumes com certificados (ex: `./certs/:/etc/nginx/certs/`)

### Desenvolvimento (Local)

Duas opções viáveis:

**Opção A — mkcert + uvicorn com SSL (recomendada)**
- Instalar `mkcert` (gera CAs locais confiáveis)
- Gerar certificado para `localhost`, `127.0.0.1` e IP da máquina
- Servir frontend com `python -m http.server` via proxy reverso local (ex: `uvicorn` com SSL ou `caddy`)
- Ou usar `uvicorn` para servir os static files com `--ssl-keyfile` e `--ssl-certfile`
- APIs já rodam em uvicorn — adicionar flags SSL
- Criar script `scripts/dev-https.ps1` que gerencia certs + inicia tudo

**Opção B — Caddy como reverse proxy dev**
- Caddy faz TLS automático via Let's Encrypt + auto-redirect HTTP→HTTPS
- Um `Caddyfile` define o proxy reverso para frontend e APIs
- Mais simples que configurar nginx manualmente

## Configuração

### Certificados (mkcert)

```powershell
# Instalar mkcert (uma vez)
choco install mkcert  # ou winget install mkcert

# Criar CA local confiável
mkcert -install

# Gerar certificado para dev
mkcert -key-file .certs/dev-key.pem -cert-file .certs/dev-cert.pem localhost 127.0.0.1 192.168.x.x
```

### Frontend

`apps/frontend-webapp/shared/config.js` — URL da API usar `window.location.protocol` em vez de `http://` fixo:
```javascript
API_BASE_URL: window.__GRINDX_API_URL || `${window.location.protocol}//${window.location.hostname}:8002/v1`
```

### APIs

Uvicorn aceita flags SSL diretamente:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --ssl-keyfile=.certs/dev-key.pem --ssl-certfile=.certs/dev-cert.pem
```

### CORS

`apps/api-postgres/app/core/config.py` — `CORS_ORIGINS` deve aceitar `https://` origins em produção.

### CSP

`apps/api-sqlserver/app/core/config.py` e `apps/frontend-webapp/nginx.conf` — `connect-src` deve incluir `https://localhost:8002`, `https://127.0.0.1:8002`.

## Arquivos afetados

| Arquivo | Mudança |
|---------|---------|
| `apps/frontend-webapp/nginx.conf` | Adicionar servidor SSL 443 + redirect 80→443 |
| `apps/frontend-webapp/shared/config.js` | Protocolo dinâmico na URL da API |
| `compose.yaml` | Porta 443 + volume de certificados |
| `apps/api-postgres/app/core/config.py` | CORS aceitar HTTPS |
| `apps/api-sqlserver/app/core/config.py` | CSP aceitar HTTPS |
| `.certs/` (novo) | Certificados dev (gitignored) |
| `scripts/dev-https.ps1` (novo) | Script para dev com HTTPS |
