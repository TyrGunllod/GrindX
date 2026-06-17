<!-- title: GrindX — Sistema de Gestão Integrado | updated: 2026-06-10 -->

# GrindX — Sistema de Gestão Integrado (Monorepo)

O **GrindX** é um ERP modular construído com arquitetura de monorepo, focado em escalabilidade, segurança e experiência do usuário premium.

---

## Status do Projeto

Projeto em desenvolvimento ativo. Funcionalidades principais implementadas e funcionais (autenticação JWT + RBAC, CRUD de usuários, portal modular com shell, skin system com dual layout, importação de módulos). CI/CD, testes automatizados (178) e documentação acompanham o desenvolvimento.

---

## Arquitetura

O projeto utiliza micro-serviços no backend e um Portal Orquestrador (Shell) no frontend.

### Backend

- **`api-postgres` (porta 8002):** API principal em FastAPI. Gerencia autenticação JWT, RBAC, usuários, temas/skins, estrutura do portal e importação de módulos.
- **`api-sqlserver` (porta 8001):** API somente leitura para integração com bases SQL Server legadas. Valida tokens JWT emitidos pela `api-postgres`.
- **`shared`:** Pacote Python compartilhado entre as APIs — segurança, schemas e exceções.

### Frontend

- **Portal Modular (porta 8101):** Shell que gerencia navegação e carrega módulos via iframe isolado.
- **Módulos:** `home`, `users`, `structure`, `admin-skins`, `importer`, `profile` — cada um é standalone e testável independentemente.
- **Design System:** Glassmorphism + tokens CSS + `UIFactory` para consistência absoluta.

---

## Como Rodar

### Pré-requisitos

- Python 3.12+
- PostgreSQL rodando localmente
- ODBC Driver 17 for SQL Server (apenas para `api-sqlserver`)

### Setup Inicial

```powershell
# 1. Clonar
git clone <url> && cd GrindX

# 2. Criar virtualenv e instalar dependências — api-postgres
cd apps/api-postgres
python -m venv .venv && .\.venv\Scripts\activate
pip install -r requirements.txt

# 3. Configurar banco
copy .env.example .env   # editar DATABASE_URL e SECRET_KEY

# 4. Rodar migrações e popular dados iniciais
make migrate   # alembic upgrade head (cria todas as tabelas)
make seed      # popula admin, empresa, skin, abas, módulos
```

```powershell
# 5. Rodar APIs (terminais separados)
make dev-postgres    # porta 8002
make dev-sqlserver   # porta 8001

# 6. Rodar frontend
python -m http.server 8101 --directory apps/frontend-webapp
```

Acesse em `http://localhost:8101`.

### Credenciais de Teste

| Usuário | Senha | Perfil |
|---------|-------|--------|
| `admin` | `admin123` | Administrador |

---

## Testes

Suite com 178 testes cobrindo unitários, integração e validação do monorepo.

| Pacote | Testes | Cobertura |
|--------|--------|-----------|
| `api-postgres` | 178 | Auth, RBAC, temas, usuários, portal, segurança, cache, importação |
| `api-sqlserver` | 8+ | Cliente SQL Server |
| `shared` | 26 | Permissões RBAC |
| `tests/` (raiz) | 21 | Validação de pacotes |

```powershell
make test-postgres    # somente api-postgres
make test-sqlserver   # somente api-sqlserver
make test-shared      # somente shared
make test-root        # testes da raiz
make test-all         # todos os pacotes
```

---

## CI/CD

Workflow único em `.github/workflows/release.yml`:

- **`test-api-postgres`** — 178 testes com SQLite in-memory, cobertura mínima 70%
- **`test-api-sqlserver`** — testes de integração com SQL Server
- **`test-root`** — testes do monorepo (depende dos dois anteriores)
- **`lint`** — `ruff check` + `ruff format --check` em `packages/` e `apps/`
- **`release`** — `python-semantic-release` com publicação no GitHub (apenas push para `main`)

---

## Documentação

Portal de entrada: [`docs/README.md`](docs/README.md)

