<!-- title: Mapa de Arquivos GrindX | updated: 2026-08-23 -->

# GrindX — Mapa de Arquivos

Inventário completo do projeto. Atualizado em 2026-08-14.

**Status geral: funcionalidades principais implementadas e rodando.**

---

## Estrutura do Projeto

```
GrindX/
│
├── .agents/
│   └── skills/                      ✅ Skills do assistente (accessibility, frontend-design, python-executor, python-testing-patterns, seo)
│
├── .certs/
│   ├── .gitignore                   ✅
│   ├── dev-cert.pem                 ✅ Certificado dev HTTPS
│   └── dev-key.pem                  ✅ Chave dev HTTPS
│
├── .github/
│   └── workflows/
│       └── release.yml              ✅ CI — lint + testes + semantic-release
│
├── .opencode/
│   ├── .gitignore                   ✅
│   └── skills/
│       └── create-standalone-module/
│           ├── SKILL.md             ✅ Criar módulos standalone
│           └── templates/           ✅ Templates por tech stack
│       └── extrair-manual-modulo/
│           └── SKILL.md             ✅ Gera manuais de uso p/ o Agente de IA
│
├── .planning/
│   ├── PROJECT.md                   ✅
│   ├── STATE.md                     ✅
│   ├── ROADMAP.md                   ✅
│   ├── REQUIREMENTS.md              ✅
│   ├── codebase/                    ✅
│   ├── debug/                       ✅
│   ├── phase-01/                    ✅
│   ├── phases/                      ✅
│   └── research/                    ✅
│
├── docs/
│   ├── README.md               ✅ Portal de entrada — índice de documentos
│   ├── API.md                  ✅ Referência de endpoints
│   ├── DATABASE.md             ✅ Schema e migrações
│   ├── DEPLOYMENT.md           ✅ Deploy com containers
│   ├── DEPLOYMENT-OCI.md       ✅ Deploy do Agente de IA na OCI
│   ├── DEPLOYMENT-ALT.md       ✅ Deploy alternativo (Render + Neon + OCI Object Storage)
│   ├── DEPLOYMENT-RENDER.md    ✅ Passo a passo do deploy no Render
│   ├── DEPLOYMENT-SUPABASE.md  ✅ Configuração do Supabase (Postgres + pgvector)
│   ├── SECURITY.md             ✅ JWT e RBAC
│   ├── SETUP.md                ✅ Guia de instalação
│   ├── SKILLS.md               ✅ Skills do assistente
│   ├── MAPA-ARQUIVOS.md        ✅ Este arquivo
│   ├── GRINDX-RESUMO.md        ✅ Resumo executivo
│   ├── ARCHITECTURE_PORTAL.md  ✅ Arquitetura do portal frontend
│   ├── IMPORTACAO.md           ✅ Importação de módulos
│   ├── Revisions/
│   │   └── REVISAO-GRINDX.md   ✅ Revisão de pendências
│   └── superpowers/
│       ├── specs/              ✅ Design specs
│       └── plans/              ✅ Implementation plans
│
├── apps/
│   │
│   ├── agente-ia/                    ✅ Agente de IA (RAG) — assistente de manuais
│   │   ├── app/                      ✅ FastAPI + pipeline RAG (ingestion, embeddings, vectorstore, retrieval, generation)
│   │   ├── manuals/                  ✅ Manuais Markdown/CSV dos módulos
│   │   ├── tests/                    ✅ 10 testes
│   │   ├── Dockerfile                ✅ (pré-baixa modelo de embeddings)
│   │   └── requirements.txt          ✅
│   ├── api-postgres/
│   │   ├── app/
│   │   │   ├── auth/
│   │   │   │   ├── __init__.py         ✅
│   │   │   │   ├── dependencies.py     ✅
│   │   │   │   ├── router.py           ✅ forgot-password, change-password
│   │   │   │   └── service.py          ✅
│   │   │   ├── core/
│   │   │   │   ├── __init__.py         ✅
│   │   │   │   ├── cache.py            ✅ TTLCache (15 min)
│   │   │   │   ├── config.py           ✅
│   │   │   │   ├── exceptions.py       ✅
│   │   │   │   ├── logging.py          ✅
│   │   │   │   └── versioning.py       ✅
│   │   │   ├── data/
│   │   │   │   └── skin-templates/     ✅ Modelos de skin embutidos
│   │   │   ├── middleware/
│   │   │   │   ├── __init__.py         ✅
│   │   │   │   ├── rate_limit.py       ✅
│   │   │   │   ├── request_id.py       ✅
│   │   │   │   └── security_headers.py ✅
│   │   │   ├── models/
│   │   │   │   ├── __init__.py         ✅
│   │   │   │   ├── empresa.py          ✅ Skin system
│   │   │   │   ├── portal.py           ✅
│   │   │   │   ├── theme.py            ✅ Skin system
│   │   │   │   ├── theme_history.py    ✅ Skin system v2
│   │   │   │   └── usuario.py          ✅
│   │   │   ├── modules/
│   │   │   │   ├── iam/                ✅
│   │   │   │   ├── org/                ✅
│   │   │   │   └── portal/             ✅
│   │   │   ├── repositories/
│   │   │   │   ├── __init__.py         ✅
│   │   │   │   ├── theme_repository.py ✅ Skin system
│   │   │   │   └── usuario_repository.py   ✅
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py         ✅
│   │   │   │   ├── health_router.py    ✅
│   │   │   │   ├── import_router.py    ✅ Importação de módulos
│   │   │   │   ├── portal_router.py    ✅
│   │   │   │   ├── proxies.py          ✅
│   │   │   │   ├── theme_router.py     ✅ Skin system
│   │   │   │   └── usuario_router.py   ✅
│   │   │   ├── schemas/
│   │   │   │   ├── __init__.py         ✅
│   │   │   │   ├── theme.py            ✅ Skin system
│   │   │   │   ├── theme_history.py    ✅ Skin system v2
│   │   │   │   └── usuario.py          ✅
│   │   │   ├── services/
│   │   │   │   ├── __init__.py         ✅
│   │   │   │   ├── email_service.py    ✅
│   │   │   │   ├── theme_service.py    ✅ Skin system
│   │   │   │   └── usuario_service.py  ✅
│   │   │   ├── utils/
│   │   │   │   └── encryption.py       ✅
│   │   │   ├── __init__.py             ✅
│   │   │   ├── database.py             ✅
│   │   │   └── main.py                 ✅
│   │   ├── alembic/
│   │   │   ├── versions/
│   │   │   │   ├── __init__.py                          ✅
│   │   │   │   ├── 001_initial_schema.py                ✅
│   │   │   │   ├── 002_add_usuario_modulos.py           ✅
│   │   │   │   ├── 003_add_empresa_and_theme.py         ✅ Skin system
│   │   │   │   ├── 004_add_theme_history.py             ✅ Skin system v2
│   │   │   │   ├── 005_add_aba_parent_id.py             ✅
│   │   │   │   ├── 006_add_temp_password_fields.py      ✅
│   │   │   │   ├── 007_add_org_schema_tables.py         ✅
│   │   │   │   ├── 008_add_performance_indexes.py       ✅
│   │   │   │   ├── 009_add_layout_mode.py               ✅ Dual layout
│   │   │   │   ├── 010_add_theme_preference.py          ✅
│   │   │   │   ├── 011_add_layout_preference.py         ✅
│   │   │   │   ├── 012_add_modulo_ordem.py              ✅
│   │   │   │   ├── 013_add_profile_fields.py            ✅
│   │   │   │   ├── 014_add_numero_field.py              ✅
│   │   │   │   ├── 015_add_classificacao_field.py       ✅
│   │   │   │   ├── 016_add_telefone_celular_fields.py   ✅
│   │   │   │   ├── 017_add_rg_salario_fields.py         ✅
│   │   │   │   ├── 018_add_layout_mobile_preference.py  ✅
│   │   │   │   ├── 019_add_bairro_cidade_uf_fields.py   ✅
│   │   │   │   ├── 020_encrypt_sensitive_user_fields.py ✅
│   │   │   │   └── 021_add_aprovador_to_usuarios.py     ✅
│   │   │   ├── README.md               ✅
│   │   │   ├── env.py                  ✅
│   │   │   └── script.py.mako          ✅
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   │   ├── __init__.py                                  ✅
│   │   │   │   ├── test_auth.py                                 ✅
│   │   │   │   ├── test_auth_service.py                         ✅
│   │   │   │   ├── test_cache.py                                ✅
│   │   │   │   ├── test_import_module.py                        ✅ Importação de módulos
│   │   │   │   ├── test_import_module_frontend_only.py          ✅ Importação de módulos
│   │   │   │   ├── test_import_module_sqlserver.py              ✅ Importação de módulos
│   │   │   │   ├── test_import_router.py                        ✅ Importação de módulos
│   │   │   │   ├── test_models_theme.py                         ✅ Skin system
│   │   │   │   ├── test_models_theme_history.py                 ✅ Skin system v2
│   │   │   │   ├── test_repository_usuario.py                   ✅
│   │   │   │   ├── test_schema_validation.py                    ✅
│   │   │   │   ├── test_theme_repository.py                     ✅ Skin system
│   │   │   │   └── test_theme_service.py                        ✅ Skin system
│   │   │   ├── integration/
│   │   │   │   ├── __init__.py                     ✅
│   │   │   │   ├── test_autenticacao_integrada.py  ✅
│   │   │   │   ├── test_health.py                  ✅
│   │   │   │   ├── test_indexes.py                 ✅
│   │   │   │   └── test_theme_router.py            ✅ Skin system
│   │   │   ├── __init__.py             ✅
│   │   │   ├── conftest.py             ✅
│   │   │   ├── test_auth_security.py    ✅
│   │   │   ├── test_config_security.py  ✅
│   │   │   ├── test_rate_limit.py       ✅
│   │   │   └── test_upload_security.py  ✅
│   │   ├── .env                        ✅ (não versionar)
│   │   ├── .env.dev                    ✅ (não versionar)
│   │   ├── .env.example                ✅
│   │   ├── alembic.ini                 ✅
│   │   ├── Containerfile               ✅
│   │   ├── Dockerfile                  ✅
│   │   ├── manage_db.py                ✅
│   │   ├── MIGRATIONS_GUIDE.py         ✅
│   │   ├── README.md                   ✅
│   │   ├── requirements.txt            ✅
│   │   ├── requirements-dev.txt        ✅
│   │   ├── ruff.toml                   ✅
│   │   ├── seed.py                     ✅
│   │   ├── scripts/
│   │   │   └── import_module.py        ✅ Script de importação de módulos
│   │   └── uploads/
│   │       ├── fonts/                  ✅ Uploads — fontes
│   │       ├── icons/                  ✅ Uploads — ícones
│   │       └── logos/                  ✅ Uploads — logos (PNG uuid)
│   │
│   ├── api-sqlserver/
│   │   ├── app/
│   │   │   ├── core/
│   │   │   │   ├── __init__.py         ✅
│   │   │   │   ├── config.py           ✅
│   │   │   │   ├── exceptions.py       ✅
│   │   │   │   └── logging.py          ✅
│   │   │   ├── middleware/
│   │   │   │   ├── __init__.py         ✅
│   │   │   │   ├── request_id.py       ✅
│   │   │   │   └── security_headers.py ✅
│   │   │   ├── modules/                ✅ (vazio — módulos read-only importados)
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py         ✅
│   │   │   │   ├── health_router.py    ✅
│   │   │   │   └── protheus_router.py  ✅ Consultas Protheus (read-only)
│   │   │   ├── __init__.py             ✅
│   │   │   ├── database.py             ✅
│   │   │   └── main.py                 ✅
│   │   ├── tests/
│   │   │   ├── unit/                   ✅ (vazio)
│   │   │   │   └── __init__.py         ✅
│   │   │   ├── integration/
│   │   │   │   ├── __init__.py             ✅
│   │   │   │   ├── test_health.py          ✅
│   │   │   │   └── test_protheus.py        ✅
│   │   │   ├── __init__.py             ✅
│   │   │   └── conftest.py             ✅
│   │   ├── .env                        ✅ (não versionar)
│   │   ├── .env.dev                    ✅ (não versionar)
│   │   ├── .env.example                ✅
│   │   ├── Containerfile               ✅
│   │   ├── Dockerfile                  ✅
│   │   ├── README.md                   ✅
│   │   ├── requirements.txt            ✅
│   │   └── test_connection.py          ✅
│   │
│   └── frontend-webapp/
│       ├── assets/
│       │   ├── fonts/                  ✅ (hemico.ttf)
│       │   ├── apple-touch-icon.png    ✅ Visual assets
│       │   ├── favicon-16.png          ✅ Visual assets
│       │   ├── favicon-32.png          ✅ Visual assets
│       │   ├── favicon.ico             ✅ Visual assets
│       │   ├── favicon.png             ✅ Visual assets
│       │   ├── favicon.svg             ✅ Visual assets
│       │   ├── icon-192.png            ✅ Visual assets
│       │   ├── icon-512.png            ✅ Visual assets
│       │   ├── mask-icon.svg           ✅ Visual assets
│       │   └── site.webmanifest        ✅ Visual assets (PWA)
│       ├── modules/
│       │   ├── admin-skins/
│       │   │   ├── index.html          ✅ Skin system v2
│       │   │   ├── script.js           ✅ Skin system v2
│       │   │   └── style.css           ✅ Skin system v2
│       │   ├── admins/
│       │   │   ├── index.html          ✅
│       │   │   └── script.js           ✅
│       │   ├── home/
│       │   │   └── index.html          ✅
│       │   ├── importer/
│       │   │   ├── index.html          ✅ Importação de módulos
│       │   │   ├── script.js           ✅ Importação de módulos
│       │   │   └── style.css           ✅ Importação de módulos
│       │   ├── profile/
│       │   │   ├── index.html          ✅
│       │   │   ├── script.js           ✅
│       │   │   └── style.css           ✅
│       │   ├── structure/
│       │   │   ├── index.html          ✅
│       │   │   ├── script.js           ✅
│       │   │   └── style.css           ✅
│       │   └── users/
│       │       ├── index.html          ✅
│       │       ├── script.js           ✅
│       │       └── style.css           ✅
│       ├── shared/
│       │   ├── components/
│       │   │   ├── DataTable.js        ✅
│       │   │   ├── FormField.js        ✅
│       │   │   ├── LoadingSpinner.js   ✅
│       │   │   └── ReusableModal.js    ✅
│       │   ├── fonts/
│       │   │   ├── barlow-condensed-400.woff2 ✅ Self-hosted fonts
│       │   │   ├── barlow-condensed-700.woff2 ✅ Self-hosted fonts
│       │   │   ├── dm-sans-400.woff2          ✅ Self-hosted fonts
│       │   │   ├── dm-sans-500.woff2          ✅ Self-hosted fonts
│       │   │   └── dm-sans-700.woff2          ✅ Self-hosted fonts
│       │   ├── apiService.js           ✅
│       │   ├── app.js                  ✅ UIFactory (window.grindx.ui)
│       │   ├── baseController.js       ✅
│       │   ├── config.js               ✅ API_BASE_URL
│       │   ├── constants.js            ✅
│       │   ├── core.css                ✅ Tokens do design system
│       │   ├── inactivity.js           ✅
│       │   ├── skinLoader.js           ✅ Skin system, applyLayout(), clearCache()
│       │   └── validation.js           ✅
│       ├── tests/
│       │   └── inactivity.test.js      ✅
│       ├── apple-touch-icon.png        ✅ Visual assets
│       ├── dashboard.css               ✅
│       ├── dashboard.html              ✅
│       ├── dashboard.js                ✅
│       ├── widget/                     ✅ Mascote do Agente de IA (chat nativo)
│       │   ├── widget.js               ✅
│       │   ├── widget.css              ✅
│       │   └── grindx_chibi.png        ✅ Mascote
│       ├── modules/
│       │   └── configurar-agente/      ✅ Gestão → Configurar Agente
│       ├── Dockerfile                  ✅
│       ├── index.html                  ✅ forgot-password modal
│       ├── nginx.conf                  ✅ Reverse proxy / CSP
│       ├── script.js                   ✅ forgot-password controller
│       ├── skins/                      ✅ 21 JSONs (temas de skin/layout/teste)
│       │   ├── grindx-default.json     ✅ Skin system
│       │   ├── interozone-green.json   ✅ Skin system
│       │   └── ...                     ✅ demais JSONs (testes/layout)
│       ├── style.css                   ✅ modal styles (forgot-password)
│       ├── sw.js                       ✅ Service worker (PWA)
│       └── version.json                ✅ Semantic release version
│
├── packages/
│   │
│   └── shared/
│       ├── exceptions/
│       │   ├── __init__.py             ✅
│       │   ├── base.py                 ✅
│       │   └── codes.py                ✅ ErrorCode
│       ├── schemas/
│       │   ├── __init__.py             ✅
│       │   ├── auth.py                 ✅
│       │   └── base.py                 ✅
│       ├── security/
│       │   ├── __init__.py             ✅
│       │   ├── encryption.py           ✅
│       │   ├── jwt.py                  ✅
│       │   └── permissions.py          ✅
│       ├── tests/
│       │   └── test_permissions.py     ✅ 26 testes RBAC
│       ├── RBAC_GUIDE.py               ✅
│       ├── __init__.py                 ✅
│       └── pyproject.toml              ✅
│
├── tests/
│   ├── unit/
│   │   ├── __init__.py                 ✅
│   │   └── test_shared_modules.py      ✅
│   ├── integration/
│   │   ├── __init__.py                 ✅
│   │   └── test_pacotes.py             ✅
│   ├── __init__.py                     ✅
│   └── conftest.py                     ✅
│
├── AGENTS.md                           ✅ Memória do assistente
├── .gitignore                          ✅
├── CHANGELOG.md                        ✅ Histórico de releases
├── LICENSE                             ✅
├── Makefile                            ✅
├── README.md                           ✅
├── TASK.md                             ✅
├── compose.yaml                        ✅ Orquestração Podman
├── compose.postgres.yaml               ✅ PostgreSQL + pgvector
├── compose.oci.yaml                    ✅ Deploy OCI (agente + postgres)
├── .env.oci.example                    ✅ Variáveis de produção (OCI)
├── render.yaml                         ✅ Blueprint Render (deploy alternativo)
├── import/
│   └── modulo-custo.zip                ✅ Pacote de importação
├── infra/
│   └── nginx.conf                      ✅ Config de infra
├── Jenkinsfile                         ✅
├── opencode.json                       ✅ Config opencode
├── pyproject.toml                      ✅
├── pytest.ini                          ✅
├── ruff.toml                           ✅
├── scripts/                            ✅ 12 scripts de dev/deploy/versionamento
│   ├── dev-frontend.ps1                ✅ Dev server frontend (porta 8101)
│   ├── dev-https.ps1                   ✅ Dev HTTPS (Windows)
│   ├── dev-https.sh                    ✅ Dev HTTPS (Linux/macOS)
│   ├── dev-postgres.ps1                ✅ Dev server api-postgres (porta 8002)
│   ├── dev-sqlserver.ps1               ✅ Dev server api-sqlserver (porta 8001)
│   ├── export_openapi.py               ✅ Exporta OpenAPI das APIs
│   ├── external-access.ps1             ✅ Acesso externo
│   ├── generate_favicon.py             ✅ Gera favicons
│   ├── get_version.py                  ✅ Lê versão canônica
│   ├── kill-port.ps1                   ✅ Remove portproxy rules
│   ├── serve-https.py                  ✅ Serve HTTPS
│   └── update_frontend_version.py      ✅ Semantic release
└── skills-lock.json                    ✅ Skills registradas
```

---

## Regras de Versionamento

Nunca versionar:
- `.env` (apenas `.env.example`)
- `.venv/` e `__pycache__/`
- `.pytest_cache/` e `.ruff_cache/`
- `Thumbs.db`, `.DS_Store`
- Qualquer arquivo com credenciais reais

---

## Dependências Python

| Pacote | Versão mínima | Uso |
|--------|--------------|-----|
| FastAPI | 0.110.0 | Framework web |
| SQLAlchemy | 2.0.27 | ORM |
| psycopg | 3.1.18 | Driver PostgreSQL |
| pymssql | 2.2.11 | Driver SQL Server |
| pyodbc | 5.1.0 | Driver SQL Server (alternativo) |
| alembic | 1.13.1 | Migrações |
| pydantic-settings | 2.2.1 | Config via env |
| python-jose | 3.3.0 | JWT |
| bcrypt | 4.1.2 | Hash de senha |
| structlog | 24.1.0 | Logging estruturado |
| ruff | 0.3.0 | Linting e formatação |

Frontend: Vanilla JS, sem dependências externas, sem build tools.