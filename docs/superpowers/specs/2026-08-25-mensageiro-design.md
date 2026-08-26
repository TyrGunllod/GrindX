# Design — Módulo Central de Mensagens e Notificações Internas (Mensageiro)

**Data:** 2026-08-25
**Fonte:** `docs/new_features/mensageiro.md`
**Status:** Aprovado no brainstorm

---

## 1. Objetivo

Criar um módulo central de mensagens e notificações internas assíncronas no ERP GrindX,
permitindo que usuários e o próprio sistema enviem mensagens uns aos outros — incluindo
**threads (mensagens + respostas) e anexos** — com contador de não lidas exibido no mascote
(widget de IA) e listagem completa em um módulo dedicado.

Sem WebSockets nem tempo real: **polling** (10 min + disparos pontuais) com **bridge `postMessage`**
entre módulos (iframes) e a janela pai. Sem agendamento/background: envio é sempre **on-demand**
(admin via `POST`, ou qualquer módulo do backend chamando o service `criar_mensagem`).

---

## 2. Contexto do código real (diferenças do doc original)

- Shell real: `apps/frontend-webapp/dashboard.html` usa `#moduleViewport`; módulos carregam em iframes
  (`dashboard.js` `navigateToModule(url)`).
- Mascote = FAB do widget de IA (`widget/widget.js`, `grindx_chibi.png`), que abre painel de chat.
- Convenção de rotas: `/v1/...` (o doc dizia `/api/...`).
- Backend: pacotes transversais top-level (ex.: `app/audit/`); tabelas em schema `org` via
  `OrgBase` (`app/modules/org/base.py`); FKs para `iam.usuarios.id`.
- Uploads já existentes: `uploads/` servido por `StaticFiles` em `/uploads` (`main.py:128`) com
  padrão de `unique_filename` + `os.makedirs` (ver `app/routers/theme_router.py:466-478`).
- Migration atual mais recente: `022`. Nova será `023_add_mensagens.py`.

---

## 3. Backend

### 3.1 Tabelas (migration `023_add_mensagens.py`)

#### `org.mensagens`

| Coluna            | Tipo                          | Regras                                                             |
|-------------------|-------------------------------|--------------------------------------------------------------------|
| `id`              | BIGSERIAL                     | PK                                                                 |
| `resposta_a_id`   | BIGINT NULL                   | FK autorreferente `org.mensagens.id` ON DELETE **CASCADE** (thread)|
| `remetente_id`    | BIGINT NULL                   | FK `iam.usuarios.id` ON DELETE **SET NULL**; NULL = sistema        |
| `destinatario_id` | BIGINT NOT NULL               | FK `iam.usuarios.id` ON DELETE **CASCADE**                         |
| `titulo`          | VARCHAR(150) NOT NULL         |                                                                    |
| `texto`           | TEXT NOT NULL                 |                                                                    |
| `categoria`       | VARCHAR(20) NOT NULL DEFAULT `'DIRETA'` | CHECK em `SISTEMA`, `DIRETA`, `AVISO`                   |
| `url_acao`        | VARCHAR(255) NULL             | caminho interno opcional                                           |
| `lida_em`         | TIMESTAMPTZ NULL              |                                                                    |
| `arquivada_em`    | TIMESTAMPTZ NULL              | só na mensagem raiz (arquivar = arquivar a thread)                 |
| `criado_em`       | TIMESTAMPTZ NOT NULL DEFAULT now() |                                                               |

Regras de thread:
- **Raiz** = `resposta_a_id IS NULL`. **Resposta** = aponta para a raiz (apenas um nível: responde-se à raiz).
- Excluir a raiz (CASCADE) remove todas as respostas.
- Arquivamento é por **thread** (coluna na raiz); respostas nunca arquivam sozinhas.

Índices:
- `ix_mensagens_destinatario_id` — `(destinatario_id, criado_em DESC)` — caixa de entrada + ordenação.
- `ix_mensagens_nao_lidas` — parcial `(destinatario_id, criado_em DESC) WHERE lida_em IS NULL` — contador do badge.
- `ix_mensagens_resposta_a` — `(resposta_a_id)` — busca de respostas da thread.

#### `org.anexos_mensagem`

| Coluna                 | Tipo                          | Regras                                        |
|------------------------|-------------------------------|-----------------------------------------------|
| `id`                   | BIGSERIAL                     | PK                                            |
| `mensagem_id`          | BIGINT NOT NULL               | FK `org.mensagens.id` ON DELETE **CASCADE**   |
| `nome_arquivo_original`| VARCHAR(255) NOT NULL         |                                               |
| `caminho`              | VARCHAR(255) NOT NULL         | relativo: `mensagens/{uuid}{ext}`             |
| `content_type`         | VARCHAR(100) NOT NULL         |                                               |
| `tamanho_bytes`        | INTEGER NOT NULL              |                                               |
| `criado_em`            | TIMESTAMPTZ NOT NULL DEFAULT now() |                                          |

