.PHONY: build up down logs test-postgres test-sqlserver test-all lint format clean

# ==========================================
# Build & Run
# ==========================================

build:
	podman-compose build

up:
	podman-compose up -d

down:
	podman-compose down

restart:
	podman-compose down && podman-compose up -d

logs:
	podman-compose logs -f

logs-postgres:
	podman-compose logs -f api-postgres

logs-sqlserver:
	podman-compose logs -f api-sqlserver

# ==========================================
# Testes
# ==========================================

test-postgres:
	cd packages/api-postgres && python -m pytest tests/ -v --tb=short

test-postgres-unit:
	cd packages/api-postgres && python -m pytest tests/unit/ -v --tb=short

test-postgres-integration:
	cd packages/api-postgres && python -m pytest tests/integration/ -v --tb=short

test-sqlserver:
	cd packages/api-sqlserver && python -m pytest tests/ -v --tb=short

test-sqlserver-unit:
	cd packages/api-sqlserver && python -m pytest tests/unit/ -v --tb=short

test-sqlserver-integration:
	cd packages/api-sqlserver && python -m pytest tests/integration/ -v --tb=short

test-all: test-postgres test-sqlserver

# ==========================================
# Testes em Container
# ==========================================

test-container-postgres:
	podman run --rm -v ./packages/api-postgres:/app:z \
		-v ./packages/shared:/app/shared:z \
		--user 1001:1001 erp/api-postgres:dev \
		python -m pytest tests/ -v --tb=short

test-container-sqlserver:
	podman run --rm -v ./packages/api-sqlserver:/app:z \
		-v ./packages/shared:/app/shared:z \
		--user 1001:1001 erp/api-sqlserver:dev \
		python -m pytest tests/ -v --tb=short

# ==========================================
# Qualidade de Código
# ==========================================

lint:
	cd packages/api-postgres && python -m ruff check app/ tests/
	cd packages/api-sqlserver && python -m ruff check app/ tests/

format:
	cd packages/api-postgres && python -m ruff format app/ tests/
	cd packages/api-sqlserver && python -m ruff format app/ tests/

# ==========================================
# Dev Local
# ==========================================

dev-postgres:
	cd packages/api-postgres && uvicorn app.main:app --reload --port 8002

dev-sqlserver:
	cd packages/api-sqlserver && uvicorn app.main:app --reload --port 8001

# ==========================================
# Limpeza
# ==========================================

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
