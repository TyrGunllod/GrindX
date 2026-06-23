<!-- title: Documentação GrindX | updated: 2026-06-22 -->

# GrindX — Documentação

Sistema de Gestão Integrado (ERP modular) em monorepo Python + Vanilla JS.

---

## Status do Projeto

**Em desenvolvimento ativo.** Backend, frontend, testes (179+), CI/CD com semantic release, assets visuais, sistema de skins e reverse proxy prontos.

---

## Documentos

### Setup & Instalação

| Documento | Descrição |
|-----------|-----------|
| [SETUP.md](SETUP.md) | Guia detalhado de instalação e configuração |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deploy com containers, CI/CD e reverse proxy |

### Referência Técnica

| Documento | Descrição |
|-----------|-----------|
| [API.md](API.md) | Referência completa dos endpoints REST |
| [DATABASE.md](DATABASE.md) | Schema, modelos SQLAlchemy e migrações Alembic |
| [SECURITY.md](SECURITY.md) | Autenticação JWT, RBAC e middlewares de segurança |

### Projeto

| Documento | Descrição |
|-----------|-----------|
| [README.md](../README.md) | Visão geral, arquitetura e como rodar |
| [MAPA-ARQUIVOS.md](MAPA-ARQUIVOS.md) | Inventário completo de arquivos |
| [ARCHITECTURE_PORTAL.md](../apps/frontend-webapp/ARCHITECTURE_PORTAL.md) | Como criar novos módulos frontend |
| [SKILLS.md](SKILLS.md) | Skills do assistente e templates de criação |

### Pacotes

| Documento | Descrição |
|-----------|-----------|
| [api-postgres/README.md](../apps/api-postgres/README.md) | API principal (FastAPI + PostgreSQL) |
| [api-sqlserver/README.md](../apps/api-sqlserver/README.md) | API leitura (FastAPI + SQL Server) |

---

## Acesso Rápido

| Serviço | URL | Porta |
|---------|-----|-------|
| Frontend | `http://localhost:8101` | 8101 |
| API Postgres | `http://localhost:8002` | 8002 |
| API SQL Server | `http://localhost:8001` | 8001 |
| Swagger UI | `http://localhost:8002/v1/docs` | 8002 |

### Credenciais de Teste

| Usuário | Senha | Perfil |
|---------|-------|--------|
| `admin` | `admin123` | Administrador |