Índice: `ix_anexos_mensagem_mensagem_id` — `(mensagem_id)`.

Modelo SQLAlchemy em `app/mensagens/models.py` usando `OrgBase`, com `Index` e `CheckConstraint`
no banco **e** enum `CategoriaMensagem` validado nos schemas Pydantic (dupla validação).

### 3.2 Estrutura do pacote `app/mensagens/`

- `models.py` — classes `Mensagem(OrgBase)` e `AnexoMensagem(OrgBase)` em schema `org`.
- `schemas.py` — `MensagemCreate`, `MensagemResponse`, `AnexoResponse`, enum `CategoriaMensagem`,
  enum `StatusMensagem` (`todas`, `nao_lidas`, `lidas`, `arquivadas`), enum `OrdemMensagem`
  (`crescente`, `decrescente`).
  - `MensagemResponse` inclui: `remetente_nome` (NULL quando sistema), `quantidade_respostas`,
    `ultima_resposta_em`, `anexos_count`. `AnexoResponse` inclui `id`, `nome_arquivo_original`,
    `content_type`, `tamanho_bytes`, `criado_em`.
- `service.py` — `listar_mensagens`, `listar_thread`, `contar_nao_lidas`, `criar_mensagem`,
  `criar_resposta`, `marcar_lida`, `marcar_thread_lida`, `arquivar`, `listar_anexos`,
  `salvar_anexo`, `obter_caminho_anexo`.
- `router.py` — `APIRouter(prefix="/v1/mensagens", tags=["Mensagens"])`, registrado no `main.py`.

### 3.3 Endpoints

**`GET /v1/mensagens`** — **mensagens raiz** do destinatário logado (respostas não aparecem na lista;
entram na thread). Paginado (`PaginatedResponse`).
- Query: `status` (`todas` padrão / `nao_lidas` / `lidas` / `arquivadas`), `ordem`
  (`decrescente` padrão / `crescente`), `page`, `page_size`.
- Ordenação por **última atividade**: `COALESCE(ultima_resposta_em, criado_em)`.
- Semântica de filtro (sempre exclui raízes arquivadas, exceto no filtro `arquivadas`):
  - `nao_lidas` → raiz com atividade não lida: `lida_em IS NULL` **ou** existe resposta com `lida_em IS NULL`.
  - `lidas` → raiz sem atividade não lida: `lida_em IS NOT NULL` e nenhuma resposta não lida.
  - `arquivadas` → `arquivada_em IS NOT NULL`.
  - `todas` → raízes não arquivadas.

**`GET /v1/mensagens/{id}/thread`** — raiz + todas as respostas (crescente por `criado_em`),
com `AnexoResponse[]` por mensagem. Acesso: participantes da raiz.

**`GET /v1/mensagens/nao-lidas/count`** → `{ "count": N }`.
- N = mensagens (raiz **ou** resposta) com `destinatario_id = usuário`, `lida_em IS NULL`
  e raiz não arquivada. Equivale a: `COUNT WHERE destinatario_id=:uid AND lida_em IS NULL AND
  COALESCE(m.arquivada_em, raiz.arquivada_em) IS NULL` (para respostas, `m.arquivada_em` é NULL
  e o estado vem da raiz via join por `resposta_a_id`).

**`POST /v1/mensagens`** — cria mensagem **raiz**. Autenticado.
- Regras de categoria/remetente (remetente **nunca** vem do cliente; sempre derivado no servidor):
  - `DIRETA` → qualquer usuário autenticado; `remetente_id` = usuário logado.
  - `SISTEMA` / `AVISO` → exige `admin`; `remetente_id` = NULL.
- Validações: `destinatario_id` deve existir (mensagem amigável via `ErrorCode` do
  `packages/shared/exceptions/codes.py`); `titulo` ≤ 150; `texto` obrigatório; `url_acao`
  opcional ≤ 255. Sem `resposta_a_id` neste endpoint.

**`POST /v1/mensagens/{id}/respostas`** — cria **resposta** na thread.
- Acesso: participantes da raiz (remetente ou destinatário). Terceiros → 403.
- Servidor deriva: `resposta_a_id` = raiz; `destinatario_id` = **o outro participante** da raiz;
  `categoria` = `DIRETA` (fixa, ignorada se enviada); `remetente_id` = usuário logado.
- `titulo` opcional (herda da raiz se omitido); `texto` obrigatório; `url_acao` opcional.

**`PATCH /v1/mensagens/{id}/lida`** — só o destinatário da mensagem (403 caso contrário);
seta `lida_em = now()`. Aceita mensagem raiz ou resposta.

**`PATCH /v1/mensagens/{id}/thread/lida`** — só participantes da raiz; marca **todas** as mensagens
da thread (raiz + respostas, destinadas ao usuário) como lidas. Chamado ao abrir a thread.

