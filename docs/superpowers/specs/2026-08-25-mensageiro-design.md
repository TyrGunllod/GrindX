# Design — Módulo Central de Mensagens e Notificações Internas (Mensageiro)

**Data:** 2026-08-25
**Fonte:** `docs/new_features/mensageiro.md`
**Status:** Aprovado no brainstorm

---

## 1. Objetivo

Criar um módulo central de mensagens e notificações internas assíncronas no ERP GrindX,
permitindo que usuários e o próprio sistema enviem mensagens uns aos outros, com contador
de não lidas exibido no mascote (widget de IA) e listagem completa em um módulo dedicado.

Sem WebSockets nem tempo real: **polling** (10 min + disparos pontuais) com **bridge `postMessage`**
entre módulos (iframes) e a janela pai.

---

## 2. Contexto do código real (diferenças do doc original)

- Shell real: `apps/frontend-webapp/dashboard.html` usa `#moduleViewport`; módulos carregam em iframes
  (`dashboard.js` `navigateToModule(url)`).
- Mascote = FAB do widget de IA (`widget/widget.js`, `grindx_chibi.png`), que abre painel de chat.
- Convenção de rotas: `/v1/...` (o doc dizia `/api/...`).
- Backend: pacotes transversais top-level (ex.: `app/audit/`); tabelas em schema `org` via
  `OrgBase` (`app/modules/org/base.py`); FKs para `iam.usuarios.id`.
- Migration atual mais recente: `022`. Nova será `023_add_mensagens.py`.

---

## 3. Backend

### 3.1 Tabela `org.mensagens` (migration `023_add_mensagens.py`)

| Coluna           | Tipo                          | Regras                                                            |
|------------------|-------------------------------|-------------------------------------------------------------------|
| `id`             | BIGSERIAL                     | PK                                                                |
| `remetente_id`   | BIGINT NULL                   | FK `iam.usuarios.id` ON DELETE **SET NULL**; NULL = sistema       |
| `destinatario_id`| BIGINT NOT NULL               | FK `iam.usuarios.id` ON DELETE **CASCADE**                        |
| `titulo`         | VARCHAR(150) NOT NULL         |                                                                   |
| `texto`          | TEXT NOT NULL                 |                                                                   |
| `categoria`      | VARCHAR(20) NOT NULL DEFAULT `'DIRETA'` | CHECK em `SISTEMA`, `DIRETA`, `AVISO`                    |
| `url_acao`       | VARCHAR(255) NULL             | caminho interno opcional                                          |
| `lida_em`        | TIMESTAMPTZ NULL              |                                                                   |
| `arquivada_em`   | TIMESTAMPTZ NULL              | extensão aprovada no brainstorm                                    |
| `criado_em`      | TIMESTAMPTZ NOT NULL DEFAULT now() |                                                               |

Índices:
- `ix_mensagens_destinatario_id` — `(destinatario_id, criado_em DESC)` — consultas por caixa de entrada + ordenação.
- `ix_mensagens_nao_lidas` — parcial `(destinatario_id, criado_em DESC) WHERE lida_em IS NULL` — contador do badge.

Modelo SQLAlchemy em `app/mensagens/models.py` usando `OrgBase`, com `Index` e `CheckConstraint`
no banco **e** enum `CategoriaMensagem` validado nos schemas Pydantic (dupla validação).

### 3.2 Estrutura do pacote `app/mensagens/`

- `models.py` — classe `Mensagem(OrgBase)` com schema `org`.
- `schemas.py` — `MensagemCreate`, `MensagemResponse`, enum `CategoriaMensagem`, enum `StatusMensagem`
  (`todas`, `nao_lidas`, `lidas`, `arquivadas`), enum `OrdemMensagem` (`crescente`, `decrescente`).
  `MensagemResponse` inclui `remetente_nome` (NULL quando `remetente_id` NULL), resolvido no service
  via join com `Usuario` (mesmo padrão do `app/audit/router.py`).