| Documento | Conteúdo |
|-----------|----------|
| [`docs/API.md`](docs/API.md) | Referência completa dos endpoints REST |
| [`docs/SETUP.md`](docs/SETUP.md) | Guia detalhado de instalação |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Instruções de deploy com containers |
| [`docs/DATABASE.md`](docs/DATABASE.md) | Schema, modelos e migrações |
| [`docs/SECURITY.md`](docs/SECURITY.md) | Autenticação JWT e RBAC |
| [`docs/SKILLS.md`](docs/SKILLS.md) | Skills do assistente |
| [`docs/MAPA-ARQUIVOS.md`](docs/MAPA-ARQUIVOS.md) | Inventário completo de arquivos |

---

## Design System

- **Glassmorphism** com tokens CSS centralizados em `shared/core.css`
- **`UIFactory`** (`shared/app.js`) para criação programática de componentes
- **Componentes:** `FormField`, `DataTable`, `ReusableModal`, `LoadingSpinner`
- **Skin system:** tema visual customizável por empresa, aplicado via `skinLoader.js`
- **Dual layout:** `topbar` (padrão) e `sidebar` — configurável por tema
- **Dark/Light mode** com persistência via `localStorage` + banco de dados (preferência do usuário)
- **Fluxo de forgot-password** com envio de email e troca de senha
- **Utilitários:** `apiService.js` (chamadas centralizadas com auto-auth), `validation.js` (validação de formulários e URLs)
- **WCAG** — acessibilidade como primeira camada

---

## Estrutura de Pastas

```
GrindX/
├── .github/workflows/
│   └── release.yml            # CI/CD completo (testes + lint + semantic release)
├── docs/                      # Documentação técnica
│   ├── README.md              # Portal de entrada
│   ├── API.md
│   ├── SETUP.md
│   ├── DEPLOYMENT.md
│   ├── DATABASE.md
│   ├── SECURITY.md
│   ├── SKILLS.md
│   └── MAPA-ARQUIVOS.md
├── apps/
│   ├── api-postgres/          # API principal (FastAPI + PostgreSQL)
│   │   ├── app/
│   │   │   ├── auth/          # JWT — router, service, dependencies
│   │   │   ├── core/          # config, exceptions, logging, versioning, cache
│   │   │   ├── middleware/    # rate limit, request id, security headers
│   │   │   ├── modules/       # Modelos por schema (iam, portal, catalogo, org)
│   │   │   ├── models/        # Re-export shims (compatibilidade)
│   │   │   ├── repositories/
│   │   │   ├── routers/       # auth, health, portal, theme, usuario, import
│   │   │   ├── schemas/
│   │   │   └── services/      # email, produto, usuario, theme
│   │   ├── alembic/           # 10 migrações do banco
│   │   ├── tests/             # 178 testes
│   │   └── ...
│   ├── api-sqlserver/         # API somente leitura (SQL Server)
│   │   ├── app/
│   │   │   ├── auth/          # Validação JWT (sem emissão)
│   │   │   ├── core/
│   │   │   ├── middleware/
│   │   │   ├── routers/       # cliente, health
│   │   │   └── services/
│   │   ├── tests/
│   │   └── ...
│   └── frontend-webapp/       # Portal Frontend
│       ├── index.html         # Login
│       ├── dashboard.html     # Shell principal
│       ├── modules/           # home, users, structure, admin-skins, importer, profile
│       └── shared/            # Design System + Core Framework
├── packages/
│   └── shared/                # Pacote Python compartilhado
│       ├── security/          # JWT e bcrypt
│       ├── schemas/           # Schemas base (auth, error codes)
│       └── exceptions/        # Exceções customizadas + códigos de erro
├── tests/                     # Testes do monorepo (raiz)
├── Makefile                   # Automação de tasks
├── podman-compose.yml         # Orquestração de containers
└── pytest.ini                 # Configuração de testes
```

---

Desenvolvido com foco em **SOLID**, **Clean Code** e **Performance**.

---
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