**`PATCH /v1/mensagens/{id}/arquivar`** — só o destinatário da **raiz**; body opcional
`{"arquivar": true|false}` (default `true`); seta/limpa `arquivada_em` na raiz (arquiva a thread toda).

**Anexos** (apenas mensagens da própria thread):
- `POST /v1/mensagens/{id}/anexos` — multipart, autenticado, só o **remetente** da mensagem pode anexar.
  Limite de **10 MB** e allowlist de `content_type` (ex.: `application/pdf`, `image/*`, `text/*`,
  `application/msword`, `application/vnd.openxmlformats-officedocument.*`, `application/zip`).
  Salva em `uploads/mensagens/{uuid}{ext}` (padrão `unique_filename` do `theme_router`) e insere em
  `org.anexos_mensagem`. Retorna `AnexoResponse`.
- `GET /v1/mensagens/{id}/anexos` — lista anexos da mensagem; participantes da thread.
- `GET /v1/mensagens/{id}/anexos/{anexo_id}/download` — `FileResponse` com
  `Content-Disposition: attachment` (nome original); participantes da thread. **Arquivos não ficam
  públicos** (não servidos pelo StaticFiles `/uploads`).

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
- **Lista** (raízes) — toolbar com:
  - Dropdown **status**: Todas / Não lidas / Lidas / Arquivadas.
  - Dropdown **ordenação**: Data crescente / decrescente.
  - Botão **"Nova Mensagem"**.
  - Cards: badge da categoria, remetente (ou "Sistema"), título, preview do texto, data,
    **contador de respostas**, estado lida/arquivada.
- **Thread** (ao clicar na mensagem):
  1. Abre a thread → `PATCH /v1/mensagens/{id}/thread/lida` (marca tudo como lido) e
     `grindx.notifyMensagens()`.
  2. Exibe raiz + respostas em ordem cronológica; se a raiz tiver `url_acao`, mostra botão
     **"Ir para a ação"** → `grindx.navegarPara(url_acao)` (o shell valida caminho interno).
  3. Caixa de **responder** (texto + anexos opcionais) → `POST /v1/mensagens/{id}/respostas`;
     após enviar → `notifyMensagens()`.
  4. Anexos: lista com ícone por tipo; clique faz download via `GET .../download` autenticado
     (fetch → blob → save).
- **Arquivar/Restaurar** a thread → `PATCH /v1/mensagens/{id}/arquivar`.
- **Nova Mensagem** (modal):
  - Select de destinatário: `GET /v1/usuarios` (`PaginatedResponse[UsuarioResponse]`).
  - Campos: título, texto, `url_acao` opcional, **anexos** (múltiplos).
  - Categoria: admin escolhe `SISTEMA`/`DIRETA`/`AVISO`; usuário comum vê `DIRETA` fixa.
  - Após envio (mensagem + uploads de anexos) → `grindx.notifyMensagens()`.

---

## 6. Segurança / Permissões

- Qualquer usuário autenticado: `GET` próprias mensagens/thread, `count`, `PATCH` de lida/arquivar
  (somente nas próprias — 403 para terceiros).
- Threads e anexos restritos aos **participantes** (remetente/destinatário da raiz).
- Anexos: upload só do **remetente** da mensagem; download autenticado e restrito a participantes
  (nunca servido publicamente).
- `POST` `DIRETA`: qualquer autenticado. `POST` `SISTEMA`/`AVISO`: admin.
- `remetente_id`/`destinatario_id` de respostas sempre derivados no servidor (nunca do cliente).
- `url_acao` validada no shell como caminho interno (bloqueia `javascript:`, URLs externas etc.).
- Limite de upload 10 MB + allowlist de `content_type`.
- Sem endpoints de escrita em `api-sqlserver` (mantido somente leitura).

---

## 7. Testes

- Backend (`apps/api-postgres/tests/`, pytest):
  - Regras de envio: DIRETA por usuário comum (remetente = logado); SISTEMA/AVISO por admin
    (remetente NULL); usuário comum sem permissão para SISTEMA/AVISO.
  - Threads: resposta só de participante; derivada `destinatario_id` = outro participante;
    categoria fixa DIRETA; exclusão CASCADE.
  - Só o destinatário marca lida/arquiva; `thread/lida` marca raiz + respostas; terceiros → erro.
  - Filtros `status` (com semântica de atividade não lida) e ordenação por última atividade.
  - Contador de não lidas (exclui arquivadas; inclui respostas não lidas).
  - Anexos: upload só do remetente, allowlist/limite, download autenticado só de participantes.
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
- Conversas multi-participantes / grupos (thread atual é 1:1 raiz + respostas).
- WebSockets / tempo real.
- Envio agendado/background (criação é sempre on-demand: via POST, por admin ou módulo do backend).
