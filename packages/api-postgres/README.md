# ERP — API Postgres (Principal)

Esta é a API principal do sistema ERP, responsável pela persistência centralizada no PostgreSQL, gerenciamento de usuários, autenticação JWT e controle de estoque.

## 🚀 Funcionalidades

- **Autenticação:** Sistema de login com JWT (Access & Refresh Tokens).
- **RBAC (Role-Based Access Control):** Controle de acesso baseado em perfis (Admin, Operador, Leitura).
- **Gestão de Estoque:** CRUD completo de produtos com soft delete.
- **Segurança:** Middlewares para Rate Limiting, Security Headers e CORS configuráveis.
- **Observabilidade:** Logs estruturados em JSON (structlog) e endpoint de health check.

## 🛠️ Tecnologias

- **FastAPI:** Framework web moderno e performático.
- **SQLAlchemy 2.0:** ORM com suporte a tipagem estática e sintaxe `select()`.
- **Alembic:** Gerenciamento de migrações de banco de dados.
- **Pydantic v2:** Validação de dados e configurações.
- **PostgreSQL:** Banco de dados relacional para persistência principal.

## 📂 Estrutura do Pacote

```
api-postgres/
├── alembic/          # Migrações do banco de dados
├── app/
│   ├── auth/         # Lógica de autenticação e dependências
│   ├── core/         # Configurações e logging
│   ├── middleware/   # Middlewares customizados
│   ├── models/       # Modelos SQLAlchemy (2.0 Style)
│   ├── repositories/ # Camada de acesso a dados (Pattern Repository)
│   ├── routers/      # Endpoints da API
│   ├── schemas/      # Modelos Pydantic (DTOs)
│   └── services/     # Regras de negócio
├── tests/            # Testes unitários e de integração
├── manage_db.py      # CLI para migrações
└── seed.py           # Script para popular banco inicial
```

## ⚙️ Configuração Local

1.  **Ambiente Virtual:**
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Variáveis de Ambiente:**
    Copie o `.env.example` para `.env` e ajuste as credenciais do PostgreSQL.

3.  **Banco de Dados:**
    ```powershell
    # Rodar migrações
    python manage_db.py upgrade head
    
    # Popular dados iniciais (admin/admin123)
    python seed.py
    ```

4.  **Execução:**
    ```powershell
    uvicorn app.main:app --reload --port 8002
    ```

## 🧪 Testes

Os testes utilizam SQLite em memória para garantir isolamento e velocidade.

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## 📝 Notas de Versão (Revisão Recente)

- **Modernização SQLAlchemy:** Todo o código de repositórios foi atualizado para o estilo 2.0 (`select()`).
- **Correção Alembic:** `env.py` corrigido para importar modelos automaticamente no `autogenerate`.
- **Configuração Robusta:** `Settings` agora ignora campos extras e trata listas CORS em formato JSON strings.
