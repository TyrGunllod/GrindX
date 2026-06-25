<!-- title: Guia de Instalação — GrindX | updated: 2026-06-22 -->

# Guia de Instalação — GrindX

---

## Pré-requisitos

| Ferramenta | Versão mínima | Uso |
|------------|--------------|-----|
| Python | 3.12 | Runtime das APIs |
| PostgreSQL | 14+ | Banco principal |
| ODBC Driver 17 for SQL Server ou FreeTDS | — | Apenas para `api-sqlserver` |
| Git | qualquer | Versionamento |
| Podman | 4+ | Containers (substituto Docker) |
| make (GnuMake) | qualquer | Automação de tasks |

### Notas para WSL

**Clone o repositório dentro do filesystem do WSL** (`~/`), não em `/mnt/c/`. Isso garante que os volumes do Podman funcionem corretamente (paths Windows não são acessíveis ao Podman).

```bash
cd ~
git clone git@github.com:TyrGunllod/GrindX.git _Projects/GrindX
cd _Projects/GrindX
```

---

## 1. Clonar o Repositório

```powershell
git clone git@github.com:TyrGunllod/GrindX.git
cd GrindX
```

---

## 2. Configurar `api-postgres`

```powershell
cd apps/api-postgres

# Criar e ativar virtualenv
python -m venv .venv
.\.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
copy .env.example .env
```

Editar `.env` com seus valores reais:

```env
DATABASE_URL=postgresql+psycopg://postgres:SUA_SENHA@localhost:5432/grindxdb
SECRET_KEY=chave-secreta-forte-com-pelo-menos-32-caracteres
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# SMTP/Email (opcional — necessário para "Esqueceu a senha?")
SMTP_HOST=127.0.0.1
SMTP_PORT=1025
SMTP_USER=
SMTP_PASS=
SMTP_USE_TLS=false
EMAIL_FROM=admin@grindx.local
EMAIL_FROM_NAME=GrindX Administrador
```

```powershell
# Rodar migrações (cria todas as tabelas do banco)
make migrate

# Popular dados iniciais
make seed
```

> **Ordem importante:** `migrate` deve rodar antes do `seed` para garantir que todas as tabelas (inclusive as sem model class, como `projetos`, `recursos`, `tarefas`, `registros_tarefas`) existam antes da inserção de dados.

---

## 3. Configurar `api-sqlserver` (opcional)

```powershell
cd apps/api-sqlserver

python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
```

Editar `.env`:

```env
DB_SERVER=XXX.XXX.XXX.XXX,XXXXX
DB_DATABASE=Database_Name
DB_USERNAME=User_Name
DB_PASSWORD=senha_real_aqui
DB_DRIVER=ODBC Driver 17 for SQL Server

# Deve ser IDÊNTICA à SECRET_KEY da api-postgres
SECRET_KEY=chave-secreta-forte-com-pelo-menos-32-caracteres
```

---

## 4. Rodar o Projeto

Abrir três terminais a partir da raiz do projeto:

```powershell
# Terminal 1 — api-postgres (porta 8002)
make dev-postgres

# Terminal 2 — api-sqlserver (porta 8001, opcional)
make dev-sqlserver

# Terminal 3 — frontend (porta 8101)
python -m http.server 8101 --directory apps/frontend-webapp
```

Acessar: `http://localhost:8101`

---

## 5. Credenciais de Teste

| Usuário | Senha | Perfil |
|---------|-------|--------|
| `admin` | `admin123` | Administrador — acesso total |

---

## 6. Rodar Testes

```powershell
# Da raiz do projeto
make test-postgres       # 190 testes — api-postgres
make test-sqlserver      # 11 testes — api-sqlserver
make test-shared         # 26 testes — RBAC shared
make test-root           # 24 testes de integração do monorepo
make test-all            # todos de uma vez (obrigatório antes de push)
```

Os testes usam SQLite in-memory — não precisam de PostgreSQL real rodando.

> **Importante:** os testes do `api-sqlserver` precisam de `PYTHONPATH` com `packages/` — o Makefile já configura automaticamente. Em Windows, use `cmd /c` para executar (PowerShell não suporta `set PYTHONPATH=...&&`).

