# ==========================================
# GrindX — Sistema de Gestão Integrado
# Makefile para Windows (PowerShell/GnuMake)
# ==========================================

.PHONY: build up down logs test-postgres test-sqlserver test-all dev-postgres dev-sqlserver seed migrate clean

# ==========================================
# Desenvolvimento & Execução
# ==========================================

dev-postgres:
	@echo "Iniciando API Postgres na porta 8002..."
	cd packages/api-postgres && set PYTHONPATH=..&& .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --port 8002

dev-sqlserver:
	@echo "Iniciando API SQL Server na porta 8001..."
	cd packages/api-sqlserver && set PYTHONPATH=..&& .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --port 8001

# ==========================================
# Banco de Dados & Dados Iniciais
# ==========================================

migrate:
	@echo "Rodando migrações no PostgreSQL..."
	cd packages/api-postgres && set PYTHONPATH=..&& .\\.venv\\Scripts\\python manage_db.py upgrade head

seed:
	@echo "Populando banco de dados inicial..."
	cd packages/api-postgres && set PYTHONPATH=..&& .\\.venv\\Scripts\\python seed.py

# ==========================================
# Testes Automatizados
# ==========================================

test-postgres:
	@echo "Executando testes da API Postgres..."
	cd packages/api-postgres && set PYTHONPATH=..&& .\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short

test-sqlserver:
	@echo "Executando testes da API SQL Server..."
	cd packages/api-sqlserver && set PYTHONPATH=..&& .\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short

test-all: test-postgres test-sqlserver

# ==========================================
# Infraestrutura (Containers)
# ==========================================

build:
	podman-compose build

up:
	podman-compose up -d

down:
	podman-compose down

logs:
	podman-compose logs -f

# ==========================================
# Utilitários
# ==========================================

clean:
	@echo "Limpando arquivos temporários..."
	if exist .pytest_cache (rmdir /s /q .pytest_cache)
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
