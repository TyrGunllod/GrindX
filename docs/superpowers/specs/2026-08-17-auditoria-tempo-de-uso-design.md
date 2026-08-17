# Design: Auditoria de Alterações e Tempo de Uso (GrindX)

**Data da Especificação:** 2026-08-17
**Versão:** 1.0
**Responsável:** GrindX Team

---

## 1. Objetivo

Implementar um sistema de auditoria de movimentação do usuário no GrindX que:

- Registre **somente alterações** (toda escrita em banco) com **data/hora e usuário** que executou
- **Não** registre consultas/leituras
- Registre **entrada e saída** do usuário no sistema (login/logout) para cálculo de **tempo de uso**
- Exiba os dados em um módulo frontend no portal (somente admin)

---

## 2. Requisitos Funcionais

### 2.1 Auditoria de Alterações

- **Cobertura:** toda escrita em banco na api-postgres via SQLAlchemy:
  - INSERT, UPDATE, DELETE em qualquer entidade persistida pelo ORM
  - Usuários, perfil, senha, temas/skins, portal/abas/módulos, import, etc.
- **Consultas (GET/reads) não geram log.**
- **Resumo da alteração:** lista com os **nomes dos campos alterados** (ex: `["email", "role"]`), **sem valores antes/depois** e **sem omitir nenhum campo** (inclui nomes de campos sensíveis).
- Cada registro contém: usuário, entidade, id do registro, ação (`insert|update|delete`), campos alterados, IP, data/hora.

### 2.2 Tempo de Uso

- **Tabela de sessões** dedicada para cálculo de tempo de uso.
- **Login** (`POST /v1/auth/token`): cria registro de sessão (aberta).
- **Logout** (`POST /v1/auth/logout`, novo): fecha a sessão ativa com `logout_at`, `duracao_segundos` e motivo.
- **Logout manual** e **logout por inatividade** no frontend devem chamar `POST /v1/auth/logout` antes de limpar a sessão local.
- Motivos de fechamento: `logout` (manual), `inativo` (timeout de inatividade), `expirado` (reserva para fechamento forçado).

### 2.3 Visualização

- Módulo frontend novo **"Auditoria"** no portal com duas abas:
  - **Alterações:** tabela de logs (data/hora, usuário, entidade, ação, campos alterados) com filtros
  - **Tempo de uso:** tabela de sessões (login, logout, duração, motivo) com filtros
- Acesso restrito a `admin`.

### 2.4 Retenção

- Logs acumulam **sem retenção automática** (limpeza manual futura, fora do escopo).

---

## 3. Arquitetura Técnica

### 3.1 Tabelas (schema `org`, migração Alembic nova)

**`org.audit_logs`**

| coluna | tipo | descrição |
|---|---|---|
| `id` | int PK | autoincrement |
| `user_id` | int FK `iam.usuarios.id` nullable | usuário que executou (null se sem auth) |
| `entidade` | varchar(100) not null | nome da classe da entidade |
| `entidade_id` | int nullable | id do registro alterado |
| `acao` | varchar(20) not null | `insert` / `update` / `delete` |
| `campos_alterados` | JSON not null | lista de nomes de campos alterados |
| `ip` | varchar(45) nullable | IP de origem |
| `criado_em` | timestamptz not null | default `now()` |

Índices: `(entidade, entidade_id)`, `(user_id)`, `(criado_em)`.

**`org.sessoes`**

| coluna | tipo | descrição |
|---|---|---|
| `id` | int PK | autoincrement |
| `user_id` | int FK `iam.usuarios.id` not null | usuário |
| `login_at` | timestamptz not null | entrada (default `now()`) |
| `logout_at` | timestamptz nullable | saída |
| `duracao_segundos` | int nullable | preenchido no logout |
| `ip` | varchar(45) nullable | IP de origem |
| `logout_motivo` | varchar(20) nullable | `logout` / `inativo` / `expirado` |

Índices: `(user_id)`, `(login_at)`.

> Observação: FKs para `iam.usuarios` seguem o padrão das demais tabelas (recomendável `ondelete="CASCADE"` ou sem FK rígida, conforme decisão de implementação; usuários não são excluídos fisicamente hoje).

### 3.2 Componentes Backend (novo pacote `apps/api-postgres/app/audit/`)