- `service.py` — `listar_mensagens`, `contar_nao_lidas`, `criar_mensagem`, `marcar_lida`, `arquivar`.
- `router.py` — `APIRouter(prefix="/v1/mensagens", tags=["Mensagens"])`, registrado no `main.py`.

### 3.3 Endpoints

**`GET /v1/mensagens`** — mensagens do destinatário logado. Paginado (`PaginatedResponse`).
- Query: `status` (`todas` padrão / `nao_lidas` / `lidas` / `arquivadas`), `ordem`
  (`decrescente` padrão / `crescente`), `page`, `page_size`.
- Semântica de filtro:
  - `nao_lidas` → `lida_em IS NULL AND arquivada_em IS NULL`
  - `lidas` → `lida_em IS NOT NULL AND arquivada_em IS NULL`
  - `arquivadas` → `arquivada_em IS NOT NULL`
  - `todas` → sem filtro de estado.

**`GET /v1/mensagens/nao-lidas/count`** → `{ "count": N }`, onde N = `lida_em IS NULL AND arquivada_em IS NULL`.

**`POST /v1/mensagens`** — cria mensagem. Autenticado.
- Regras de categoria/remetente (remetente **nunca** vem do cliente; sempre derivado no servidor):
  - `DIRETA` → qualquer usuário autenticado; `remetente_id` = usuário logado.
  - `SISTEMA` / `AVISO` → exige `admin`; `remetente_id` = NULL.
- Validações: `destinatario_id` deve existir (mensagem amigável via `ErrorCode` do
  `packages/shared/exceptions/codes.py`); `titulo` ≤ 150; `texto` obrigatório; `url_acao`
  opcional ≤ 255.

**`PATCH /v1/mensagens/{id}/lida`** — só o destinatário (403 caso contrário); seta `lida_em = now()`.

**`PATCH /v1/mensagens/{id}/arquivar`** — só o destinatário; body opcional `{"arquivar": true|false}`
(default `true`); seta/limpa `arquivada_em`.

---

## 4. Frontend — Shell (janela pai)

### 4.1 Mascote / widget (`widget/widget.js` + `widget.css`)

- FAB (`grindx-ai-fab`) **continua abrindo o chat de IA**.
- **Badge** de contagem sobre o FAB quando `count > 0`; oculto quando 0. Estilos com tokens
  `var(--...)` (nunca cores fixas).
- **Balão de fala** persistente quando `count > 0`: *"Você tem N novos recados!"*.
  - Conflito de UX resolvido: o **balão é o elemento clicável** que navega o iframe para
    `modules/mensagens/index.html`; o clique no FAB não muda de comportamento.
  - Ao clicar no balão, ele some (não reaparece a cada poll até nova mensagem chegar).
- `refreshMensagens()`: busca `GET /v1/mensagens/nao-lidas/count` via `apiService` e atualiza
  badge + balão. Disparado: no load do dashboard, a cada **10 min**, ao receber `postMessage`
  `grindx:mensagens-atualizar`, e após navegação de módulo.

### 4.2 Dropdown do perfil (`dashboard.js`)

- Item **"Mensagens"** (`nav-dropdown-item`) abaixo de "Meu Perfil" nos dois dropdowns
  (sidebar e topbar), com badge de contagem ao lado.
- Clique → `navigateToModule('modules/mensagens/index.html')`.

### 4.3 Bridge de comunicação (`shared/notificationBridge.js`)

Incluído no `dashboard.html` (após `apiService.js`). Expõe no `window.grindx`:
- `notifyMensagens()` → `window.parent.postMessage({ type: 'grindx:mensagens-atualizar' }, '*')`.
- `navegarPara(url)` → `window.parent.postMessage({ type: 'grindx:navegar', url }, '*')`.

`dashboard.js` escuta `window.addEventListener('message', ...)`:
- `grindx:mensagens-atualizar` → `refreshMensagens()`.
- `grindx:navegar` → valida que `url` é caminho interno (relativo, sem `://`, `javascript:`,
  `data:` etc.) e chama `navigateToModule(url)`.

Módulos que quiserem avisar o pai incluem `shared/notificationBridge.js` e chamam as funções.

---

