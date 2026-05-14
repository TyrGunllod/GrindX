# ERP — Sistema de Gestão Integrado

Monorepo para sistema ERP local com duas APIs FastAPI conectadas a bancos distintos.

## Arquitetura

| Serviço | Porta | Banco | Função |
|---|---|---|---|
| `api-postgres` | 8002 | PostgreSQL (LAN) | CRUD completo + Autenticação |
| `api-sqlserver` | 8001 | SQL Server (WAN) | Somente consulta |

## Estrutura

```
packages/
├── api-sqlserver/    → API read-only (consultas SQL Server)
├── api-postgres/     → API principal (CRUD + Auth via PostgreSQL)
└── shared/           → Código compartilhado (schemas, exceptions, security)
```

## Stack

- **Linguagem:** Python 3.12+
- **Framework:** FastAPI + Uvicorn
- **ORM:** SQLAlchemy 2.x (DeclarativeBase)
- **Auth:** JWT (python-jose) + bcrypt
- **Config:** pydantic-settings + python-dotenv
- **Logging:** structlog (JSON)
- **Testes:** pytest + httpx
- **Containers:** Podman rootless + podman-compose

## Setup Local

```bash
# 1. Criar ambiente virtual em cada API
cd packages/api-postgres
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Copiar e configurar variáveis de ambiente
copy .env.example .env

# 3. Executar a API
uvicorn app.main:app --reload --port 8002
```

## Comandos (Makefile)

```bash
make build          # Build das imagens
make up             # Subir containers
make down           # Parar containers
make logs           # Acompanhar logs
make test-postgres  # Testes api-postgres
make test-sqlserver # Testes api-sqlserver
make test-all       # Todos os testes
```

## Documentação das APIs

| API | Swagger | ReDoc |
|---|---|---|
| api-postgres | http://localhost:8002/v1/docs | http://localhost:8002/v1/redoc |
| api-sqlserver | http://localhost:8001/v1/docs | http://localhost:8001/v1/redoc |
