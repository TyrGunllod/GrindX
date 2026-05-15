# SGI - Sistema de Gestão Integrado (Monorepo)

O **SGI** é um ERP modular construído com uma arquitetura moderna de monorepo, focado em alta escalabilidade, segurança e experiência do usuário premium.

## 🏗️ Arquitetura do Sistema

O projeto utiliza uma abordagem de **Micro-serviços no Backend** e um **Portal Orquestrador (Shell) no Frontend**.

### Backend
- **api-postgres (Porta 8002):** API principal em FastAPI. Gerencia persistência, autenticação centralizada (JWT), RBAC e a estrutura dinâmica do portal.
- **api-sqlserver (Porta 8003):** API dedicada para integração com bases legadas ou extração de dados complexos em SQL Server.
- **shared (Pacote):** Código compartilhado entre as APIs (Segurança, Schemas, Exceções).

### Frontend
- **Portal Modular (Porta 5500):** Um orquestrador (Host) que gerencia a navegação e carrega módulos independentes via Viewport isolada.
- **Micro-módulos:** Cada funcionalidade (Usuários, Estoque, Vendas) é um projeto standalone, permitindo desenvolvimento e testes isolados.

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

## 🛠️ Design System
O projeto utiliza um design system proprietário baseado em:
- **Glassmorphism:** Interfaces modernas e translúcidas.
- **Accessibility First:** Conformidade com WCAG (Cores, Contrastes e ARIA).
- **Dark/Light Mode:** Suporte nativo a temas.
- **UIFactory:** Geração programática de componentes para consistência visual absoluta.

---
Desenvolvido com foco em **SOLID**, **Clean Code** e **Performance**.
