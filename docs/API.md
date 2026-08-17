<!-- title: API Reference — GrindX | updated: 2026-08-17 -->

# API Reference — GrindX

Base URL local: `http://localhost:8002/v1`
Documentação interativa: `http://localhost:8002/v1/docs` (Swagger UI)

---

## Autenticação

A maioria dos endpoints exige token JWT no header:

```
Authorization: Bearer <access_token>
```

**Endpoints públicos** (não exigem autenticação): `/health`, `/v1/auth/token`, `/v1/auth/forgot-password`, `/v1/cbo/{codigo}`, `/v1/cep/{cep}` e todos os endpoints da `api-sqlserver` (que não valida JWT).

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

### `GET /v1/auth/me`

Retorna o perfil do usuário autenticado. Qualquer role pode acessar.

**Response 200:**

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@grindx.com",
  "nome_completo": "Administrador",
  "role": "admin",
  "ativo": true,
  "theme_preference": "dark",
  "empresa_id": 1
}
```

### `PUT /v1/auth/me`

Atualiza o perfil do próprio usuário autenticado. Todos os campos são opcionais.

**Body:**

```json
{
  "email": "novo@email.com",
  "nome_completo": "Novo Nome",
  "theme_preference": "dark"
}
```

**Response 200:** Objeto do usuário atualizado.

### `POST /v1/auth/change-password`

Altera a senha do usuário autenticado. Requer auth.

**Body:**

```json
{
  "current_password": "senha123",
  "new_password": "novaSenha456"
}
```

**Response 200:** `{ "message": "Senha alterada com sucesso" }`

### `POST /v1/auth/logout`

Encerra a sessão do usuário autenticado. Fecha a sessão aberta mais recente do usuário, gravando `logout_at`, `duracao_segundos` e motivo `logout`. Requer auth.

**Response 200:** `{ "message": "Sessão encerrada." }`

O frontend chama esse endpoint (fire-and-forget, tolerante a falha) no logout manual e no logout por inatividade — ver `shared/serverLogout.js`.

### `POST /v1/auth/forgot-password`

Gera uma senha temporária e envia por e-mail. Não requer auth.

**Body:**

```json
{ "username": "admin" }
```

**Response 200:** `{ "message": "Nova senha enviada para o e-mail cadastrado." }`

**Response 503:** Retornado se o envio de e-mail falhar.

---

## Health Check

### `GET /health`

Verifica se a API está respondendo e a conectividade com o banco. Não exige autenticação.

**Response 200:**

```json
{
  "status": "healthy",
  "service": "ERP API Postgres",
  "version": "1.69.1",
  "database": { "postgres": "connected" },
  "timestamp": "2026-08-14T12:00:00Z"
}
```

**Response 503:** Retornado quando o banco está `disconnected`/`degraded` ou faltam tabelas críticas — `status` passa a `"degraded"`, `database.postgres` reflete o estado e `details` traz `missing_tables`/`error`.

---

## Usuários

Endpoints de gestão de usuários. Requerem perfil `operador` (ou superior). Apenas a criação/edição de usuários com perfil `admin` exige role `admin`.

### `GET /v1/usuarios/`

Lista todos os usuários (paginado, filtrável por role). Requer perfil `operador` (ou superior).

**Query params:** `page` (default 1), `page_size` (default 20), `role` (opcional)

**Response 200:**

```json
{
  "items": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@grindx.com",
      "nome_completo": "Administrador",
      "role": "admin",
      "ativo": true,
      "theme_preference": null,
      "empresa_id": 1
    }
  ],
  "total": 1
}
```

### `POST /v1/usuarios/`

Cria um novo usuário. Requer perfil `operador` (ou superior).

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

Retorna um usuário pelo ID. Requer perfil `operador` (ou superior).

### `PUT /v1/usuarios/{id}`

Atualiza dados de um usuário. Requer perfil `operador` (ou superior).

### `DELETE /v1/usuarios/{id}`

Desativa (soft-delete) um usuário. Requer perfil `operador` (ou superior).

### `GET /v1/usuarios/{id}/modulos`

Lista os módulos permitidos para um usuário. Requer `operador` (ou superior).

### `PUT /v1/usuarios/{id}/modulos`

Substitui a lista de módulos permitidos de um usuário. Requer `operador` (ou superior).

---

## Códigos de Erro Padrão

| Código | Significado |
|--------|-------------|
| 400 | Dados inválidos no body |
| 401 | Token ausente ou expirado |
| 403 | Permissão insuficiente para o perfil |
| 404 | Recurso não encontrado |
| 409 | Conflito (ex: username ou e-mail duplicado) |
| 422 | Falha de validação Pydantic |
| 429 | Rate limit excedido (100 req/min por padrão) |
| 500 | Erro interno — consultar logs estruturados |

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
    "parent_id": null,
    "children": [],
    "modulos": [
      {
        "id": 1,
        "nome": "Usuários",
        "url": "/modules/users/index.html",
        "icone": "users",
        "ordem": 1,
        "role_minima": "admin",
        "slug": "usuarios"
      }
    ]
  }
]
```

