<!-- title: Segurança — GrindX | updated: 2026-08-14 -->

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
9. Qualquer perfil pode obter o próprio perfil via `GET /v1/auth/me` (diferente de `GET /v1/usuarios/`, que exige `operador` ou superior)

### Validação Cruzada

A `api-sqlserver` **não emite nem valida tokens JWT** — seus endpoints (`/v1/produtos/*`, `/health`) são públicos, sem autenticação.

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
| `operador` | Acesso operacional — CRUD em usuários, com restrições para manipular perfis `admin` |
| `leitura` | Somente leitura — sem criação, alteração ou exclusão |

> A hierarquia é `admin ≥ operador ≥ leitura` (definida em `packages/shared/security/permissions.py`).

> `POST /v1/auth/forgot-password` é público (sem autenticação). `POST /v1/auth/change-password` exige autenticação atual.

### Matriz de Permissões

| Recurso | admin | operador | leitura |
|---------|-------|----------|---------|
| `GET /v1/usuarios/` | ✅ | ✅ | ❌ |
| `POST /v1/usuarios/` | ✅ | ✅¹ | ❌ |
| `PUT /v1/usuarios/{id}` | ✅ | ✅¹ | ❌ |
| `DELETE /v1/usuarios/{id}` | ✅ | ✅¹ | ❌ |
| `GET /v1/portal/menu` | ✅ | ✅ | ✅ |
| `POST/PUT/DELETE /v1/portal/*` | ✅ | ❌ | ❌ |
| `GET /v1/auth/me` | ✅ | ✅ | ✅ |
| `POST /v1/auth/change-password` | ✅ | ✅ | ✅ |

> ¹ Todos os endpoints `GET/POST/PUT/DELETE /v1/usuarios*` usam `require_role_or_higher("operador")`. O `operador` tem acesso, mas apenas o `admin` pode criar, alterar ou desativar usuários com perfil `admin` (e apenas o `admin` pode atribuir o perfil `admin`).

> **Produtos:** não existe router de produtos na api-postgres. As consultas de produto são read-only na api-sqlserver, via `GET /v1/produtos/por-codigo` e `GET /v1/produtos/por-descricao` (protheus_router).

A implementação fica em `packages/shared/security/` e `apps/api-postgres/app/auth/dependencies.py`.

---

## Hash de Senha

Todas as senhas são armazenadas com bcrypt, usado **diretamente** (`import bcrypt` em `packages/shared/security/jwt.py`) — não utiliza `passlib`:

```python
from shared.security.jwt import gerar_hash_senha, verificar_senha

hash = gerar_hash_senha("senha123")      # armazena no banco
ok = verificar_senha("senha123", hash)   # True
```

Nunca armazenar senha em texto plano. Nunca logar senhas.

---

## Middlewares de Segurança

A `api-postgres` aplica quatro middlewares automáticos: SecurityHeaders, RateLimit, RequestId e CORS.

A `api-sqlserver` aplica apenas SecurityHeaders, RequestId e CORS — **não possui rate limit**:

### SecurityHeadersMiddleware

Adiciona headers de segurança em todas as respostas:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src <origens>
```

O `connect-src` do CSP inclui as origens das duas APIs (`localhost:8001/8002` e o `DEV_NETWORK_IP` quando definido). Nas rotas de documentação (`/v1/docs`, `/v1/redoc`, `/v1/openapi.json`) o CSP é mais permissivo para permitir os CDNs usados pelo Swagger UI.

### RateLimitMiddleware

Aplicado **apenas na `api-postgres`**, usando a biblioteca `limits`/SlowAPI com janela deslizante em memória. Usa chaves duplas: rate limit por `user_id` (extraído do JWT) em endpoints autenticados e por IP em endpoints não autenticados.

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
# Desenvolvimento — default da api-postgres
CORS_ORIGINS=["http://localhost:3000"]

# Produção — restringir ao domínio real (nunca "*")
CORS_ORIGINS=["https://seu-dominio.com"]
```

Em desenvolvimento, além do valor de `CORS_ORIGINS`, os defaults adicionam automaticamente `http://localhost:3000`, `http://localhost:8101`, `http://127.0.0.1:8101`, `https://localhost:8443` e `https://127.0.0.1:8443` (mais as origens de `DEV_NETWORK_IP` quando definido). **Não** usa `["*"]` como default — e, em produção, `*` é rejeitado na validação.

A `api-sqlserver` aceita apenas método GET (read-only), reforçado pelo middleware CORS (`allow_methods=["GET"]`).

---

## Boas Práticas de Produção

- Trocar `SECRET_KEY` para valor gerado aleatoriamente antes do deploy
- Usar `DEBUG=false` em produção — evita exposição de stack traces
- Restringir `CORS_ORIGINS` ao domínio real
- Rodar atrás de reverse proxy com SSL/HTTPS (ver [`DEPLOYMENT.md`](DEPLOYMENT.md))
- Agendar rotação periódica da `SECRET_KEY` (invalida todos os tokens ativos)
- Monitorar logs de autenticação para detectar força bruta
- Nunca versionar arquivos `.env` com credenciais reais
