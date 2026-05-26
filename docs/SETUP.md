<!-- title: Guia de Instalação — GrindX | updated: 2026-05-25 -->

# Guia de Instalação — GrindX

---

## Pré-requisitos

| Ferramenta | Versão mínima | Uso |
|------------|--------------|-----|
| Python | 3.12 | Runtime das APIs |
| PostgreSQL | 14+ | Banco principal |
| ODBC Driver 17 for SQL Server | — | Apenas para `api-sqlserver` |
| Git | qualquer | Versionamento |
| make (GnuMake) | qualquer | Automação de tasks |

---

## 1. Clonar o Repositório

```powershell
git clone git@github.com:TyrGunllod/GrindX.git
cd GrindX
```

---

## 2. Configurar `api-postgres`

```powershell
cd packages/api-postgres

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
# Criar banco e rodar migrações
python manage_db.py upgrade head

# Popular dados iniciais (usuários admin/operador)
python seed.py

# Aplicar migração mais recente (sub-abas)
alembic upgrade head
```

---

## 3. Configurar `api-sqlserver` (opcional)

```powershell
cd packages/api-sqlserver

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

# Terminal 3 — frontend (porta 5500)
python -m http.server 5500 --directory packages/frontend-webapp
```

Acessar: `http://localhost:5500`

---

## 5. Credenciais de Teste

| Usuário | Senha | Perfil |
|---------|-------|--------|
| `admin` | `admin123` | Administrador — acesso total |
| `operador` | `operador123` | Operador — leitura e criação |

---

## 6. Rodar Testes

```powershell
# Da raiz do projeto
pytest                   # testes da raiz (21 testes)

# Por pacote
make test-postgres       # 110 testes — api-postgres
make test-sqlserver      # testes api-sqlserver
make test-shared         # 26 testes RBAC

# Todos de uma vez
make test-all
```

Os testes usam SQLite in-memory — não precisam de PostgreSQL real rodando.

---

## 7. Migrações de Banco (Alembic)

Os modelos foram reorganizados em **4 schemas de domínio** (`iam`, `portal`, `catalogo`, `org`) dentro de `app/modules/`. As migrações existentes (001–005) criaram as tabelas no schema `public`. A estrutura de modelos está em `app/modules/{schema}/models/`, com shims de compatibilidade em `app/models/`.

Para recriar o banco do zero com os schemas:

```powershell
dropdb grindx
createdb grindx
python seed.py
```

```powershell
cd packages/api-postgres

# Criar nova migração após alterar models/
alembic revision --autogenerate -m "descricao da mudanca"

# Aplicar migrações pendentes
python manage_db.py upgrade head

# Ver estado atual
alembic current

# Reverter uma migração
alembic downgrade -1
```

---

## 8. Containers (Podman/Docker)

```powershell
# Da raiz do projeto
make build   # build das imagens
make up      # subir todos os serviços
make down    # parar os serviços
make logs    # ver logs em tempo real
```

---

## 9. Criar um Novo Módulo Frontend

1. Criar pasta em `packages/frontend-webapp/modules/nome-do-modulo/`
2. Criar `index.html`, `script.js`, `style.css`
3. Usar o design system:

```html
<link rel="stylesheet" href="../../shared/core.css">
<script src="../../shared/app.js"></script>
<script src="../../shared/apiService.js"></script>
```

4. Cadastrar a URL do módulo no painel de **Gestão de Estrutura** dentro do portal

> As **Abas** agora suportam `parent_id` para aninhamento hierárquico (sub-abas). Ao cadastrar uma aba, é possível definir uma aba pai para criar sub-menus.

Ver [`ARCHITECTURE_PORTAL.md`](../packages/frontend-webapp/ARCHITECTURE_PORTAL.md) para o guia completo.

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
