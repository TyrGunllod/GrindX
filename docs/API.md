<!-- title: API Reference — GrindX | updated: 2026-05-20 -->

# API Reference — GrindX

Base URL local: `http://localhost:8002/v1`
Documentação interativa: `http://localhost:8002/v1/docs` (Swagger UI)

---

## Autenticação

Todos os endpoints (exceto `/health` e `/v1/auth/token`) exigem o header:

```
Authorization: Bearer <access_token>
```

### `POST /v1/auth/token`

Emite um par de tokens JWT.

**Body:**

```json
{ "username": "admin", "password": "admin123" }
```

**Response 200:**

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### `POST /v1/auth/refresh`

Renova o access token usando o refresh token.

**Body:**

```json
{ "refresh_token": "eyJ..." }
```

**Response 200:**

```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

---

## Health Check

### `GET /health`

Verifica se a API está respondendo. Não exige autenticação.

**Response 200:**

```json
{ "status": "ok", "service": "GrindX API Postgres", "version": "0.1.0" }
```

---

## Usuários

### `GET /v1/usuarios/`

Lista todos os usuários. Requer perfil `admin`.

**Response 200:**

```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@grindx.com",
    "nome_completo": "Administrador",
    "role": "admin",
    "ativo": true
  }
]
```

### `POST /v1/usuarios/`

Cria um novo usuário. Requer perfil `admin`.

**Body:**

```json
{
  "username": "novo",
  "email": "novo@grindx.com",
  "nome_completo": "Novo Usuário",
  "password": "senha123",
  "role": "operador"
}
```

**Response 201:** Objeto do usuário criado (sem `password`).

### `GET /v1/usuarios/{id}`

Retorna um usuário pelo ID. Requer perfil `admin` ou o próprio usuário.

### `PUT /v1/usuarios/{id}`

Atualiza dados de um usuário. Requer perfil `admin`.

### `DELETE /v1/usuarios/{id}`

Remove um usuário. Requer perfil `admin`.

---

## Produtos

### `GET /v1/produtos/`

Lista produtos. Acessível para `admin` e `operador`.

**Query params opcionais:** `skip` (int), `limit` (int)

**Response 200:**

```json
[
  {
    "id": 1,
    "nome": "Produto A",
    "descricao": "Descrição do produto",
    "preco": 49.90,
    "estoque": 100,
    "ativo": true
  }
]
```

### `POST /v1/produtos/`

Cria um produto. Requer `admin` ou `operador`.

**Body:**

```json
{
  "nome": "Produto B",
  "descricao": "Descrição",
  "preco": 29.90,
  "estoque": 50
}
```

**Response 201:** Objeto do produto criado.

### `GET /v1/produtos/{id}`

Retorna produto pelo ID.

### `PUT /v1/produtos/{id}`

Atualiza produto. Requer `admin` ou `operador`.

### `DELETE /v1/produtos/{id}`

Remove produto. Requer `admin`.

---

## Portal (Estrutura de Menu)

Esses endpoints gerenciam a árvore de navegação dinâmica do portal frontend.

### `GET /v1/portal/menu`

Retorna a estrutura completa de abas e módulos para o menu lateral.

**Response 200:**

```json
[
  {
    "id": 1,
    "nome": "Administração",
    "icone": "settings",
    "ordem": 1,
    "modulos": [
      {
        "id": 1,
        "nome": "Usuários",
        "url": "/modules/users/index.html",
        "icone": "users",
        "ordem": 1
      }
    ]
  }
]
```

### `POST /v1/portal/abas`

Cria uma nova aba no menu. Requer `admin`.

**Body:**

```json
{ "nome": "Logística", "icone": "truck", "ordem": 2 }
```

### `PUT /v1/portal/abas/{id}`

Atualiza uma aba. Requer `admin`.

### `DELETE /v1/portal/abas/{id}`

Remove uma aba e seus módulos. Requer `admin`.

### `POST /v1/portal/modulos`

Cria um módulo dentro de uma aba. Requer `admin`.

**Body:**

```json
{
  "aba_id": 1,
  "nome": "Estoque",
  "url": "/modules/estoque/index.html",
  "icone": "package",
  "ordem": 1
}
```

### `PUT /v1/portal/modulos/{id}`

Atualiza um módulo. Requer `admin`.

### `DELETE /v1/portal/modulos/{id}`

Remove um módulo. Requer `admin`.

---

## Temas / Skins

Endpoints para gerenciar o sistema de skins visuais por empresa. O `company_id` é obtido automaticamente do token JWT do usuário logado. Requer perfil `admin`.

### `GET /v1/themes/`

Lista todos os temas da empresa do usuário logado.

**Response 200:**
```json
[
  {
    "id": 1,
    "company_id": 1,
    "name": "Corporate Blue",
    "is_active": true,
    "colors": {"--skin-primary": "#0055aa", "--skin-danger": "#ef4444", ...},
    "fonts": {"heading": "Barlow Condensed", "body": "DM Sans"},
    "tokens": {"--skin-radius-md": "0.5rem", "--skin-shadow-card": "0 10px 25px rgba(0,0,0,0.1)", ...},
    "icon_library": "fontawesome",
    "logo_url": "/uploads/logos/uuid.jpg",
    "company_name": "Acme Corp",
    "copyright_text": "© 2026 Acme Corp. Todos os direitos reservados.",
    "criado_em": "2026-05-20T10:00:00",
    "atualizado_em": "2026-05-20T14:30:00"
  }
]
```

### `POST /v1/themes/`

Cria um novo tema para a empresa do usuário logado.

**Body:**
```json
{
  "name": "Acme Blue",
  "colors": {"--skin-primary": "#0055aa"},
  "fonts": {"heading": "Inter", "body": "Roboto"},
  "tokens": {"--skin-radius-md": "0.75rem"},
  "icon_library": "fontawesome",
  "logo_url": null,
  "company_name": "Acme Corp",
  "copyright_text": "© 2026 Acme Corp. Todos os direitos reservados."
}
```

**Response 201:** Objeto do tema criado.

### `GET /v1/themes/{id}`

Retorna um tema pelo ID. Requer que o tema pertença à empresa do usuário.

### `PUT /v1/themes/{id}`

Atualiza um tema existente. Todos os campos são opcionais.

### `DELETE /v1/themes/{id}`

Remove um tema. Requer `admin`. Não é possível deletar um tema ativo.

### `POST /v1/themes/{id}/activate`

Ativa um tema (desativa automaticamente os outros da mesma empresa).

**Response 200:** Objeto do tema ativado.

### `GET /v1/themes/active`

Retorna o tema ativo da empresa do usuário logado. Usado pelo `skinLoader` no boot do frontend.

**Response 200:** Objeto do tema ativo ou 404 se nenhum encontrado.

### `GET /v1/themes/templates`

Lista os templates de skin pré-configurados disponíveis.

**Response 200:**
```json
[
  {"slug": "corporate-blue", "name": "Corporate Blue", "preview": {"--skin-primary": "#0055aa", ...}},
  {"slug": "dark-minimal", "name": "Dark Minimal", "preview": {...}}
]
```

### `POST /v1/themes/{id}/logo`

Upload de logo para o tema (multipart/form-data). Tipos aceitos: jpeg, png, svg, gif. Máximo 5MB.

### `GET /v1/themes/{id}/history`

Retorna o histórico de alterações de um tema.

### `POST /v1/themes/from-template`

Cria um tema a partir de um template existente.

**Body:**
```json
{
  "template_slug": "corporate-blue",
  "name": "Corporate Blue"
}
```

**Response 201:** Objeto do tema criado.

---

## API SQL Server (porta 8001)

Base URL local: `http://localhost:8001/v1`

Aceita apenas `GET`. Tokens JWT emitidos pela `api-postgres` são válidos aqui desde que `SECRET_KEY` seja idêntica nas duas APIs.

### `GET /health`

```json
{ "status": "ok", "service": "GrindX API SQL Server" }
```

### `GET /v1/clientes/`

Lista registros de clientes do SQL Server. Requer token válido.

---

## Códigos de Erro Padrão

| Código | Significado |
|--------|-------------|
| 400 | Dados inválidos no body |
| 401 | Token ausente ou expirado |
| 403 | Permissão insuficiente para o perfil |
| 404 | Recurso não encontrado |
| 422 | Falha de validação Pydantic |
| 429 | Rate limit excedido (100 req/min por padrão) |
| 500 | Erro interno — consultar logs estruturados |