| arquivo | responsabilidade |
|---|---|
| `models.py` | Modelos `AuditLog` e `Sessao` (herdam `OrgBase`) |
| `context.py` | `ContextVar` para `user_id` e `ip` da requisição atual |
| `service.py` | `AuditService`: `registrar_audit`, `abrir_sessao`, `fechar_sessao`, `listar_logs`, `listar_sessoes` |
| `listeners.py` | Evento SQLAlchemy `after_flush` → auditoria automática de escritas |
| `dependencies.py` | `set_audit_context`: lê o JWT (se houver), popula as `ContextVar`; dependência global |

**Fluxo da auditoria automática (`listeners.py`):**
1. Registrar dois handlers: `before_flush` e `after_flush` na `SessionLocal`.
2. **`before_flush`** — captura o diff (histórico de atributos ainda íntegro antes do SQL):
   - Para cada objeto nas coleções `inserted` / `dirty` / `deleted` da sessão:
     - Filtrar classes auditáveis (exclui `AuditLog`, `Sessao` e `ThemeHistory` — esta já tem histórico próprio, evita duplicação).
     - Obter `user_id`/`ip` das `ContextVar`.
     - Montar `campos_alterados`:
       - `insert`/`delete`: todos os atributos de coluna do registro
       - `update`: campos com `attr.history.has_changes()` (nomes apenas)
     - Acumular entradas pendentes numa lista.
3. **`after_flush`** — persiste os registros de auditoria:
   - Adiciona os `AuditLog` acumulados à própria sessão (são gravados no commit subsequente, **na mesma transação** da operação).
4. A auditoria é feita **no mesmo commit** da operação (não abre sessão separada).

> Observação: usar `after_flush` isolado para ler `attr.history` é inseguro (o flush já zera o histórico de alguns atributos); o `before_flush` é o ponto correto para captura.

**Contexto de requisição (`dependencies.py`):**
- `set_audit_context` roda para toda requisição — implementado como `BaseHTTPMiddleware` (padrão dos demais middlewares em `app/middleware/`), registrado no `main.py`.
- Extrai o token do header `Authorization` (se presente) e decodifica de forma **opcional** (sem lançar erro quando não há token — necessário pois login/refresh não têm token ainda). Reutiliza `verificar_jwt` (via `shared.security.jwt`) para obter `user_id`.
- Seta `ContextVar` de `user_id` e `ip` (`request.client.host`); limpa/restaura no `finally`.

### 3.3 Eventos de Sessão (auth)

No `apps/api-postgres/app/auth/router.py`:
- `POST /v1/auth/token` (login): após `auth_service.autenticar` com sucesso, chama `AuditService.abrir_sessao(user_id, ip)`.
- `POST /v1/auth/logout` (**novo**): autenticado (`get_current_user`), chama `AuditService.fechar_sessao(user_id, motivo="logout")` e retorna `{"message": "Logout realizado com sucesso."}`. Fecha a sessão mais recente aberta do usuário.
- `POST /v1/auth/refresh`: renova token, **não** toca na sessão (sem abrir/fechar).

### 3.4 Endpoints Novos (`app/routers/audit_router.py`)

Prefix `/v1/audit`, role mínima `admin` (via `require_role_or_higher(Role.ADMIN)`).

- `GET /v1/audit/logs`
  - Query params: `user_id`, `entidade`, `acao`, `data_inicio`, `data_fim`, `page` (default 1), `page_size` (default 20)
  - Resposta: lista de logs + total (padrão de paginação dos demais routers)
- `GET /v1/audit/sessoes`
  - Query params: `user_id`, `data_inicio`, `data_fim`, `page`, `page_size`
  - Resposta: lista de sessões (com `duracao_segundos`) + total

### 3.5 Registro no main.py

- Incluir `audit_router` (`app.include_router(audit_router)`).
- Registrar a dependência global `set_audit_context`.
- Garantir import dos novos models em `app/models/__init__.py` e `alembic/env.py` (padrão de registro para migrações).

---

## 4. Frontend

### 4.1 Estrutura do módulo

`apps/frontend-webapp/modules/auditoria/`:
- `index.html` — estrutura com duas abas (Alterações / Tempo de uso) + filtros + tabelas
- `script.js` — controle das abas, chamadas via `apiService`, renderização (DataTable existente)
- `style.css` — estilos locais (somente `var(--...)` do design system)
- `module.json` — manifest: `module_name`, `schema_name: "org"`, `route_prefix: "/v1/audit"`, `frontend_tabs` (Alterações / Tempo de uso), `role_minima: "admin"`

