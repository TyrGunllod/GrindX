<!-- title: API Postgres — GrindX | updated: 2026-05-20 -->

# GrindX — API Postgres (Principal)

API principal do sistema GrindX, responsável pela persistência no PostgreSQL, gerenciamento de usuários, autenticação JWT e controle de estoque.

---

## Funcionalidades

- **Autenticação:** Sistema de login com JWT (Access & Refresh Tokens)
- **Portal Dinâmico:** Gerenciamento centralizado da árvore de menus (Abas e Módulos) via API
- **RBAC:** Controle de acesso baseado em perfis (Admin, Operador, Leitura)
- **Gestão de Usuários:** CRUD completo com validação de e-mails e hashing de senhas
- **Gestão de Estoque:** CRUD completo de produtos com soft delete

---

## Tecnologias

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| FastAPI | 0.110.0+ | Framework web |
| SQLAlchemy | 2.0.27+ | ORM |
| Alembic | 1.13.1+ | Migrações de banco |
| Pydantic | v2 | Validação de dados |
| PostgreSQL | 14+ | Banco principal |

---

## Estrutura do Pacote

```
api-postgres/
├── alembic/          # Migrações do banco de dados
├── app/
│   ├── auth/         # Autenticação e dependências JWT
│   ├── core/         # Configurações e logging
│   ├── middleware/   # Middlewares customizados
│   ├── models/       # Modelos SQLAlchemy (2.0 Style)
│   ├── repositories/ # Camada de acesso a dados (Repository Pattern)
│   ├── routers/      # Endpoints da API
│   ├── schemas/      # Modelos Pydantic (DTOs)
│   └── services/     # Regras de negócio
├── tests/            # Testes unitários e de integração
├── manage_db.py      # CLI para migrações
└── seed.py           # Script para popular banco inicial
```

---

## Configuração Local

### 1. Ambiente Virtual

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste as credenciais do PostgreSQL.

### 3. Banco de Dados

```powershell
# Rodar migrações
python manage_db.py upgrade head

# Popular dados iniciais (admin/admin123)
python seed.py
```

### 4. Execução

```powershell
uvicorn app.main:app --reload --port 8002
```

---

## Testes

Os testes utilizam SQLite em memória para garantir isolamento e velocidade.

```powershell
.\.venv\Scripts\python.exe -m pytest
```

---

## Notas de Versão

- **Modernização SQLAlchemy:** Todo o código de repositórios foi atualizado para o estilo 2.0 (`select()`)
- **Correção Alembic:** `env.py` corrigido para importar modelos automaticamente no `autogenerate`
- **Configuração Robusta:** `Settings` agora ignora campos extras e trata listas CORS em formato JSON strings