### `GET /v1/portal/modules/available`

Lista os módulos disponíveis para vínculo em abas. Requer `admin`.

**Response 200:**
```json
[
  {
    "slug": "estoque",
    "nome": "Estoque",
    "url": "/modules/estoque/index.html",
    "ja_vinculado": true,
    "aba_vinculada": "Logística"
  }
]
```

### `POST /v1/portal/abas`

Cria uma nova aba no menu. Requer `admin`.

**Body:**

```json
{
  "nome": "Logística",
  "icone": "truck",
  "ordem": 2,
  "parent_id": null
}
```

**Response 201:** Objeto da aba criada.

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
  "ordem": 1,
  "role_minima": "operador",
  "slug": "estoque"
}
```

**Response 201:** Objeto do módulo criado.

### `PUT /v1/portal/modulos/{id}`

Atualiza um módulo. Requer `admin`.

### `DELETE /v1/portal/modulos/{id}`

Remove um módulo. Requer `admin`.

---

## Temas / Skins

Endpoints para gerenciar o sistema de skins visuais por empresa. O `company_id` é obtido automaticamente do token JWT do usuário logado. A maioria exige perfil `admin`; `GET /v1/themes/active` aceita qualquer usuário autenticado.

### `GET /v1/themes/active`

Retorna o tema ativo da empresa do usuário logado. Usado pelo `skinLoader` no boot do frontend.

**Response 200:** Objeto do tema ativo ou 404 se nenhum encontrado.

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
    "colors": {"--skin-primary": "#0055aa", "--skin-danger": "#ef4444"},
    "fonts": {"heading": "Barlow Condensed", "body": "DM Sans"},
    "tokens": {"--skin-radius-md": "0.5rem", "--skin-shadow-card": "0 10px 25px rgba(0,0,0,0.1)"},
    "icon_library": "fontawesome",
    "logo_url": "/uploads/logos/uuid.jpg",
    "layout_mode": "topbar",
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
  "layout_mode": "topbar",
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

### `GET /v1/themes/templates`

Lista os templates de skin pré-configurados disponíveis.

**Response 200:**
```json
[
  {"slug": "corporate-blue", "name": "Corporate Blue", "preview": {"--skin-primary": "#0055aa"}},
  {"slug": "dark-minimal", "name": "Dark Minimal", "preview": {"--skin-primary": "#6b7280"}}
]
```

### `POST /v1/themes/{id}/logo`

Upload de logo para o tema (multipart/form-data). Tipos aceitos: jpeg, png, svg, gif. Máximo 5MB.

### `POST /v1/themes/fonts-icons/upload`

Upload de um único arquivo de fonte ou ícone (multipart/form-data). Não é ZIP. Tipos aceitos: `.ttf`, `.otf`, `.woff`, `.woff2`. Máximo 5MB.

**Form fields:**
- `file` (obrigatório) — arquivo da fonte ou ícone
- `type` (`font` | `icon`, default `font`) — define o destino (`fonts/` ou `icons/`)

**Response 200:**
```json
{ "url": "/uploads/fonts/uuid.ttf", "type": "font" }
```

### `GET /v1/themes/{id}/history`

Retorna o histórico de alterações de um tema.

### `GET /v1/themes/{theme_id}/original-snapshot`

Retorna o snapshot do tema no momento da criação. Requer `admin`.

**Response 200:** Objeto do snapshot original (igual ao tema criado) ou **404** se não encontrado.

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

## Auditoria

Endpoints de auditoria de alterações no banco e de tempo de uso (sessões). Requerem perfil `admin`. Somente leitura.

**Como funciona:** toda escrita em banco (INSERT/UPDATE/DELETE) é auditada automaticamente via listener SQLAlchemy `before_flush` (`app/audit/listeners.py`) — grava `user_id`, entidade, ação e nomes dos campos alterados na mesma transação. Entidades excluídas da auto-auditoria: `audit_logs`, `sessoes` e `theme_history`. O contexto do request (usuário + IP) é propagado via `ContextVar` pelo middleware `app/middleware/audit_context.py`.

### `GET /v1/audit/logs`

Lista os logs de alterações no banco, mais recentes primeiro. Requer `admin`.

**Query params:** `page` (default 1), `page_size` (default 20, máx 100)

**Response 200:**

```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "entidade": "CompanyTheme",
      "entidade_id": 2,
      "acao": "UPDATE",
      "campos_alterados": ["name", "is_active"],
      "ip": "127.0.0.1",
      "criado_em": "2026-08-17T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

> `campos_alterados` guarda apenas os **nomes** dos campos alterados (sem valores). `acao` é `INSERT`, `UPDATE` ou `DELETE`.

