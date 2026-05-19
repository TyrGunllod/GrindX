# Schema do Banco de Dados — GrindX

O projeto utiliza **SQLAlchemy 2.0** como ORM para gerenciar o banco de dados PostgreSQL.

## 🏛️ Modelagem Principal

A modelagem é dividida entre os pacotes `api-postgres` (dados transacionais) e o `shared` (esquemas base).

- **`Usuario`**: Gerencia dados de autenticação e perfis (RBAC).
- **`Produto`**: Gerencia o estoque transacional.
- **`Menu/Aba/Modulo`**: Gerencia a estrutura dinâmica do portal (Portal Metadata).

## 🗄️ Gerenciamento de Migrações
As migrações são gerenciadas pelo **Alembic**. Todo novo campo ou modelo adicionado deve gerar uma nova migração:

```powershell
alembic revision --autogenerate -m "descrição da mudança"
alembic upgrade head
```
