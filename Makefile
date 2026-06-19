# ==========================================
# GrindX — Makefile Unificado (Win/Linux)
# ==========================================

.PHONY: build up down logs images \
        dev-postgres dev-sqlserver dev-frontend dev-all \
        migrate seed \
        test-postgres test-sqlserver test-shared test-root test-all \
        lint format clean volumes deploy

# ==========================================
# Detecção de plataforma
# ==========================================
ifeq ($(OS),Windows_NT)
    PY = python
    VENV_PY = .venv\Scripts\python
    SEP = ;
    PP_APP = set PYTHONPATH=../../packages&&
    PP_ROOT = set PYTHONPATH=apps/api-postgres$(SEP)apps/api-sqlserver$(SEP)packages&&
    PP_SHARED = set PYTHONPATH=..&&
else
    PY = python3
    VENV_PY = .venv/bin/python
    SEP = :
    PP_APP = PYTHONPATH=../../packages
    PP_ROOT = PYTHONPATH=apps/api-postgres:apps/api-sqlserver:packages
    PP_SHARED = PYTHONPATH=..
endif

# ==========================================
# Desenvolvimento
# ==========================================

dev-postgres:
	@echo "Iniciando API Postgres na porta 8002..."
	cd apps/api-postgres && $(PP_APP) $(VENV_PY) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

dev-sqlserver:
	@echo "Iniciando API SQL Server na porta 8001..."
	cd apps/api-sqlserver && $(PP_APP) $(VENV_PY) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

dev-frontend:
	@echo "Iniciando Frontend na porta 8101..."
	$(PY) -m http.server 8101 --directory apps/frontend-webapp --bind 0.0.0.0

dev-all:
ifeq ($(OS),Windows_NT)
	@echo "Subindo todos os servicos GrindX..."
	pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd apps/api-postgres; $$env:PYTHONPATH=(Get-Item ..\..\packages).FullName; .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002'"
	pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd apps/api-sqlserver; $$env:PYTHONPATH=(Get-Item ..\..\packages).FullName; .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001'"
	pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd $(CURDIR); $(PY) -m http.server 8101 --directory apps/frontend-webapp --bind 0.0.0.0'"
	@echo "Acesse: http://localhost:8101"
else
	@echo "Subindo todos os servicos GrindX..."
	@echo "Abra terminais separados para cada servico:"
	@echo "  make dev-postgres"
	@echo "  make dev-sqlserver"
	@echo "  make dev-frontend"
	@echo "Acesse: http://localhost:8101"
endif

# ==========================================
# Banco de Dados
# ==========================================

migrate:
	@echo "Rodando migracoes no PostgreSQL..."
	cd apps/api-postgres && $(PP_APP) $(VENV_PY) manage_db.py upgrade head

seed:
	@echo "Populando banco de dados inicial..."
	cd apps/api-postgres && $(PP_APP) $(VENV_PY) seed.py

# ==========================================
# Testes
# ==========================================

test-postgres:
	@echo "Executando testes da API Postgres..."
	cd apps/api-postgres && $(PP_APP) $(VENV_PY) -m pytest tests/ -v --tb=short

test-sqlserver:
	@echo "Executando testes da API SQL Server..."
	cd apps/api-sqlserver && $(PP_APP) $(VENV_PY) -m pytest tests/ -v --tb=short

test-shared:
	@echo "Executando testes do pacote shared..."
	cd packages/shared && $(PP_SHARED) $(VENV_PY) -m pytest tests/ -v --tb=short

test-root:
	@echo "Executando testes da raiz do monorepo..."
	$(PP_ROOT) $(VENV_PY) -m pytest tests/ -v --tb=short

test-all: test-postgres test-sqlserver test-shared test-root

# ==========================================
# Lint e Formatação
# ==========================================

format:
	ruff format packages/ apps/

lint:
	ruff check --fix .
	ruff check .

# ==========================================
# Containers
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
# Volumes (runtime)
# ==========================================

volumes:
ifeq ($(OS),Windows_NT)
	@echo "Criando diretorios de volumes..."
	if not exist "Containers\volumes\grindx\frontend" mkdir "Containers\volumes\grindx\frontend"
	if not exist "Containers\volumes\grindx\api-postgres\uploads" mkdir "Containers\volumes\grindx\api-postgres\uploads"
	@echo "Copiando nginx.conf para o volume..."
	copy /y "apps\frontend-webapp\nginx.conf" "Containers\volumes\grindx\frontend\nginx.conf" >nul
	@echo "Volumes prontos."
else
	@echo "Criando diretorios de volumes..."
	mkdir -p Containers/volumes/grindx/frontend
	mkdir -p Containers/volumes/grindx/api-postgres/uploads
	@echo "Copiando nginx.conf para o volume..."
	cp apps/frontend-webapp/nginx.conf Containers/volumes/grindx/frontend/nginx.conf
	@echo "Volumes prontos."
endif

# ==========================================
# Imagens (build com versão)
# ==========================================

images:
	$(eval V := $(shell python scripts/get_version.py))
	@echo "Construindo imagens versao $(V)..."
	podman build -t grindx-frontend:$(V) -f apps/frontend-webapp/Dockerfile apps/frontend-webapp
	podman build -t grindx-api-sqlserver:$(V) -f apps/api-sqlserver/Dockerfile apps/api-sqlserver
	podman build -t grindx-api-postgres:$(V) -f apps/api-postgres/Dockerfile apps/api-postgres
	@echo "Imagens criadas: grindx-*:$(V)"

# ==========================================
# Deploy (exportar configs para diretório)
# ==========================================

deploy:
	@if [ "$(DEST)" = "" ]; then echo "Uso: make deploy DEST=/caminho/para/deploy"; exit 1; fi
	@echo "Exportando configs para $(DEST)/GrindX/..."
	mkdir -p "$(DEST)/GrindX/Containers/volumes/grindx/frontend"
	mkdir -p "$(DEST)/GrindX/Containers/volumes/grindx/api-postgres/uploads"
	mkdir -p "$(DEST)/GrindX/import"
	cp compose.yaml "$(DEST)/GrindX/"
	cp .env.postgres "$(DEST)/GrindX/"
	cp .env.sqlserver "$(DEST)/GrindX/"
	cp apps/frontend-webapp/nginx.conf "$(DEST)/GrindX/Containers/volumes/grindx/frontend/nginx.conf"
	cp -r packages "$(DEST)/GrindX/packages"
	@echo "Configs exportadas para $(DEST)/GrindX/"
	@echo "Proximo passo:"
	@echo "  cd $(DEST)/GrindX"
	@echo "  make volumes  (cria diretorios de volumes)"
	@echo "  podman-compose up -d"

# ==========================================
# Limpeza
# ==========================================

clean:
ifeq ($(OS),Windows_NT)
	@echo "Limpando arquivos temporarios..."
	if exist .pytest_cache (rmdir /s /q .pytest_cache)
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
else
	@echo "Limpando arquivos temporarios..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
endif
