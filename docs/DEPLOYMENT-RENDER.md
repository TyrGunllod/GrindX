<!-- title: Deploy Render — GrindX APIs | updated: 2026-08-24 -->

# Deploy no Render — Agente de IA + API Postgres

Passo a passo para publicar as APIs do GrindX no **Render**, usando o **Supabase** como banco de dados.

---

## Pré-requisitos

- Repositório no GitHub com o `render.yaml` (já está na raiz do GrindX).
- Projeto **Supabase** configurado (ver [DEPLOYMENT-SUPABASE.md](DEPLOYMENT-SUPABASE.md)) com:
  - `DATABASE_URL` do agente: `postgresql://postgres.<REF>:<SENHA>@aws-0-<REGIAO>.pooler.supabase.com:5432/postgres?sslmode=require`
  - `DATABASE_URL` da api-postgres: `postgresql+psycopg://postgres.<REF>:<SENHA>@aws-0-<REGIAO>.pooler.supabase.com:5432/postgres?sslmode=require`
- Chave da **DeepSeek** (`LLM_API_KEY`).
- Uma **`SECRET_KEY`** forte para a api-postgres (32+ caracteres, entropia alta).
- Migrações + seed do ERP **já aplicados no Supabase** (feito em `make migrate` + `make seed`).

---

## Passo 1 — Subir o código no GitHub

```bash
git push origin main
```

---

## Passo 2 — Criar o Blueprint no Render

1. Acesse [render.com](https://render.com) e entre.
2. Clique em **New** → **Blueprint**.
3. Conecte o repositório **GrindX** (ou cole a URL do `render.yaml`).
4. O Render lê o `render.yaml` e mostra os serviços que vai criar:
   - **`agente-ia`** (Web Service, porta 8003).
   - **`api-postgres`** (Web Service, porta 8002).
5. Clique em **Apply**.

> O `render.yaml` **não** cria banco — o banco é o **Supabase**. Você preenche as `DATABASE_URL` manualmente no passo 4.

---

## Passo 3 — Escolher o plano

- Ambos os serviços podem usar o plano **Free** (dormem após 15 min de inatividade; acordam no próximo request).
- Para o desafio (demo), o Free é suficiente.

---

## Passo 4 — Preencher as variáveis de ambiente

No dashboard de **cada** serviço (abas *Environment*), preencha as variáveis marcadas como `sync: false` no blueprint:

### Serviço `agente-ia`

| Variável | Valor |
|---|---|
| `DATABASE_URL` | `postgresql://postgres.<REF>:<SENHA>@aws-0-<REGIAO>.pooler.supabase.com:5432/postgres?sslmode=require` |
| `LLM_API_KEY` | sua chave DeepSeek |
| `CORS_ORIGINS` | domínio do frontend GrindX (ex.: `https://frontend.onrender.com`) |

> `LLM_BASE_URL`, `LLM_MODEL`, `EMBEDDING_MODEL`, `SIMILARITY_THRESHOLD`, `TOP_K` já vêm com valores padrão do blueprint.

### Serviço `api-postgres`

| Variável | Valor |
|---|---|
| `DATABASE_URL` | `postgresql+psycopg://postgres.<REF>:<SENHA>@aws-0-<REGIAO>.pooler.supabase.com:5432/postgres?sslmode=require` |
| `SECRET_KEY` | chave forte (32+ chars) — gere com: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `CORS_ORIGINS` | domínio do frontend GrindX |

> `APP_NAME`, `APP_VERSION`, `DEBUG`, `ENVIRONMENT`, `RATE_LIMIT_*` já vêm com valores de produção do blueprint.

---

## Passo 5 — Aplicar o deploy

1. Clique em **Apply** (ou **Save Changes**).
2. O Render faz o build da imagem (o `Dockerfile` do agente pré-baixa o modelo de embeddings) e inicia os serviços.
3. Acompanhe os logs (abas *Logs*) de cada serviço.

---

## Passo 6 — Validar

Após o deploy, teste:

```
https://<agente-ia>.onrender.com/health
```
→ Esperado: `{"status":"healthy","service":"GrindX Agente IA",...,"database":{"postgres":"connected"}}`

```
https://<api-postgres>.onrender.com/health
```
→ Esperado: `{"status":"healthy",...,"database":{"postgres":"connected"}}`

Testar uma pergunta ao agente (Swagger público):

```
https://<agente-ia>.onrender.com/v1/docs
```
→ `POST /v1/agente/chat` com `{"question":"o que faz o botão Salvar?","module":"users"}`.

---

## Passo 7 — Frontend (opcional)

O frontend do GrindX pode ser um **Static Site** no Render (ou qualquer host estático):

1. Render → **New → Static Site** → apontar para `apps/frontend-webapp/` (ou build do Dockerfile nginx).
2. Injetar as URLs via `window.__GRINDX_API_URL` e `window.__GRINDX_AGENT_URL` (no `config.js` ou meta).
3. O `CORS_ORIGINS` de cada API deve incluir o domínio do frontend.

---

## Passo 8 — Evidência do deploy (desafio)

1. Tire um **print** (ou vídeo) do agente respondendo no Swagger público (`/v1/docs`).
2. No OCI, tire um print do **bucket Object Storage** com os manuais.
3. Preencha a seção **"Deploy na nuvem — Evidência"** no `README.md` (URL + imagem/vídeo).

---

## Solução de problemas

| Problema | Causa / solução |
|---|---|
| Build falha no `agente-ia` | Modelo de embeddings não baixa no build (rede/limite) — verificar logs; o modelo também baixa em runtime na 1ª pergunta |
| `/health` `degraded` na api-postgres | `DATABASE_URL` errada ou `SECRET_KEY` sem entropia — verificar env vars |
| `401` ao autenticar | `SECRET_KEY` diferente entre serviços — usar a mesma chave |
| `429` nas respostas do agente | Rate limit do DeepSeek — aguardar e tentar de novo (o agente tem retry) |
| Serviço Free dormindo | 1º request demora a acordar (até ~50s) — normal no plano free |
