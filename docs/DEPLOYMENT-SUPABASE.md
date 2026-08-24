<!-- title: Supabase — Banco do Agente de IA | updated: 2026-08-23 -->

# Supabase — Banco de Dados do Agente de IA

Guia para usar o **Supabase** (PostgreSQL gratuito + pgvector) como banco do Agente de IA do GrindX.

---

## Por que Supabase

- PostgreSQL gerenciado **grátis** (500MB) — sem data de expiração.
- **pgvector já vem habilitado** por padrão.
- Conexão externa fácil (via pooler).

---

## 1. Criar o projeto

1. Acesse [supabase.com](https://supabase.com) e entre.
2. **New project**:
   - Nome do projeto (ex.: `grindx-agente`).
   - **Database password**: crie uma senha forte e **guarde** (usada na connection string).
   - **Region**: escolha a mais próxima (ex.: `South America (São Paulo)`).
   - Clique em **Create project** e aguarde (1–2 min).

---

## 2. Obter a connection string

1. Dashboard → **Project Settings** (engrenagem) → **Database** → **Connection string**.
2. Escolha a aba **Session pooler** (recomendado para APIs com pool de conexões).
   - Alternativa: **Direct connection** (`db.<ref>.supabase.co`).
   - Evite a **Transaction pooler** (porta 6543) — feita para serverless e pode conflitar com o pool do SQLAlchemy.
3. Copie a URL. Formato:

```
postgresql://postgres.<REF>:<SENHA>@aws-0-<REGIAO>.pooler.supabase.com:5432/postgres
```

> `<REF>` é o código do projeto (ex.: `abcdefghijklmnopqrst`). A senha é a que você definiu no passo 1.

---

## 3. Adicionar `sslmode=require`

O Supabase **exige SSL**. Acrescente `?sslmode=require` ao final da URL:

```
postgresql://postgres.<REF>:<SENHA>@aws-0-<REGIAO>.pooler.supabase.com:5432/postgres?sslmode=require
```

> Se a URL já tiver `?` (query params), use `&sslmode=require`.

---

## 4. Verificar o pgvector

O Supabase já traz o **pgvector** habilitado. Para confirmar, no **SQL Editor** do dashboard rode:

```sql
SELECT name, default_version FROM pg_available_extensions WHERE name = 'vector';
```

Esperado: `vector` disponível. O agente executa `CREATE EXTENSION IF NOT EXISTS vector` sozinho na subida (não precisa criar manualmente).

---

## 5. Configurar o agente

No ambiente do agente (`apps/agente-ia/.env` ou as env vars do Render/Neon):

```
DATABASE_URL=postgresql://postgres.<REF>:<SENHA>@aws-0-<REGIAO>.pooler.supabase.com:5432/postgres?sslmode=require
LLM_API_KEY=<chave-deepseek>
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
EMBEDDING_MODEL=intfloat/multilingual-e5-small
SIMILARITY_THRESHOLD=0.35
TOP_K=3
CORS_ORIGINS=<domínio-do-frontend>
```

> O agente aceita a URL no formato `postgresql://` (com ou sem `+psycopg`) — ele converte automaticamente para o dialeto `postgresql+psycopg://` e respeita o `sslmode`.

---

## 6. Na subida, o agente cria o schema/tabela

O `init_db` do agente executa automaticamente:

1. `CREATE EXTENSION IF NOT EXISTS vector;`
2. `CREATE SCHEMA IF NOT EXISTS "agente";`
3. Cria a tabela `agente.chunks` (com coluna `embedding vector(384)`).

Você **não** precisa criar nada manualmente no Supabase. Apenas garanta que o usuário da connection string tem permissão (o usuário `postgres` do Supabase tem).

---

## 7. Testar a conexão

Com o venv do agente instalado, valide a conexão e a criação do schema:

```powershell
cd apps/agente-ia
# rodar o init_db + listar o que foi criado
.\.venv\Scripts\python -c "from app.rag import vectorstore; vectorstore.init_db(); print('schema agente ok')"
```

No **SQL Editor** do Supabase, confira:

```sql
SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'agente';
```

Esperado: a tabela `chunks` existe.

---

## 8. Testar o fluxo completo

Com o agente rodando (`make dev-agente` ou Render), faça:

```powershell
# Importar um manual
Invoke-RestMethod -Uri "http://localhost:8003/v1/agente/manuais" -Method Post -ContentType "application/json" `
  -Body (@{ module="users"; filename="users.md"; content=(Get-Content -Raw "apps/agente-ia/manuals/users.md") } | ConvertTo-Json)

# Perguntar
Invoke-RestMethod -Uri "http://localhost:8003/v1/agente/chat" -Method Post -ContentType "application/json" `
  -Body (@{ question="o que faz o botão Salvar?"; module="users" } | ConvertTo-Json)
```

---

## Checklist

- [ ] Projeto Supabase criado e senha salva
- [ ] Connection string obtida (Session pooler)
- [ ] `?sslmode=require` adicionado
- [ ] pgvector disponível (já vem habilitado)
- [ ] `DATABASE_URL` configurada no agente
- [ ] `init_db` criou `agente.chunks` (verificado no SQL Editor)
- [ ] `/health` responde `{"database":{"postgres":"connected"}}`

