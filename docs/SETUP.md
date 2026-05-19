# Guia de Instalação — GrindX

Este guia descreve como configurar o ambiente de desenvolvimento do GrindX em uma máquina local.

## 📋 Pré-requisitos

- **Python 3.12+**
- **PostgreSQL**
- **Git**

## 🚀 Setup Inicial

1. **Clonar o Repositório:**
   ```powershell
   git clone <url-do-repositorio>
   cd GrindX
   ```

2. **Configurar Ambiente Python:**
   Cada pacote possui suas próprias dependências.
   ```powershell
   # Backend (Postgres)
   cd packages/api-postgres
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configurar Banco de Dados:**
   - Crie o banco de dados no PostgreSQL conforme definido no seu `.env`.
   - Execute as migrações:
     ```powershell
     python manage_db.py upgrade head
     ```
   - Popule os dados iniciais:
     ```powershell
     python seed.py
     ```

4. **Rodar a Aplicação:**
   - **API Postgres:** `make dev-postgres` (ou manualmente via uvicorn)
   - **Frontend:** `python -m http.server 5500 --directory packages/frontend-webapp`
   - Acesse em `http://localhost:5500`
