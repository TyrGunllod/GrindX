<!-- title: Documentação GrindX | updated: 2026-08-23 -->

# GrindX — Documentação

Sistema de Gestão Integrado (ERP modular) em monorepo Python + Vanilla JS.

---

## Status do Projeto

**Em desenvolvimento ativo.** Backend, frontend, testes (264), CI/CD com semantic release, assets visuais, sistema de skins e reverse proxy prontos. Geração de PDF pendente (xhtml2pdf listado em requirements mas sem uso).

---

## Documentos

### Setup & Instalação

| Documento | Descrição |
|-----------|-----------|
| [SETUP.md](SETUP.md) | Guia detalhado de instalação e configuração |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deploy com containers, CI/CD e reverse proxy |
| [DEPLOYMENT-OCI.md](DEPLOYMENT-OCI.md) | Deploy do Agente de IA na Oracle Cloud (OCI) |
| [DEPLOYMENT-ALT.md](DEPLOYMENT-ALT.md) | Deploy alternativo (Render + Neon/Supabase + OCI Object Storage) |
| [DEPLOYMENT-SUPABASE.md](DEPLOYMENT-SUPABASE.md) | Configuração do Supabase (Postgres + pgvector) como banco do agente |

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
| [ARCHITECTURE_PORTAL.md](ARCHITECTURE_PORTAL.md) | Como criar novos módulos frontend |
| [SKILLS.md](SKILLS.md) | Skills do assistente e templates de criação |

### Pacotes

| Documento | Descrição |
|-----------|-----------|
| [api-postgres/README.md](../apps/api-postgres/README.md) | API principal (FastAPI + PostgreSQL) |
| [api-sqlserver/README.md](../apps/api-sqlserver/README.md) | API leitura (FastAPI + SQL Server) |
| [agente-ia/README.md](../apps/agente-ia/README.md) | Agente de IA (RAG) — assistente de manuais |

---

## Acesso Rápido

| Serviço | URL | Porta |
|---------|-----|-------|
| Frontend (HTTP) | `http://localhost:8101` | 8101 |
| Frontend (HTTPS) | `https://localhost` | 443 |
| API Postgres | `http://localhost:8002` | 8002 |
| API SQL Server | `http://localhost:8001` | 8001 |
| Agente de IA | `http://localhost:8003` | 8003 |
| Swagger UI | `http://localhost:8002/v1/docs` | 8002 |
| Swagger Agente | `http://localhost:8003/v1/docs` | 8003 |

### Credenciais de Teste

| Usuário | Senha | Perfil |
|---------|-------|--------|
| `admin` | `admin123` | Administrador |
