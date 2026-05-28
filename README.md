<!-- title: GrindX — Sistema de Gestão Integrado | updated: 2026-05-28 -->

# GrindX — Sistema de Gestão Integrado (Monorepo)

O **GrindX** é um ERP modular construído com arquitetura de monorepo, focado em escalabilidade, segurança e experiência do usuário premium.

---

## Status do Projeto

Projeto em desenvolvimento ativo. Funcionalidades principais implementadas e funcionais (autenticação JWT + RBAC, CRUD de usuários e produtos, portal modular com shell, skin system). CI/CD, testes automatizados (160+) e documentação acompanham o desenvolvimento.

---

## Arquitetura

O projeto utiliza micro-serviços no backend e um Portal Orquestrador (Shell) no frontend.

### Backend

- **`api-postgres` (porta 8002):** API principal em FastAPI. Gerencia autenticação JWT, RBAC, usuários, produtos e a estrutura dinâmica do portal.
- **`api-sqlserver` (porta 8001):** API somente leitura para integração com bases SQL Server legadas. Valida tokens JWT emitidos pela `api-postgres`.
- **`shared`:** Pacote Python compartilhado entre as APIs — segurança, schemas e exceções.

### Frontend

- **Portal Modular (porta 5500):** Shell que gerencia navegação e carrega módulos via iframe isolado.
- **Módulos:** `home`, `users`, `structure`, `admin-skins` — cada um é standalone e testável independentemente.
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
python manage_db.py upgrade head
python seed.py

# 4. Rodar APIs (terminais separados)
make dev-postgres    # porta 8002
make dev-sqlserver   # porta 8001

# 5. Rodar frontend
python -m http.server 5500 --directory apps/frontend-webapp
```

Acesse em `http://localhost:5500`.

### Credenciais de Teste

| Usuário | Senha | Perfil |
|---------|-------|--------|
| `admin` | `admin123` | Administrador |
| `operador` | `operador123` | Operador |

---

## Testes

Suite com 160+ testes cobrindo unitários, integração e validação do monorepo.

| Pacote | Testes | Cobertura |
|--------|--------|-----------|
| `api-postgres` | 110 | Auth, RBAC, produtos, usuários |
| `api-sqlserver` | 8+ | Cliente SQL Server |
| `shared` | 26 | Permissões RBAC |
| `tests/` (raiz) | 21 | Validação de pacotes |

```powershell
make test-postgres    # somente api-postgres
make test-sqlserver   # somente api-sqlserver
make test-all         # todos os pacotes
pytest                # testes da raiz
```

---

## CI/CD

Workflows em `.github/workflows/`:

- **`tests.yml`** — executa os três conjuntos de testes em push/PR para `main` e `develop`. Os testes da `api-postgres` usam SQLite in-memory (sem PostgreSQL real no CI).
- **`lint.yml`** — executa `ruff check` e `ruff format --check` em todo `packages/`.

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
| [`MAPA-ARQUIVOS.md`](MAPA-ARQUIVOS.md) | Inventário completo de arquivos |

---

## Design System

- **Glassmorphism** com tokens CSS centralizados em `shared/core.css`
- **`UIFactory`** (`shared/app.js`) para criação programática de componentes
- **Componentes:** `FormField`, `DataTable`, `ReusableModal`, `LoadingSpinner`
- **Skin system:** tema visual customizável por empresa, aplicado via `skinLoader.js`
- **Dark/Light mode** com persistência de tema
- **Fluxo de forgot-password** com envio de email e troca de senha
- **Utilitários:** `apiService.js` (chamadas centralizadas com auto-auth), `validation.js` (validação de formulários e URLs)
- **WCAG** — acessibilidade como primeira camada

---

## Estrutura de Pastas

```
GrindX/
├── .github/workflows/
│   ├── tests.yml           # CI — testes automatizados
│   └── lint.yml            # CI — qualidade de código
├── docs/                   # Documentação técnica
│   ├── README.md           # Portal de entrada
│   ├── API.md
│   ├── SETUP.md
│   ├── DEPLOYMENT.md
│   ├── DATABASE.md
│   ├── SECURITY.md
│   └── SKILLS.md
├── apps/
│   ├── api-postgres/       # API principal (FastAPI + PostgreSQL)
│   │   ├── app/
│   │   │   ├── auth/       # JWT — router, service, dependencies
│   │   │   ├── core/       # config, exceptions, logging
│   │   │   ├── middleware/ # rate limit, request id, security headers
│   │   │   ├── modules/    # Modelos por schema (iam, portal, catalogo, org)
│   │   │   ├── models/     # Re-export shims (compatibilidade)
│   │   │   ├── repositories/
│   │   │   ├── routers/    # auth, health, portal, produto, usuario
│   │   │   ├── schemas/
│   │   │   └── services/   # email_service, produto_service, usuario_service
│   │   ├── alembic/        # Migrações do banco
│   │   ├── tests/          # 110 testes
│   │   └── ...
│   ├── api-sqlserver/      # API somente leitura (SQL Server)
│   │   ├── app/
│   │   │   ├── auth/       # Validação JWT (sem emissão)
│   │   │   ├── core/
│   │   │   ├── middleware/
│   │   │   ├── routers/    # cliente, health
│   │   │   └── services/
│   │   ├── tests/
│   │   └── ...
│   └── frontend-webapp/    # Portal Frontend
│       ├── index.html      # Shell/Host
│       ├── dashboard.html
│       ├── modules/        # home, users, structure, admin-skins
│       └── shared/         # Design System
├── packages/
│   └── shared/             # Pacote Python compartilhado
│       ├── security/       # JWT e bcrypt
│       ├── schemas/        # Schemas base
│       └── exceptions/     # Exceções customizadas
├── tests/                  # Testes do monorepo (raiz)
├── Makefile                # Automação de tasks
├── podman-compose.yml      # Orquestração de containers
└── pytest.ini              # Configuração de testes
```

---

Desenvolvido com foco em **SOLID**, **Clean Code** e **Performance**.

---
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