### `GET /v1/audit/sessoes`

Lista os logins/logouts dos usuários (tempo de uso), mais recentes primeiro. Requer `admin`.

**Query params:** `page` (default 1), `page_size` (default 20, máx 100)

**Response 200:**

```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "login_at": "2026-08-17T09:00:00Z",
      "logout_at": "2026-08-17T10:30:00Z",
      "duracao_segundos": 5400,
      "ip": "127.0.0.1",
      "logout_motivo": "logout"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

> `logout_motivo` é `logout` (manual), `inativo` (timeout de inatividade) ou `expirado` (reservado para fechamento forçado). Sessões sem `logout_at` estão abertas. Uma sessão é aberta a cada login em `POST /v1/auth/token`.

---

## Produtos Protheus (api-sqlserver)

Endpoints read-only da `api-sqlserver` para consulta de produtos na tabela `SB1010` do Protheus. **Não validam token JWT** — a `api-sqlserver` não implementa autenticação, portanto são públicos.

Base URL: `http://localhost:8001/v1/produtos`

### `GET /v1/produtos/por-codigo?codigo=XXXX`

Busca produtos pelo código (`B1_COD`). Mínimo **4 caracteres**. Retorna todos que **iniciam** com o valor informado.

**Response 200:**
```json
[{"codigo": "ABCD01", "descricao": "Produto Teste"}]
```

**422:** `codigo` com menos de 4 caracteres.

### `GET /v1/produtos/por-descricao?descricao=XXXX`

Busca produtos pela descrição (`B1_DESC`). Mínimo **4 caracteres**. Usa `LIKE %texto%` (busca por trecho).

**Parâmetros:**
- `descricao` (obrigatório, min 4) — texto da descrição
- Sem parâmetro `modo` — sempre busca por trecho

**Response 200:**
```json
[{"codigo": "001", "descricao": "Produto Teste Um"}]
```

---

## Consultas Públicas (Proxies)

Proxies para APIs externas sem CORS, evitando bloqueios do navegador no frontend. Não exigem autenticação. Os dados são repassados de forma transparente (proxy pass-through).

### `GET /v1/cbo/{codigo}`

Consulta a descrição de um código CBO via `https://sistemas.unasus.gov.br/ws_cbo/cbo.php`.

**Response 200:** Corpo bruto retornado pela API upstream (`text/xml`).

**502:** Erro ao consultar a API de CBO.

### `GET /v1/cep/{cep}`

Consulta o endereço de um CEP via `https://opencep.com/v1/{cep}`.

**Response 200:** Corpo bruto (`application/json`) com os dados do endereço.

**502:** Erro ao consultar a API de CEP.

---

## Importação de Módulos

Endpoints para escanear e importar módulos frontend a partir de zips disponíveis no diretório de importação. Requer perfil `admin`.

### `GET /v1/import/scan`

Escaneia o diretório de importação (zips `.zip` disponíveis) e os módulos já instalados. Não recebe arquivo multipart.

**Response 200:**
```json
{
  "modules": [
    {
      "slug": "meu-modulo",
      "module_name": "meu-modulo",
      "entity_name": "MeuModulo",
      "version": "1.0.0",
      "menu_label": "Meu Módulo",
      "schema_name": "org",
      "target_api": "postgres",
      "ja_importado": false,
      "pode_remover": true
    }
  ],
  "instalados": [
    {
      "slug": "estoque",
      "module_name": "estoque",
      "entity_name": "Estoque",
      "version": "1.0.0",
      "menu_label": "Estoque",
      "schema_name": "org",
      "target_api": "postgres",
      "ja_importado": true,
      "pode_remover": true
    }
  ]
}
```

- `modules` — zips disponíveis no diretório de importação (com manifest válido)
- `instalados` — módulos já instalados (frontend/backend existentes no monorepo)

### `POST /v1/import/{module_name}`

Importa (instala) um módulo a partir do zip `{module_name}.zip` no diretório de importação.

**Path params:** `module_name` — nome do módulo (fuzzy match no arquivo `.zip`)

**Query params:** `force` (boolean, default `true`) — sobrescreve o módulo se já existir

**Response 200:**
```json
{
  "success": true,
  "message": "Importação concluída com sucesso",
  "steps": [
    "Backend copiado",
    "Frontend copiado",
    "Migração aplicada"
  ],
  "error": null
}
```

### `DELETE /v1/import/{module_name}`

Remove um módulo importado (backend, frontend e vínculo com aba).

**Path params:** `module_name` — nome do módulo a remover

**Response 200:**
```json
{
  "success": true,
  "message": "Módulo 'meu-modulo' removido com sucesso",
  "steps": [
    "Backend removido",
    "Vínculo com aba removido do banco"
  ],
  "error": null
}
```

**404:** Módulo não encontrado para remoção.
