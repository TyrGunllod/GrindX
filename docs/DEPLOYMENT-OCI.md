<!-- title: Deploy OCI — Agente de IA GrindX | updated: 2026-08-23 -->

# Deploy OCI — Agente de IA GrindX

Guia para publicar o **Agente de IA** (RAG) na Oracle Cloud Infrastructure (Always Free), junto com o **PostgreSQL + pgvector**.

---

## Arquitetura

```
OCI Always Free
└── VM Compute (Ampere A1, ARM64)
    └── Docker Compose (compose.oci.yaml)
        ├── agente-ia   (FastAPI, porta 8003)  ← imagem OCIR
        └── postgres    (pgvector/pgvector:pg18, porta 5432)
```

Recursos OCI usados (sempre grátis):

| Serviço | Recurso |
|---|---|
| Compute | 1 VM `VM.Standard.A1.Flex` (4 OCPU / 24GB RAM) |
| Container Registry (OCIR) | imagem do agente |
| Object Storage | 10GB (manuais/logs, opcional) |
| Vault | secrets (`DEEPSEEK_API_KEY`, senha Postgres) |
| VCN | subnet pública + security list |

---

## 1. Imagem do sistema operacional

- **Recomendada:** **Ubuntu 22.04 LTS (aarch64 / ARM64)** do OCI Marketplace (Canonical).
- A VM Ampere A1 é **ARM**, então escolha a imagem **aarch64**.
- Alternativa: **Oracle Linux 8** (imagem nativa OCI).

---

## 2. Provisionar a VM

1. OCI Console → **Compute → Instances → Create instance**.
2. **Image:** Marketplace → Ubuntu 22.04 LTS (aarch64).
3. **Shape:** `VM.Standard.A1.Flex` — configure 4 OCPUs e 24GB de RAM (dentro do Always Free).
4. **VCN:** criar nova VCN com subnet pública.
5. Gerar/fornecer **SSH key** para acesso.
6. Criar a instância e anotar o **IP público**.

---

## 3. Instalar Docker no VM

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# reinicie a sessão (logout/login) para usar docker sem sudo
```

---

## 4. Build + push da imagem no OCIR

Na sua máquina (ou no CI):

```bash
# Login no OCIR (região iad como exemplo)
docker login iad.ocir.io -u '<tenancy>/<user>' -p '<auth-token>'

# Build (pré-baixa o modelo de embeddings no build)
docker build -t iad.ocir.io/<tenancy>/grindx/agente-ia:latest apps/agente-ia

# Push
docker push iad.ocir.io/<tenancy>/grindx/agente-ia:latest
```

> O Dockerfile já baixa o modelo `paraphrase-multilingual-MiniLM-L12-v2` no build, evitando download (~470MB) em runtime.

---

## 5. Configurar o deploy no VM

```bash
sudo mkdir -p /opt/grindx && sudo chown $USER:$USER /opt/grindx
cd /opt/grindx

# Copiar o compose e o env de exemplo
cp <caminho-para>/compose.oci.yaml .
cp <caminho-para>/.env.oci.example .env

# Editar o .env (preencher DEEPSEEK_API_KEY, senhas, CORS)
nano .env
```

**`.env`** (resumo):

```
DATABASE_URL=postgresql+psycopg://postgres:<senha>@postgres:5432/grindx
LLM_API_KEY=<chave-deepseek>
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
SIMILARITY_THRESHOLD=0.35
TOP_K=3
CORS_ORIGINS=https://<dominio-do-grindx>
POSTGRES_PASSWORD=<senha>
```

---

## 6. Subir

```bash
cd /opt/grindx
docker compose -f compose.oci.yaml up -d
docker compose -f compose.oci.yaml logs -f
```

Na primeira subida, o agente cria o schema `agente`, a extensão `vector` e a tabela `chunks` automaticamente (`init_db`).

---

## 7. Rede / Security List (VCN)

Na VCN → **Security List da subnet pública**, adicionar ingress rules:

| Porta | Origem | Uso |
|---|---|---|
| 22 | seu IP | SSH |
| 8003 | IP/domínio do frontend GrindX | API do agente |
| 5432 | **restrita** | Postgres (opcional expor) |
| 80/443 | 0.0.0.0/0 | frontend GrindX (se hospedado no mesmo VM) |

---

## 8. Ajuste no frontend GrindX

Em produção, injete a URL do agente no `config.js` do frontend:

```js
window.__GRINDX_AGENT_URL = 'https://<ip-ou-dominio>:8003';
```

E garanta que o `CORS_ORIGINS` do agente inclui o domínio do frontend.

---

## 9. Manutenção

```bash
# Atualizar imagem + restart
docker pull iad.ocir.io/<tenancy>/grindx/agente-ia:latest
docker compose -f compose.oci.yaml up -d

# Logs (JSONL do agente em logs/agente.log)
docker exec agente-ia tail -f logs/agente.log

# Backup do Postgres
docker exec postgres18 pg_dump -U postgres grindx > backup_$(date +%F).sql
```

---

## Checklist

- [ ] VM Ampere A1 criada (Ubuntu 22.04 LTS aarch64)
- [ ] Docker + Docker Compose instalados
- [ ] Imagem `agente-ia` no OCIR
- [ ] `.env` preenchido no VM (secrets reais)
- [ ] Security List liberando 8003/80/443
- [ ] `docker compose -f compose.oci.yaml up -d` saudável
- [ ] `GET /health` respondendo `{"status":"healthy","database":{"postgres":"connected"}}`
- [ ] `window.__GRINDX_AGENT_URL` apontando para o agente na nuvem
