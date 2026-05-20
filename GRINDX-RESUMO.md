<!-- title: GrindX — Resumo Executivo | updated: 2026-05-20 -->

# GrindX — Resumo Executivo

---

## Status Atual

**100% completo.**

| Área | Status |
|------|--------|
| Backend `api-postgres` (FastAPI + PostgreSQL) | ✅ |
| Backend `api-sqlserver` (FastAPI + SQL Server) | ✅ |
| Frontend Portal Modular | ✅ |
| Design System (Glassmorphism + UIFactory) | ✅ |
| Módulos: `home`, `users`, `structure` | ✅ |
| Autenticação JWT + RBAC | ✅ |
| Suite de testes (160+) | ✅ |
| Documentação técnica completa | ✅ |
| CI/CD — GitHub Actions | ✅ |
| Assets visuais (favicon, fontes) | ✅ |

---

## Arquitetura em Uma Linha

Monorepo Python + Vanilla JS. Dois backends FastAPI independentes compartilhando JWT. Frontend Shell que carrega micro-módulos via iframe isolado. Menu de navegação dinâmico gerenciado pelo banco.

---

## Acesso Rápido

```powershell
cd D:\_Projetos\GrindX

make dev-postgres    # API Postgres — porta 8002
make dev-sqlserver   # API SQL Server — porta 8001
python -m http.server 5500 --directory packages/frontend-webapp
```

| Serviço | URL |
|---------|-----|
| Frontend | `http://localhost:5500` |
| Swagger | `http://localhost:8002/v1/docs` |

### Credenciais

| Usuário | Senha | Perfil |
|---------|-------|--------|
| `admin` | `admin123` | Administrador |
| `operador` | `operador123` | Operador |

---

## Testes

```powershell
make test-all    # todos os pacotes
pytest           # testes da raiz
```

---

## O Que Ainda Falta

1. Trocar `SECRET_KEY` para valor gerado aleatoriamente antes do deploy em produção
2. Decidir próximo módulo do ERP (produtos, estoque, vendas)

---

## Documentação

Portal de entrada: [`docs/README.md`](docs/README.md)

| Arquivo | Conteúdo |
|---------|----------|
| `README.md` | Visão geral, como rodar, estrutura |
| `MAPA-ARQUIVOS.md` | Inventário completo de arquivos |
| `docs/API.md` | Referência de endpoints |
| `docs/SETUP.md` | Instalação passo a passo |
| `docs/DEPLOYMENT.md` | Deploy + CI/CD |
| `docs/DATABASE.md` | Schema, modelos, migrações |
| `docs/SECURITY.md` | JWT, RBAC, middlewares |
| `packages/frontend-webapp/ARCHITECTURE_PORTAL.md` | Como criar novos módulos |