## 5. Frontend — Módulo `modules/mensagens/`

- `index.html` na ordem padrão de scripts: `config.js` → `app.js` → `apiService.js` →
  `baseController.js` → `script.js`, mais `shared/notificationBridge.js`.
- Badge de versão via `BaseController.setBadgeVersao()` (módulo padrão exibe versão do sistema).
- Registro no `seed.py` (`modulos_seed`) — ex.:
  `{ "aba": "Principal", "nome": "Mensagens", "slug": "mensagens",
     "url": "modules/mensagens/index.html", "icone": "fas fa-envelope" }`.
- Toolbar:
  - Dropdown **status**: Todas / Não lidas / Lidas / Arquivadas.
  - Dropdown **ordenação**: Data crescente / decrescente.
  - Botão **"Nova Mensagem"**.
- Lista em cards: badge da categoria (`SISTEMA`/`DIRETA`/`AVISO` coloridos via tokens),
  remetente (nome completo via join com usuário; "Sistema" quando `remetente_id` NULL),
  título, preview do texto, data formatada, estado lida/arquivada.
- Clique na mensagem:
  1. Se não lida → `PATCH /v1/mensagens/{id}/lida`.
  2. Se `url_acao` → `grindx.navegarPara(url_acao)` (o shell valida caminho interno e navega o iframe).
  3. Se não há `url_acao` → apenas abre/exibe a mensagem completa; permanece no módulo.
  4. Após o PATCH → `grindx.notifyMensagens()` (pai atualiza badge/balão).
- Botão **Arquivar/Restaurar** por mensagem → `PATCH /v1/mensagens/{id}/arquivar`.
- Modal **"Nova Mensagem"**:
  - Select de destinatário: `GET /v1/usuarios` (`PaginatedResponse[UsuarioResponse]`).
  - Campos: título, texto, `url_acao` opcional.
  - Categoria: admin escolhe `SISTEMA`/`DIRETA`/`AVISO`; usuário comum vê `DIRETA` fixa.
  - Após envio → `grindx.notifyMensagens()`.

---

## 6. Segurança / Permissões

- Qualquer usuário autenticado: `GET` próprias mensagens, `count`, `PATCH` de lida/arquivar
  (somente nas próprias mensagens — 403 para mensagens de terceiros).
- `POST` `DIRETA`: qualquer autenticado. `POST` `SISTEMA`/`AVISO`: admin.
- `remetente_id` sempre derivado no servidor (nunca aceito do cliente).
- `url_acao` validada no shell como caminho interno (bloqueia `javascript:`, URLs externas etc.).
- Sem endpoints de escrita em `api-sqlserver` (mantido somente leitura).

---

## 7. Testes

- Backend (`apps/api-postgres/tests/`, pytest):
  - Regras de envio: DIRETA por usuário comum (remetente = logado); SISTEMA/AVISO por admin
    (remetente NULL); usuário comum sem permissão para SISTEMA/AVISO.
  - Só o destinatário marca lida/arquiva; terceiros → erro.
  - Filtros `status` (todas/não lidas/lidas/arquivadas) e ordenação crescente/decrescente.
  - Contador de não lidas (exclui arquivadas).
  - Validação de categoria e `destinatario_id` inexistente.
- Frontend (`apps/frontend-webapp/tests/`, `node:test`):
  - Bridge: `notifyMensagens`/`navegarPara` emitem `postMessage` correto.
  - Dashboard: listener processa `grindx:mensagens-atualizar` e `grindx:navegar` (validação de
    caminho interno).
  - Badge: count 0 oculto, count > 0 visível.

---

## 8. Docs Sync (obrigatório no AGENTS.md)

Atualizar `README.md`, `docs/API.md`, `docs/DATABASE.md`, e registrar o módulo no `seed.py`.

---

## 9. Fora de escopo (YAGNI)

- Exclusão física de mensagens (arquivar cobre a redução de poluição).
- Anexos, threads, respostas.
- WebSockets / tempo real.
- Envio agendado/background de mensagens do sistema (criação é via POST, por admin ou módulo).