---

## 7. Migrações de Banco (Alembic)

Os modelos foram reorganizados em **4 schemas de domínio** (`iam`, `portal`, `catalogo`, `org`) dentro de `app/modules/`. Todas as bases compartilham um único `registry()` e `MetaData()`, com schema definido via `__table_args__` herdado.

```powershell
cd apps/api-postgres

# Criar nova migração após alterar models/
alembic revision --autogenerate -m "descricao da mudanca"

# Aplicar migrações pendentes
make migrate

# Ver estado atual
alembic current

# Reverter uma migração
alembic downgrade -1
```

Para recriar o banco do zero:

```powershell
# Dropar e recriar o database
psql -U postgres -c "DROP DATABASE IF EXISTS grindx"
psql -U postgres -c "CREATE DATABASE grindx"

# Aplicar migrações + seed
make migrate
make seed
```

---

## 8. Containers (Podman)

### Desenvolvimento (hot-reload)

```bash
# Da raiz do projeto
make build   # build das imagens
make volumes # cria diretórios de volumes + copia nginx.conf
make up      # sobe todos os serviços
make down    # para os serviços
make logs    # ver logs em tempo real

# Primeira vez
docker exec grindx-api-postgres alembic upgrade head
docker exec grindx-api-postgres python seed.py
```

### Deploy para produção

```bash
# 1. Gerar imagens e exportar .tar
make images

# 2. Exportar configs para diretório de deploy
make deploy DEST=~/Apps

# 3. Copiar .tar e diretório de deploy para o servidor
# 4. No servidor:
cd ~/Apps/GrindX
make volumes
podman load -i grindx-frontend-*.tar
podman load -i grindx-api-sqlserver-*.tar
podman load -i grindx-api-postgres-*.tar
podman-compose up -d
```

### Volumes no compose.yaml

Os paths de volume usam `${PWD}` (diretório atual ao rodar o compose) para compatibilidade com WSL e Linux. Exemplo:

```yaml
volumes:
  - ${PWD}/apps/frontend-webapp/modules:/usr/share/nginx/html/modules
```

---

## 9. Criar um Novo Módulo Frontend

1. Criar pasta em `apps/frontend-webapp/modules/nome-do-modulo/`
2. Criar `index.html`, `script.js`, `style.css`
3. Usar o design system:

```html
<link rel="stylesheet" href="../../shared/core.css">
<script src="../../shared/config.js"></script>
<script src="../../shared/app.js"></script>
<script src="../../shared/apiService.js"></script>
```

> A ordem dos scripts é obrigatória: `config.js` → `app.js` → `apiService.js` → `baseController.js` → `script.js`. O `config.js` define a URL base da API e deve vir antes do `app.js`.

4. Cadastrar a URL do módulo no painel de **Módulos & Abas** dentro do portal

> As **Abas** suportam `parent_id` para aninhamento hierárquico (sub-abas). Ao cadastrar uma aba, é possível definir uma aba pai para criar sub-menus.

Ver [`ARCHITECTURE_PORTAL.md`](../apps/frontend-webapp/ARCHITECTURE_PORTAL.md) para o guia completo.

---

## 10. Criar um Novo Módulo Completo (backend + frontend)

Usar a skill do assistente:

```
.opencode/skills/create-standalone-module/SKILL.md
```

Cobre: backend FastAPI + SQLAlchemy models, frontend vanilla JS, testes, migration Alembic e auto-registro.

---

## Resolução de Problemas

### API não sobe — erro de importação do `shared`

```powershell
# Garantir que PYTHONPATH aponta para packages/
set PYTHONPATH=D:\_Projetos\GrindX\packages
```

### Erro de conexão com PostgreSQL

- Verificar se o serviço está rodando: `pg_ctl status`
- Verificar `DATABASE_URL` no `.env`

### Erro de autenticação JWT entre as APIs

- Confirmar que `SECRET_KEY` é idêntica nos dois `.env`

### Rate limit no CI

- O workflow usa variável `RATE_LIMIT_REQUESTS=100` — valores baixos podem causar flaky tests; aumentar se necessário.
