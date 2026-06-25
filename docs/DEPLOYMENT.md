<!-- title: Deploy — GrindX | updated: 2026-06-17 -->

# Deploy — GrindX

---

## Estratégia de Deploy

O GrindX foi projetado para rodar em containers. O `podman-compose.yml` na raiz orquestra os serviços.

Fluxo:

```
push para main
  → GitHub Actions (release.yml)
    → test-api-postgres (SQLite in-memory)
    → test-api-sqlserver (SQLite in-memory)
    → test-root (depende dos dois anteriores)
    → lint (ruff check + format)
    → semantic release (versionamento automático)
  → build das imagens
  → deploy no servidor
  → make migrate (alembic upgrade head)
  → restart dos containers
```

---

## CI/CD (GitHub Actions)

Workflow único em `.github/workflows/release.yml` — executa em push para `main`.

### Jobs (sequenciais):

1. **test-api-postgres** — testes com SQLite in-memory, `--cov=app --cov-fail-under=70`
2. **test-api-sqlserver** — testes com SQLite via `DB_URL_OVERRIDE`
3. **test-root** — depende de 1 e 2, valida o monorepo completo
4. **lint** — `ruff check` (select E, F, I — ignore E501) + `ruff format --check`
5. **release** — `python-semantic-release` com parser angular; gera changelog e tag automática

### Secrets do GitHub

| Secret | Descrição |
|--------|-----------|
| `SQLSERVER_PASSWORD` | Senha do usuário SQL Server (testes reais) |
| `PROD_SECRET_KEY` | Chave JWT de produção |

---

## Variáveis de Ambiente em Produção

**Nunca usar** `.env` de desenvolvimento. Injetar via secrets do container/plataforma.

Shannon entropy validation: `SECRET_KEY` precisa de **entropia mínima de 3.5 bits/caractere** (validado via Pydantic `field_validator`).

### `api-postgres`

```
DATABASE_URL=postgresql+psycopg://user:senha@host:5432/grindx
SECRET_KEY=<chave-aleatoria-32-chars-min-entropia-3.5>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_NAME="ERP API Postgres"
APP_VERSION=1.19.0
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=["https://seu-dominio.com"]
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# SMTP (recuperação de senha)
SMTP_HOST=smtp.seuprovedor.com
SMTP_PORT=587
SMTP_USER=seu@email.com
SMTP_PASS=senha_real
SMTP_USE_TLS=true
EMAIL_FROM=noreply@seudominio.com
EMAIL_FROM_NAME=GrindX

# Import de módulos (opcional)
IMPORT_DIR=

# Skins snapshot (opcional — default: apps/frontend-webapp/skins)
SKINS_DIR=
```

### `api-sqlserver`

```
DB_SERVER=host,porta
DB_DATABASE=nome_banco
DB_USERNAME=usuario
DB_PASSWORD=<senha-real>
DB_DRIVER=ODBC Driver 17 for SQL Server
SECRET_KEY=<mesma-chave-da-api-postgres>
APP_NAME="ERP API SQL Server"
APP_VERSION=1.19.0
DEBUG=false
ENVIRONMENT=production
ENABLE_CACHE=false
LOG_LEVEL=INFO
CORS_ORIGINS=["https://seu-dominio.com"]
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Para testes: DB_URL_OVERRIDE=sqlite:///:memory:
```

---

## Deploy com Containers

```powershell
# Build das imagens
make build

# Subir serviços
make up

# Rodar migrações (sempre antes de nova versão)
make migrate

# Dados iniciais (apenas primeira vez)
make seed

# Logs
make logs

# Parar
make down
```

O `podman-compose.yml` define três serviços:

| Serviço | Porta host | Imagem |
|---------|-----------|--------|
| `frontend` | 8101 (host) → 80 (container) | nginx:alpine (estático) |
| `api-sqlserver` | 8001 | python:3.12-slim |
| `api-postgres` | 8002 | python:3.12-slim |

O pacote `packages/` é copiado para a imagem (`/app/packages/`) e sobrescrito por bind mount em `compose.yaml` (`./packages:/app/packages:z`) para facilitar o desenvolvimento. Em produção standalone (sem compose), o `shared` já está embutido na imagem. O frontend é servido via Nginx oficial com cache de assets e gzip.

Os containers rodam com usuário não-root (UID 1001) e health checks configurados.

---

## Semantic Release

Configurado via `pyproject.toml` (raiz) — `python-semantic-release` com parser **angular**.

- A versão é definida em `APP_VERSION` em cada `config.py` (atualmente `1.36.1`)
- O build hook `scripts/update_frontend_version.py` sincroniza `apps/frontend-webapp/version.json`
- O CI gera automaticamente: bump de versão, changelog, tag e release no GitHub

---

## Reverse Proxy (Nginx)

O `nginx.conf` do frontend serve estáticos e faz proxy reverso da API (`/v1/` → `localhost:8002`). Aplica security headers e CSP:

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com;
  style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com;
  img-src 'self' data: blob: http://localhost:8002 https://ui-avatars.com;
   connect-src 'self' http://localhost:8001 http://127.0.0.1:8001 http://localhost:8002 http://127.0.0.1:8002;
  font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com;
```

A API é acessada via same-origin (`/v1/`) em produção, eliminando CORS. Em desenvolvimento, o `config.js` detecta a porta `8101` e usa `http://localhost:8002/v1` diretamente.

### Volumes no compose.yaml

Os paths usam `${PWD}` (portátil entre WSL e Linux nativo):

```yaml
volumes:
  - ${PWD}/apps/frontend-webapp/modules:/usr/share/nginx/html/modules
  - ${HOME:-.}/Containers/volumes/grindx/frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro,z
```

Para desenvolvimento (hot-reload nos módulos), mantenha o volume de `modules`. Para produção sem importador, pode remover o volume de módulos do frontend (os módulos já estão na imagem).

Para ambientes que exigem SSL, adicione um nginx externo apontando para o container:

```nginx
server {
    listen 443 ssl;
    server_name seu-dominio.com;

    ssl_certificate /etc/ssl/certs/seu-dominio.crt;
    ssl_certificate_key /etc/ssl/private/seu-dominio.key;

    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

O frontend já aplica CSP, security headers e cache de assets. A API é acessada via same-origin (`/v1/`), eliminando CORS em produção.

---

## Checklist de Deploy

- [ ] Variáveis de ambiente de produção configuradas
- [ ] `SECRET_KEY` idêntica nas duas APIs (com entropia Shannon ≥ 3.5 bits/char)
- [ ] `DEBUG=false` em ambas as APIs
- [ ] `ENVIRONMENT=production` em ambas
- [ ] `CORS_ORIGINS` restrito ao domínio de produção (nunca `*`)
- [ ] Migrações aplicadas: `make migrate`
- [ ] Dados iniciais populados: `make seed` (apenas na primeira vez)
- [ ] SSL/HTTPS ativo via reverse proxy
- [ ] Health checks respondendo: `/v1/health` em cada API
- [ ] Rate limiting ativo (100 requests/min por padrão)
- [ ] Pacote `packages/` presente no diretório do deploy (copiado por `make deploy`)
- [ ] Cache TTLCache operacional (15 min TTL para temas/usuários/portal)
- [ ] Logs configurados (nível INFO ou superior)
- [ ] Backup do banco PostgreSQL agendado
