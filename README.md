# GrindX - Sistema de Gestão Integrado (Monorepo)

O **GrindX** é um ERP modular construído com uma arquitetura moderna de monorepo, focado em alta escalabilidade, segurança e experiência do usuário premium.

## 📊 Status do Projeto
✅ **80% Completo** - Funcionalidades principais implementadas, documentação criada, frontend módulos funcionais

## 🏗️ Arquitetura do Sistema

O projeto utiliza uma abordagem de **Micro-serviços no Backend** e um **Portal Orquestrador (Shell) no Frontend**.

### Backend
- **api-postgres (Porta 8002):** API principal em FastAPI. Gerencia persistência, autenticação centralizada (JWT), RBAC e a estrutura dinâmica do portal.
- **api-sqlserver (Porta 8001):** API dedicada para integração com bases legadas ou extração de dados complexos em SQL Server.
- **shared (Pacote):** Código compartilhado entre as APIs (Segurança, Schemas, Exceções).

### Frontend
- **Portal Modular (Porta 5500):** Um orquestrador (Host) que gerencia a navegação e carrega módulos independentes via Viewport isolada.
- **Micro-módulos:** Cada funcionalidade (Usuários, Estoque, Vendas) é um projeto standalone, permitindo desenvolvimento e testes isolados.
- **Módulo de Estrutura:** Implementado para gestão de abas e módulos do sistema.

## 🚀 Como Rodar o Projeto

### Pré-requisitos
- Python 3.12+
- PostgreSQL
- SQL Server (Opcional para módulos de consulta)

### Inicialização Rápida (Makefile)
```bash
# Instalar dependências (Virtualenv)
make install

# Rodar a API Postgres
make dev-postgres

# Rodar o Front-end (em outro terminal)
python -m http.server 5500 --directory packages/frontend-webapp
```

### Credenciais de Teste (Seed)
| Usuário | Senha | Perfil |
| :--- | :--- | :--- |
| `admin` | `admin123` | Administrador |
| `operador` | `operador123` | Operador |

## 📚 Documentação

Documentação completa disponível na pasta `/docs`:
- **API.md** - Referência da API REST
- **SETUP.md** - Guia de instalação e configuração
- **DEPLOYMENT.md** - Instruções de deploy em produção
- **DATABASE.md** - Esquema do banco de dados
- **SECURITY.md** - Políticas de segurança e autenticação

## 🛠️ Design System
O projeto utiliza um design system proprietário baseado em:
- **Glassmorphism:** Interfaces modernas e translúcidas.
- **Accessibility First:** Conformidade com WCAG (Cores, Contrastes e ARIA).
- **Dark/Light Mode:** Suporte nativo a temas.
- **UIFactory:** Geração programática de componentes para consistência visual absoluta.
- **Componentes Compartilhados:** FormField, DataTable, ReusableModal, LoadingSpinner

## 📦 Estrutura de Pastas

```
Grindx/
│
├── docs/                       # Documentação do projeto
├── packages/
│   ├── api-postgres/           # API Principal (FastAPI + PostgreSQL)
│   ├── api-sqlserver/          # API Integração SQL Server
│   ├── frontend-webapp/        # Portal Frontend
│   │   ├── index.html          # Shell/Host
│   │   ├── dashboard.html      # Dashboard principal
│   │   ├── modules/            # Micro-módulos
│   │   │   ├── home/           # Módulo Home
│   │   │   ├── users/          # Módulo de Usuários
│   │   │   └── structure/      # Módulo de Gestão de Estrutura
│   │   └── shared/             # Design System & Componentes
│   │       ├── components/     # Componentes reutilizáveis
│   │       ├── core.css        # Variáveis CSS (Tokens)
│   │       ├── app.js          # Configuração global
│   │       ├── apiService.js   # Cliente HTTP
│   │       ├── constants.js    # Constantes do sistema
│   │       ├── validation.js   # Validação client-side
│   │       └── baseController.js # Controller base
│   └── shared/                 # Código Compartilhado Backend
│       ├── security.py         # Funções de segurança
│       ├── schemas.py          # Schemas compartilhados
│       └── exceptions.py       # Exceções customizadas
├── .gitignore                  # Configuração Git
├── LICENSE                     # Licença do software
├── Makefile                    # Automação de tasks
├── podman-compose.yml          # Orquestração de containers
└── README.md                   # Este arquivo
```

---
Desenvolvido com foco em **SOLID**, **Clean Code** e **Performance**.
