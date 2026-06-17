# ==========================================
# GrindX — Sistema de Gestão Integrado
# Makefile para Windows (PowerShell/GnuMake)
# ==========================================

.PHONY: build up down logs test-postgres test-sqlserver test-all dev-postgres dev-sqlserver dev-frontend dev-all seed migrate clean

# ==========================================
# Desenvolvimento & Execução
# ==========================================

dev-postgres:
	@echo "Iniciando API Postgres na porta 8002..."
	cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

dev-sqlserver:
	@echo "Iniciando API SQL Server na porta 8001..."
	cd apps/api-sqlserver && set PYTHONPATH=..\..\packages&& .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

dev-frontend:
	@echo "Iniciando Frontend na porta 8101 (acessivel na rede)..."
	python -m http.server 8101 --directory apps/frontend-webapp --bind 0.0.0.0

dev-all:
	@echo "Subindo todos os servicos GrindX..."
	pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd apps/api-postgres; $$env:PYTHONPATH=(Get-Item ..\..\packages).FullName; .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002'"
	pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd apps/api-sqlserver; $$env:PYTHONPATH=(Get-Item ..\..\packages).FullName; .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001'"
	pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'python -m http.server 8101 --directory apps/frontend-webapp --bind 0.0.0.0'"
	@echo Acesse: http://localhost:8101

# ==========================================
# Banco de Dados & Dados Iniciais
# ==========================================

migrate:
	@echo "Rodando migracoses no PostgreSQL..."
	cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .\\.venv\\Scripts\\python manage_db.py upgrade head

seed:
	@echo "Populando banco de dados inicial..."
	cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .\\.venv\\Scripts\\python seed.py

# ==========================================
# Testes Automatizados
# ==========================================

test-postgres:
	@echo "Executando testes da API Postgres..."
	cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short

test-sqlserver:
	@echo "Executando testes da API SQL Server..."
	cd apps/api-sqlserver && set PYTHONPATH=..\..\packages&& .\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short

test-shared:
	@echo "Executando testes do pacote shared..."
	cd packages/shared && set PYTHONPATH=..&& .\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short

test-root:
	@echo "Executando testes da raiz do monorepo..."
	set PYTHONPATH=apps\\api-postgres;apps\\api-sqlserver;packages&& .\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short

test-all: test-postgres test-sqlserver test-shared test-root

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
	@echo "Limpando arquivos temporarios..."
	if exist .pytest_cache (rmdir /s /q .pytest_cache)
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