Scripts na ordem padrão: `config.js` → `app.js` → `inactivity.js` → `apiService.js` → `baseController.js` → `script.js`.

### 4.2 Funcionalidades

- **Aba Alterações:** tabela com data/hora, usuário, entidade, ação, campos alterados; filtros por usuário/entidade/ação/período; paginação.
- **Aba Tempo de uso:** tabela com login, logout, duração (formatada hh:mm:ss), motivo; filtros por usuário/período; paginação.
- **Logout server-side:**
  - Botão de logout do dashboard e o `LogoutHandler` de inatividade devem chamar `POST /v1/auth/logout` (fire-and-forget, com tolerância a falha — não bloqueia o logout local) antes de `session.clear()` + redirect.
  - Para o motivo `inativo`, o frontend pode enviar o motivo no body (ex: `{"motivo": "inativo"}`) ou usar um parâmetro de query; decisão de implementação.

### 4.3 Registro do módulo

- Adicionar entrada no `seed.py` (`modulos_seed`): aba "Gestão", nome "Auditoria", slug `auditoria`, url `modules/auditoria/index.html`, ícone (ex: `fas fa-history`), `role_minima: "admin"`.
- (ou, se preferível, registrar via `portal_modulos` na migração — decisão de implementação.)

---

## 5. Considerações de Segurança

- **Somente admin** acessa os endpoints de auditoria (`require_role_or_higher`).
- Campos sensíveis: os **nomes** dos campos alterados são registrados sem mascaramento (decisão do usuário); **nenhum valor** (antes/depois) é armazenado.
- A auditoria usa a mesma sessão da transação: se o commit falhar, nada é persistido (não há log de operação que não ocorreu).
- O `set_audit_context` deve nunca lançar por falta de token (login público).
- Tabelas de auditoria são read-only para o cliente (nenhum endpoint de escrita exposto).

---

## 6. Testes

- **Unit:**
  - Modelos `AuditLog` / `Sessao` (criação, constraints, defaults).
  - `AuditService`: `abrir_sessao`, `fechar_sessao` (calcula duração), `registrar_audit`, listagens com filtros.
  - Listener `after_flush`: insert/update/delete capturados com `campos_alterados` corretos; exclusão das tabelas de auditoria; user_id vindo da ContextVar.
- **Integração:**
  - `POST /v1/auth/token` cria sessão.
  - `POST /v1/auth/logout` fecha sessão com duração e motivo.
  - Escrita em entidade (ex: usuário, tema) gera `audit_logs` com campos corretos.
  - `GET /v1/audit/logs` e `GET /v1/audit/sessoes` com filtros e RBAC (403 para não-admin, 401 sem token).
  - Migração Alembic aplica/rollback (padrão dos testes de índices).
- **Frontend (JS, Node test runner):**
  - Logout manual chama `POST /v1/auth/logout`.
  - Timeout de inatividade chama `POST /v1/auth/logout` com motivo `inativo`.
  - Renderização das duas abas.

---

## 7. Documentação (Docs Sync)

Atualizar ao concluir:
- `README.md` — novo módulo Auditoria e recursos de auditoria/tempo de uso.
- `docs/API.md` — novos endpoints (`/v1/auth/logout`, `/v1/audit/*`).
- `docs/DATABASE.md` — novas tabelas `org.audit_logs` e `org.sessoes`.
- `docs/SETUP.md` — se necessário (migração nova).
- `docs/README.md` e `AGENTS.md` — menção ao módulo Auditoria.

---

## 8. Dependências

- `shared/app.js` (SessionManager) — chamada de logout.
- `shared/inactivity.js` — dispara logout com motivo `inativo`.
- `shared/apiService.js` / `baseController.js` — consumo dos endpoints.
- `apps/api-postgres/app/auth/` — injeção dos eventos de sessão.
- `apps/api-postgres/app/middleware/` — padrão de dependências globais (referência).
- `OrgBase` (`app/modules/org/base.py`) — base dos novos models.

---

**Próximo Passo:** Aprovar este design antes de prosseguir com o plano de implementação (writing-plans).
