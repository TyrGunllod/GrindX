<!-- title: GrindX — Resumo Executivo | updated: 2026-08-14 -->

# GrindX — Resumo Executivo

---

## Status Atual

Projeto em desenvolvimento ativo — funcionalidades principais implementadas e rodando. 264 testes automatizados (api-postgres 197, api-sqlserver 17, shared 26, root 24), CI/CD com semantic release, deploy via containers Podman.

---

## Arquitetura em Uma Linha

Monorepo Python + Vanilla JS. Dois backends FastAPI independentes compartilhando JWT. Frontend Shell que carrega micro-módulos via iframe isolado. Menu de navegação dinâmico gerenciado pelo banco.

---

## Funcionalidades

- **Sub-abas (nested menu):** navegação hierárquica dinâmica gerenciada pelo banco
- **Dual layout:** topbar (padrão) e sidebar, selecionável por empresa via tema
- **Forgot-password:** fluxo completo de recuperação de senha com envio de email
- **Skin system:** temas visuais customizáveis por empresa com persistência
- **Troca de senha:** alteração de senha pelo próprio usuário logado
- **Geração de PDF:** (pendente — xhtml2pdf está em requirements.txt mas não é usado; não há módulo de custos implementado)

---

## Acesso Rápido

```powershell
cd D:\_Projetos\GrindX

make dev-postgres    # API Postgres — porta 8002
make dev-sqlserver   # API SQL Server — porta 8001
python -m http.server 8101 --directory apps/frontend-webapp
```

| Serviço | URL |
|---------|-----|
| Frontend | `http://localhost:8101` |
| Swagger | `http://localhost:8002/v1/docs` |

### Credenciais

| Usuário | Senha | Perfil |
|---------|-------|--------|
| `admin` | `admin123` | Administrador |

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
| `docs/ARCHITECTURE_PORTAL.md` | Como criar novos módulos |
