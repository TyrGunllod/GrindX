# ==========================================
# GrindX — Makefile Unificado (Win/Linux)
# ==========================================

.PHONY: venv build up down logs images \
        dev-postgres dev-sqlserver dev-frontend dev-all dev-kill-port \
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
    IMG_DIR = $(USERPROFILE)/Containers/images
    VOLUMES_DIR = $(USERPROFILE)/Containers/volumes
else
    PY = python3
    VENV_PY = .venv/bin/python
    SEP = :
    PP_APP = PYTHONPATH=../../packages
    PP_ROOT = PYTHONPATH=apps/api-postgres:apps/api-sqlserver:packages
    PP_SHARED = PYTHONPATH=..
    IMG_DIR = $(HOME)/Containers/images
    VOLUMES_DIR = $(HOME)/Containers/volumes
endif

# ==========================================
# Desenvolvimento
# ==========================================

dev-postgres:
ifeq ($(OS),Windows_NT)
	@echo "Iniciando API Postgres na porta 8002..."
	pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/dev-postgres.ps1
else
	@echo "Iniciando API Postgres na porta 8002..."
	cd apps/api-postgres && $(PP_APP) $(VENV_PY) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
endif

dev-sqlserver:
ifeq ($(OS),Windows_NT)
	@echo "Iniciando API SQL Server na porta 8001..."
	pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/dev-sqlserver.ps1
else
	@echo "Iniciando API SQL Server na porta 8001..."
	cd apps/api-sqlserver && $(PP_APP) $(VENV_PY) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
endif

dev-frontend:
ifeq ($(OS),Windows_NT)
	@echo "Iniciando Frontend na porta 8101..."
	pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/dev-frontend.ps1
else
	@echo "Iniciando Frontend na porta 8101..."
	$(PY) -m http.server 8101 --directory apps/frontend-webapp --bind 0.0.0.0
endif

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

dev-kill-port:
ifeq ($(OS),Windows_NT)
	@echo "Liberando portas de desenvolvimento (8001, 8002, 8101)..."
	pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/kill-port.ps1
else
	@echo "Linux: use fuser -k 8002/tcp ou lsof -ti:8002 | xargs kill"
endif

# ==========================================
# Ambiente Virtual
# ==========================================

venv:
	@echo "=== Criando venv para api-postgres ==="
	cd apps/api-postgres && $(PY) -m venv .venv
	cd apps/api-postgres && $(VENV_PY) -m pip install --upgrade pip
	cd apps/api-postgres && $(VENV_PY) -m pip install -r requirements.txt
	@echo "=== Criando venv para api-sqlserver ==="
	cd apps/api-sqlserver && $(PY) -m venv .venv
	cd apps/api-sqlserver && $(VENV_PY) -m pip install --upgrade pip
	cd apps/api-sqlserver && $(VENV_PY) -m pip install -r requirements.txt
	@echo "Venus criados com sucesso!"

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
	@echo "Criando diretorios de volumes em $(VOLUMES_DIR)..."
ifeq ($(OS),Windows_NT)
	if not exist "$(VOLUMES_DIR)\grindx\frontend" mkdir "$(VOLUMES_DIR)\grindx\frontend"
	if not exist "$(VOLUMES_DIR)\grindx\api-postgres\uploads" mkdir "$(VOLUMES_DIR)\grindx\api-postgres\uploads"
	if exist "apps\frontend-webapp\nginx.conf" copy /y "apps\frontend-webapp\nginx.conf" "$(VOLUMES_DIR)\grindx\frontend\nginx.conf" >nul
else
	mkdir -p "$(VOLUMES_DIR)/grindx/frontend"
	mkdir -p "$(VOLUMES_DIR)/grindx/api-postgres/uploads"
	test -f apps/frontend-webapp/nginx.conf && cp apps/frontend-webapp/nginx.conf "$(VOLUMES_DIR)/grindx/frontend/nginx.conf" || true
endif
	@echo "Volumes prontos em $(VOLUMES_DIR)."

# ==========================================
# Imagens (build com versão)
# ==========================================

images:
	$(eval V := $(shell $(PY) scripts/get_version.py))
	@echo "Construindo imagens versao $(V)..."
	podman build -t grindx-frontend:$(V) -t grindx-frontend:latest -f apps/frontend-webapp/Dockerfile apps/frontend-webapp
	podman build -t grindx-api-sqlserver:$(V) -t grindx-api-sqlserver:latest -f apps/api-sqlserver/Dockerfile apps/api-sqlserver
	podman build -t grindx-api-postgres:$(V) -t grindx-api-postgres:latest -f apps/api-postgres/Dockerfile apps/api-postgres
	@echo "Imagens criadas: grindx-*:$(V) e grindx-*:latest"
	@echo "Exportando para $(IMG_DIR)..."
ifeq ($(OS),Windows_NT)
	if not exist "$(IMG_DIR)" mkdir "$(IMG_DIR)"
else
	mkdir -p "$(IMG_DIR)"
endif
	podman save -o "$(IMG_DIR)/grindx-frontend-$(V).tar" localhost/grindx-frontend:$(V)
	podman save -o "$(IMG_DIR)/grindx-api-sqlserver-$(V).tar" localhost/grindx-api-sqlserver:$(V)
	podman save -o "$(IMG_DIR)/grindx-api-postgres-$(V).tar" localhost/grindx-api-postgres:$(V)
	@echo "Exportacao concluida: $(IMG_DIR)/grindx-*-$(V).tar"

# ==========================================
# Deploy (exportar configs para diretório)
# ==========================================

deploy:
	@echo "Exportando configs para ~/Apps/GrindX/..."
	mkdir -p ~/Apps/GrindX/apps/api-postgres/uploads
	cp compose.yaml ~/Apps/GrindX/
	cp Makefile ~/Apps/GrindX/
	cp apps/api-postgres/.env.example ~/Apps/GrindX/.env.postgres.example
	cp apps/api-sqlserver/.env.example ~/Apps/GrindX/.env.sqlserver.example
	test -f .env.postgres && cp .env.postgres ~/Apps/GrindX/ || true
	test -f .env.sqlserver && cp .env.sqlserver ~/Apps/GrindX/ || true
	cp apps/frontend-webapp/nginx.conf ~/Apps/GrindX/apps/frontend-webapp/nginx.conf
	@echo "Configs exportadas para ~/Apps/GrindX/"
	@echo "Proximo passo:"
	@echo "  cd ~/Apps/GrindX"
	@echo "  make volumes  (cria diretorios de volumes)"
	@echo "  # Carregar as imagens (geradas por 'make images' na origem):"
	@echo "  podman load -i ~/Containers/images/grindx-frontend-*.tar"
	@echo "  podman load -i ~/Containers/images/grindx-api-sqlserver-*.tar"
	@echo "  podman load -i ~/Containers/images/grindx-api-postgres-*.tar"
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
