<!-- title: Documentação GrindX | updated: 2026-05-20 -->

# GrindX — Documentação

Sistema de Gestão Integrado (ERP modular) em monorepo Python + Vanilla JS.

---

## Status do Projeto

**100% completo.** Backend, frontend, testes, CI/CD, assets visuais e sistema de skins implementados.

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
| [MAPA-ARQUIVOS.md](../MAPA-ARQUIVOS.md) | Inventário completo de arquivos |
| [GRINDX-RESUMO.md](../GRINDX-RESUMO.md) | Resumo executivo e acesso rápido |

### Pacotes

| Documento | Descrição |
|-----------|-----------|
| [api-postgres/README.md](../packages/api-postgres/README.md) | API principal (FastAPI + PostgreSQL) |
| [api-sqlserver/README.md](../packages/api-sqlserver/README.md) | API leitura (FastAPI + SQL Server) |
| [ARCHITECTURE_PORTAL.md](../packages/frontend-webapp/ARCHITECTURE_PORTAL.md) | Como criar novos módulos frontend |

---

## Acesso Rápido

| Serviço | URL | Porta |
|---------|-----|-------|
| Frontend | `http://localhost:5500` | 5500 |
| API Postgres | `http://localhost:8002` | 8002 |
| API SQL Server | `http://localhost:8001` | 8001 |
| Swagger UI | `http://localhost:8002/v1/docs` | 8002 |

### Credenciais de Teste

| Usuário | Senha | Perfil |
|---------|-------|--------|
| `admin` | `admin123` | Administrador |
| `operador` | `operador123` | Operador |
