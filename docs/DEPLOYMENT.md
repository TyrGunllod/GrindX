# Deploy — GrindX

---

## Estratégia de deploy

O GrindX foi projetado para rodar em containers. O `podman-compose.yml` na raiz orquestra todos os serviços.

Fluxo recomendado:

```
push para main
  → GitHub Actions (tests.yml + lint.yml)
  → build das imagens
  → deploy no servidor via SSH ou registry
  → migrações (manage_db.py upgrade head)
  → restart dos containers
```

---

## CI/CD (GitHub Actions)

Os workflows em `.github/workflows/` executam automaticamente em push e pull requests para `main` e `develop`.

### tests.yml

Três jobs em sequência:

1. **test-api-postgres** — roda os 110 testes com SQLite in-memory (sem banco real no CI)
2. **test-api-sqlserver** — instala ODBC Driver 17 no runner Ubuntu e roda os testes
3. **test-root** — depende dos dois anteriores, valida o monorepo completo

Variáveis de ambiente sensíveis devem ser adicionadas em **Settings → Secrets and variables → Actions** no GitHub:

| Secret | Descrição |
|--------|-----------|
| `SQLSERVER_PASSWORD` | Senha real do usuário (para testes de integração reais) |
| `PROD_SECRET_KEY` | Chave JWT de produção |

### lint.yml

Executa `ruff check` (erros e imports) e `ruff format --check` em todo `packages/`.

---

## Variáveis de ambiente em produção

**Nunca usar** os arquivos `.env` de desenvolvimento em produção. Injetar variáveis via:

- Docker Secrets / Podman Secrets
- Kubernetes ConfigMaps + Secrets
- Variáveis de ambiente do servidor (systemd, Nginx Unit)

Variáveis obrigatórias em produção:

**api-postgres:**
```
DATABASE_URL=postgresql+psycopg://user:senha@host:5432/grindx
SECRET_KEY=<chave-forte-aleatória-32-chars-mínimo>
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["https://seu-dominio.com"]
```

**api-sqlserver:**
```
DB_SERVER=host,porta
DB_DATABASE=nome_banco
DB_USERNAME=usuario
DB_PASSWORD=<senha-real>
SECRET_KEY=<mesma-chave-da-api-postgres>
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["https://seu-dominio.com"]
```

---

## Deploy com containers

```powershell
# Build das imagens
make build

# Subir todos os serviços
make up

# Rodar migrações (sempre antes de iniciar uma nova versão)
make migrate

# Checar logs
make logs

# Parar tudo
make down
```

O `podman-compose.yml` já define os serviços `api-postgres`, `api-sqlserver` e `postgres` (banco). O frontend pode ser servido por Nginx ou qualquer servidor de arquivos estáticos.

---

## Reverse Proxy (Nginx)

O GrindX deve rodar atrás de um reverse proxy para terminação SSL e proteção básica.

Exemplo de configuração Nginx:

```nginx
server {
    listen 443 ssl;
    server_name seu-dominio.com;

    ssl_certificate /etc/ssl/certs/seu-dominio.crt;
    ssl_certificate_key /etc/ssl/private/seu-dominio.key;

    # Frontend
    location / {
        root /var/www/grindx/frontend-webapp;
        try_files $uri $uri/ /index.html;
    }

    # API Postgres
    location /api/postgres/ {
        proxy_pass http://localhost:8002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API SQL Server
    location /api/sqlserver/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Checklist de deploy

- [ ] Variáveis de ambiente de produção configuradas
- [ ] `SECRET_KEY` idêntica nas duas APIs
- [ ] `DEBUG=false` em ambas as APIs
- [ ] `CORS_ORIGINS` restrito ao domínio de produção
- [ ] Migrações aplicadas: `python manage_db.py upgrade head`
- [ ] Dados iniciais populados: `python seed.py` (apenas na primeira vez)
- [ ] SSL/HTTPS ativo via reverse proxy
- [ ] Health checks respondendo: `/health` em cada API
- [ ] Logs estruturados configurados (structlog → arquivo ou agregador)
- [ ] Backup do banco PostgreSQL agendado
