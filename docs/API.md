# Documentação da API - GrindX

Esta API utiliza **FastAPI** para fornecer endpoints RESTful, com autenticação JWT e gerenciamento de recursos via SQLAlchemy.

## 🔑 Autenticação

Todos os endpoints que não estão listados abaixo como públicos requerem autenticação via cabeçalho `Authorization: Bearer <token>`.

- `POST /auth/login`: Realiza login e retorna tokens de acesso.
- `POST /auth/refresh`: Atualiza o token de acesso.

## 📁 Endpoints Principais

### Portal (Menu)
- `GET /portal/menu`: Retorna a estrutura completa de abas e módulos do sistema.

### Usuários
- `GET /usuarios/`: Lista usuários (requer permissão de Admin).
- `POST /usuarios/`: Cria novo usuário (requer permissão de Admin).

### Produtos
- `GET /produtos/`: Lista produtos.
- `POST /produtos/`: Cria novo produto (requer permissão de Admin/Operador).

## ⚠️ Status dos Endpoints
*Para uma lista completa e atualizada, acesse `/docs` (Swagger UI) com a API rodando localmente.*
