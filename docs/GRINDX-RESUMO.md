<!-- title: GrindX — Resumo Executivo | updated: 2026-05-25 -->

# GrindX — Resumo Executivo

---

## Status Atual

Projeto em desenvolvimento ativo — funcionalidades principais implementadas e rodando.

---

## Arquitetura em Uma Linha

Monorepo Python + Vanilla JS. Dois backends FastAPI independentes compartilhando JWT. Frontend Shell que carrega micro-módulos via iframe isolado. Menu de navegação dinâmico gerenciado pelo banco.

---

## Funcionalidades

- **Sub-abas (nested menu):** navegação hierárquica dinâmica gerenciada pelo banco
- **Forgot-password:** fluxo completo de recuperação de senha com envio de email
- **Skin system:** temas visuais customizáveis por empresa com persistência
- **Troca de senha:** alteração de senha pelo próprio usuário logado

---

## Acesso Rápido

```powershell
cd D:\_Projetos\GrindX

make dev-postgres    # API Postgres — porta 8002
make dev-sqlserver   # API SQL Server — porta 8001
python -m http.server 5500 --directory apps/frontend-webapp
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
| `apps/frontend-webapp/ARCHITECTURE_PORTAL.md` | Como criar novos módulos |
