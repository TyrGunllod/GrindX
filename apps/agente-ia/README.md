# GrindX Agente IA — Assistente de Manuais

Agente de Inteligência Artificial (RAG) que responde perguntas dos colaboradores sobre **como usar os módulos do ERP GrindX**, com base nos manuais e documentos da empresa. Acessível pelo mascote flutuante no dashboard (widget) ou pela API.

---

## Descrição geral

O colaborador pergunta sobre uma tela (ex.: "o que faz o botão Salvar?"), e o agente responde com base nos manuais indexados do módulo atual — **sempre citando a fonte**. Se a informação não existir nos documentos, o agente informa que não encontrou, em vez de inventar.

Os documentos de origem podem ser **Markdown** ou **CSV** (planilhas). A ingestão é feita pelo módulo **Gestão → Configurar Agente** do GrindX.

---

## Arquitetura

```
GrindX (frontend)
  └─ Mascote (widget) ──► POST /v1/agente/chat  {question, module}

Agente de IA (apps/agente-ia — FastAPI, porta 8003)
  ├─ ingestion.py    → Markdown/CSV → chunks por seção/linha
  ├─ embeddings.py   → sentence-transformers (modelo local)
  ├─ vectorstore.py  → pgvector (PostgreSQL) — tabela agente.chunks
  ├─ retrieval.py    → busca por similaridade, restrita ao módulo atual
  └─ generation.py   → DeepSeek (deepseek-chat) — resposta + fontes
```

### Fluxo

1. **Ingestão**: o manual (`.md` ou `.csv`) é dividido em trechos, cada um vira um **embedding** e é gravado no pgvector com metadados (módulo, arquivo, seção).
2. **Pergunta**: o widget envia a pergunta + o módulo ativo da tela.
3. **Recuperação**: o agente embute a pergunta e busca **apenas nos manuais do módulo atual** (reduz consultas e evita misturar conteúdo de outros módulos).
4. **Geração**: o DeepSeek responde com base no contexto recuperado, **sem citar no texto** — as fontes aparecem separadas abaixo da resposta.

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| API | Python 3.12 + FastAPI + Uvicorn |
| Embeddings | sentence-transformers (`intfloat/multilingual-e5-small`) |
| Banco vetorial | PostgreSQL + pgvector (coluna `vector(384)`, índice por cosseno) |
| Geração | DeepSeek (`deepseek-chat`) |
| ORM | SQLAlchemy 2 + psycopg3 |
| Frontend | Widget vanilla JS (mascote) no dashboard do GrindX |
| Logs | JSONL (`logs/agente.log`) |

---

## Executar localmente

Pré-requisitos: Python 3.12+, PostgreSQL com extensão **pgvector**.

```bash
# 1. Instalar dependências
cd apps/agente-ia
python -m venv .venv
.\.venv\Scripts\activate          # Linux: source .venv/bin/activate
pip install -r requirements.txt

# 2. Configurar ambiente
copy .env.example .env            # preencher DATABASE_URL e LLM_API_KEY

# 3. Subir
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

Ou pelo Makefile (da raiz do GrindX):

```bash
make venv-agente      # cria o .venv e instala deps
make dev-agente       # uvicorn na porta 8003
```

Na subida, o agente cria o schema `agente`, a extensão `vector` e a tabela `chunks` automaticamente (`init_db`).

**Endpoints:**

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Health check (inclui conexão com o banco) |
| POST | `/v1/agente/chat` | Pergunta + módulo → resposta com fontes |
| POST | `/v1/agente/manuais` | Ingere um documento (`.md`/`.csv`) para um módulo |
| GET | `/v1/agente/manuais` | Lista manuais indexados |
| DELETE | `/v1/agente/manuais?module=&filename=` | Remove um manual |
| GET | `/v1/agente/modulos` | Lista módulos com manuais indexados |

Swagger: `http://localhost:8003/v1/docs`.

---

## Exemplos de perguntas que o agente responde

**No módulo Usuários:**

- "O que faz o botão Salvar no cadastro de usuário?"
- "Como desativo um usuário?"
- "Como preencho o endereço no cadastro?"
- "Como libero o acesso de um usuário a um módulo?"
- "O que significa o perfil Leitura?"

**No módulo Meu Perfil:**

- "Como troco minha senha?"
- "Onde vejo meus dados cadastrais?"

**No módulo Importar Módulos:**

- "Como importo um módulo novo?"
- "Como removo um módulo instalado?"

---

## Exemplos de respostas geradas

**Pergunta:** *O que faz o botão Salvar no cadastro de usuário?*
**Resposta:**
> O botão Salvar grava o novo usuário, fecha a janela e atualiza a tabela. Se algum campo obrigatório estiver errado (usuário com menos de 3 caracteres, e-mail sem "@" ou senha com menos de 6 caracteres), aparece um aviso explicando o que corrigir e a janela não fecha.

**Pergunta:** *Como desativo um usuário?*
**Resposta:**
> Na coluna Status, clique no selo **Ativo**. A mensagem "Usuário desativado com sucesso" aparece e o selo muda para **Inativo** — a pessoa deixa de acessar o sistema (ninguém é apagado, apenas desligado do acesso).

**Pergunta:** *Como preencho o endereço no cadastro?*
**Resposta:**
> O endereço é preenchido automaticamente pela busca de CEP. Digite o CEP no campo e clique no botão de lupa (ou pressione Enter) — os campos Endereço, Bairro, Cidade e UF são preenchidos sozinhos.

---

## Deploy

- **OCI (Always Free):** ver [docs/DEPLOYMENT-OCI.md](../../docs/DEPLOYMENT-OCI.md).
- **Alternativo (Render + Supabase/Neon + OCI Object Storage):** ver [docs/DEPLOYMENT-ALT.md](../../docs/DEPLOYMENT-ALT.md) e [docs/DEPLOYMENT-SUPABASE.md](../../docs/DEPLOYMENT-SUPABASE.md).

---

## Testes

```bash
python -m pytest tests/ -v
```

Cobrem: chunking de Markdown, conversão de CSV, recuperação restrita ao módulo, geração com retry (429) e normalização da URL do banco.

