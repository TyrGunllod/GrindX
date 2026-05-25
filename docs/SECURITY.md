<!-- title: Segurança — GrindX | updated: 2026-05-25 -->

# Segurança — GrindX

---

## Autenticação (JWT)

O GrindX usa JSON Web Tokens (JWT) com par de tokens de curta e longa duração.

### Fluxo

1. Cliente envia `POST /v1/auth/token` com `username` e `password`
2. A `api-postgres` valida as credenciais contra o hash bcrypt no banco
3. Retorna `access_token` (expira em 30 min) e `refresh_token` (expira em 7 dias)
4. Cliente inclui `Authorization: Bearer <access_token>` em todas as requisições
5. Quando o access token expira, cliente usa `POST /v1/auth/refresh` com o refresh token
6. Se esquecer a senha, usa `POST /v1/auth/forgot-password` com o username
7. Sistema gera senha temporária, envia por email e só altera o hash após confirmação de envio
8. Usuário pode alterar a própria senha via `POST /v1/auth/change-password`
9. Qualquer perfil pode obter o próprio perfil via `GET /v1/auth/me` (diferente de `GET /usuarios/`, que é admin-only)

### Validação Cruzada

A `api-sqlserver` **não emite tokens** — apenas valida tokens emitidos pela `api-postgres`. Para isso, as duas APIs precisam da mesma `SECRET_KEY` no `.env`.

### Configuração

```env
# api-postgres/.env
SECRET_KEY=chave-forte-aleatória-mínimo-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# api-sqlserver/.env — mesma chave
SECRET_KEY=chave-forte-aleatória-mínimo-32-chars
```

Para gerar uma chave segura:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## Controle de Acesso (RBAC)

O acesso é controlado por perfis definidos no campo `role` do model `Usuario`.

### Perfis

| Role | Descrição |
|------|-----------|
| `admin` | Acesso total — CRUD em todos os recursos |
| `operador` | Leitura e criação — sem delete e sem gestão de usuários |

> `POST /v1/auth/forgot-password` é público (sem autenticação). `POST /v1/auth/change-password` exige autenticação atual.

### Matriz de Permissões

| Recurso | admin | operador |
|---------|-------|----------|
| `GET /usuarios/` | ✅ | ❌ |
| `POST /usuarios/` | ✅ | ❌ |
| `PUT /usuarios/{id}` | ✅ | ❌ |
| `DELETE /usuarios/{id}` | ✅ | ❌ |
| `GET /produtos/` | ✅ | ✅ |
| `POST /produtos/` | ✅ | ✅ |
| `PUT /produtos/{id}` | ✅ | ✅ |
| `DELETE /produtos/{id}` | ✅ | ❌ |
| `GET /portal/menu` | ✅ | ✅ |
| `POST/PUT/DELETE /portal/*` | ✅ | ❌ |
| `GET /v1/auth/me` | ✅ | ✅ |
| `POST /v1/auth/change-password` | ✅ | ✅ |

A implementação fica em `packages/shared/security/` e `packages/api-postgres/app/auth/dependencies.py`.

---

## Hash de Senha

Todas as senhas são armazenadas com bcrypt via `passlib`:

```python
from shared.security.jwt import gerar_hash_senha, verificar_senha

hash = gerar_hash_senha("senha123")      # armazena no banco
ok = verificar_senha("senha123", hash)   # True
```

Nunca armazenar senha em texto plano. Nunca logar senhas.

---

## Middlewares de Segurança

Ambas as APIs aplicam três middlewares automáticos:

### SecurityHeadersMiddleware

Adiciona headers de segurança em todas as respostas:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

### RateLimitMiddleware

Limita o número de requisições por IP por janela de tempo.

```env
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

Rotas excluídas do rate limit: `/health`, `/v1/docs`, `/v1/redoc`, `/v1/openapi.json`.

Retorna HTTP 429 quando excedido.

### RequestIdMiddleware

Gera um `X-Request-ID` único por requisição para rastreabilidade nos logs.

---

## CORS

Configurado via `CORS_ORIGINS` no `.env`:

```env
# Desenvolvimento
CORS_ORIGINS=["*"]

# Produção — restringir ao domínio real
CORS_ORIGINS=["https://seu-dominio.com"]
```

A `api-sqlserver` aceita apenas método GET (read-only), reforçado pelo middleware CORS.

---

## Boas Práticas de Produção

- Trocar `SECRET_KEY` para valor gerado aleatoriamente antes do deploy
- Usar `DEBUG=false` em produção — evita exposição de stack traces
- Restringir `CORS_ORIGINS` ao domínio real
- Rodar atrás de reverse proxy com SSL/HTTPS (ver [`DEPLOYMENT.md`](DEPLOYMENT.md))
- Agendar rotação periódica da `SECRET_KEY` (invalida todos os tokens ativos)
- Monitorar logs de autenticação para detectar força bruta
- Nunca versionar arquivos `.env` com credenciais reais
