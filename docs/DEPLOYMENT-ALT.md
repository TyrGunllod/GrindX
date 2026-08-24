<!-- title: Deploy Alternativo — Agente de IA GrindX | updated: 2026-08-23 -->

# Deploy Alternativo — Agente de IA GrindX

> **Passo a passo completo do Render:** veja [DEPLOYMENT-RENDER.md](DEPLOYMENT-RENDER.md).

Guia usado quando a **OCI free não permite criar a instância** (erro de *available domain* / falta de capacidade da VM Ampere A1). Mantém o requisito do desafio de **pelo menos 1 serviço OCI** usando o **OCI Object Storage** (sempre gratuito, regional e **sem problema de AD**).

---

## Arquitetura

```
Render (Web Service free)          ── Agente FastAPI (porta 8003)
Neon / Supabase / Render DB        ── PostgreSQL + pgvector
OCI Object Storage (bucket)        ── manuais/backup  ← requisito OCI
```

| O que | Onde | Custo |
|---|---|---|
| Agente FastAPI | Render (Web Service) | free |
| PostgreSQL + pgvector | Neon ou Supabase (free) — ou Render DB | free |
| Manuais/backup | OCI Object Storage | free (10GB) |

> O agente aceita `DATABASE_URL` no formato `postgresql://...` (Neon/Supabase/Render) — ele converte automaticamente para `postgresql+psycopg://`.

---

## Opção A — Render com Postgres gerenciado (Blueprint)

1. Suba o `render.yaml` (raiz do repo) no Render (Dashboard → **New → Blueprint**), ou use o CLI do Render.
2. O Render cria os **Web Services** `agente-ia` (porta 8003) e `api-postgres` (porta 8002). O banco é o **Supabase** (não há Postgres gerenciado no blueprint).
3. No dashboard de cada serviço, preencha os env vars `sync: false`:
   - `agente-ia`: `DATABASE_URL` (Supabase), `LLM_API_KEY` (DeepSeek), `CORS_ORIGINS`.
   - `api-postgres`: `DATABASE_URL` (Supabase, com `+psycopg`), `SECRET_KEY`, `CORS_ORIGINS`.
4. **Migrações/seed do ERP** já foram aplicados no Supabase (`make migrate` + `make seed`) — o `api-postgres` só conecta.
5. Deploy automático. O agente cria o schema `agente`/tabela na subida (`init_db`).

> Se preferir o Postgres gerenciado do Render, adicione o bloco `databases:` ao blueprint — mas o free expira após ~30 dias; **Supabase é a opção permanente** (ver [DEPLOYMENT-SUPABASE.md](DEPLOYMENT-SUPABASE.md)).

---

## Opção B — Neon ou Supabase (Postgres gratuito permanente)

1. Crie um projeto no **Neon** (ou **Supabase**).
2. Copie a `DATABASE_URL` (formato `postgresql://...`).
3. Habilite o pgvector (Neon/Supabase já o suportam; no Supabase rode `CREATE EXTENSION IF NOT EXISTS vector;` no SQL editor).
4. No Render, crie um Web Service a partir do `Dockerfile` do agente (`apps/agente-ia/Dockerfile`) e defina:

   ```
   DATABASE_URL=<url-do-neon/supabase>
   LLM_API_KEY=<chave-deepseek>
   LLM_BASE_URL=https://api.deepseek.com
   LLM_MODEL=deepseek-chat
   EMBEDDING_MODEL=intfloat/multilingual-e5-small
   SIMILARITY_THRESHOLD=0.35
   TOP_K=3
   CORS_ORIGINS=<domínio-do-frontend>
   ```

> **Usando Supabase?** Veja o passo a passo completo em [DEPLOYMENT-SUPABASE.md](DEPLOYMENT-SUPABASE.md) (connection string, `sslmode=require`, pooler e criação automática do schema).

> No `render.yaml`, se usar Neon/Supabase, troque o `DATABASE_URL` de `fromDatabase` para `sync: false` (preencher manualmente) e remova o bloco `databases:`.

---

## Passo OCI (obrigatório do desafio)

1. OCI Console → **Storage → Object Storage → Buckets → Create Bucket**.
   - Object Storage é **regional** e **sempre gratuito** — não passa pelo problema de AD da Compute.
2. Crie um bucket (ex.: `grindx-agente`).
3. Faça upload dos manuais (`apps/agente-ia/manuals/*.md`) como backup.
4. Isso cumpre o requisito **"ao menos 1 serviço OCI"** do desafio.

---

## Ajuste no frontend GrindX

Aponte o widget para a URL do Render:

```js
window.__GRINDX_AGENT_URL = 'https://agente-ia.onrender.com';
```

E garanta que o `CORS_ORIGINS` do agente inclui o domínio do frontend.

---

## Checklist

- [ ] Web Service do agente no Render (healthy `/health`)
- [ ] Postgres + pgvector criado e acessível
- [ ] `DATABASE_URL`, `LLM_API_KEY`, `CORS_ORIGINS` configurados
- [ ] Bucket criado no OCI Object Storage + manuais enviados (requisito OCI)
- [ ] `window.__GRINDX_AGENT_URL` apontando para o agente na nuvem
- [ ] Testar: `POST /v1/agente/chat` respondendo

