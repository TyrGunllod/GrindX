# Reestruturação packages/ → apps/ — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mover `packages/api-postgres`, `packages/api-sqlserver` e `packages/frontend-webapp` para uma nova pasta `apps/`, separando aplicações de bibliotecas compartilhadas.

**Architecture:** Reorganiza o monorepo em dois top-levels: `apps/` (apps executáveis) e `packages/` (bibliotecas compartilhadas). Todos os arquivos de configuração, CI, containers e scripts que referenciam caminhos relativos precisam ser atualizados.

**Tech Stack:** FastAPI, PostgreSQL, SQL Server, Podman, GitHub Actions, Pytest, Ruff, python-semantic-release

**NOTA:** Não existe Jenkinsfile no repo — CI roda exclusivamente via GitHub Actions (`.github/workflows/release.yml`).

---

## Arquivos Impactados (14 arquivos + 3 moves)

| Arquivo | Mudança | Crítico para CI? |
|---------|---------|-----------------|
| `packages/api-postgres/` → `apps/api-postgres/` | Move inteiro | — |
| `packages/api-sqlserver/` → `apps/api-sqlserver/` | Move inteiro | — |
| `packages/frontend-webapp/` → `apps/frontend-webapp/` | Move inteiro | — |
| `podman-compose.yml` | Atualiza context e env_file | Containers |
| `Makefile` | Atualiza paths e PYTHONPATH | Dev local |
| `.github/workflows/release.yml` | Atualiza working-directory, cache, PYTHONPATH, lint paths | **CI quebra** |
| `Jenkinsfile` | **Novo arquivo** — pipeline Jenkins espelhando GitHub Actions | **Jenkins CI** |
| `pyproject.toml` | Atualiza `version_variable` paths | **Release quebra** |
| `pytest.ini` | Adiciona `apps` a `testpaths` | Testes |
| `tests/integration/test_pacotes.py` | Atualiza `_packages_dir` e asserts | Testes |
| `apps/api-postgres/scripts/import_module.py` | Atualiza `"packages"` → `"apps"` nos paths | Import system |
| `AGENTS.md` | Atualiza exemplos de caminhos | Docs |
| `docs/MAPA-ARQUIVOS.md` | Atualiza estrutura | Docs |
| `docs/SETUP.md` | Atualiza paths | Docs |
| `docs/README.md`, `docs/API.md`, `docs/DATABASE.md`, `docs/GRINDX-RESUMO.md` | Atualiza data e paths | Docs |

**NOTA:** Containerfiles NÃO precisam de alteração — usam `COPY . .` relativo ao build context.

---

## Pré-requisitos

- Python 3.12+
- Git
- O repo está limpo (sem alterações não commitadas)

---

### Task 1: Criar pasta apps/ e mover diretórios

**Files:**
- Move: `packages/api-postgres/` → `apps/api-postgres/`
- Move: `packages/api-sqlserver/` → `apps/api-sqlserver/`
- Move: `packages/frontend-webapp/` → `apps/frontend-webapp/`

- [ ] **Step 1: Criar pasta apps/ e mover os diretórios**

```powershell
cd D:\_Projetos\GrindX
mkdir apps
move packages\api-postgres apps\
move packages\api-sqlserver apps\
move packages\frontend-webapp apps\
```

- [ ] **Step 2: Verificar estrutura**

```powershell
dir apps\
dir packages\
```

Expected:
```
apps/
  api-postgres/
  api-sqlserver/
  frontend-webapp/
packages/
  shared/
```

- [ ] **Step 3: Commit**

```powershell
git add apps/ packages/
git commit -m "refactor: move api-postgres, api-sqlserver, frontend-webapp to apps/"
```

---

### Task 2: Atualizar podman-compose.yml

**Files:**
- Modify: `podman-compose.yml`

- [ ] **Step 1: Atualizar paths no podman-compose.yml**

Troque 4 referências de `packages/` para `apps/` (o volume `packages/shared` NÃO muda):

```yaml
# Antes:
    build:
      context: ./packages/api-sqlserver
    env_file: ./packages/api-sqlserver/.env
# Depois:
    build:
      context: ./apps/api-sqlserver
    env_file: ./apps/api-sqlserver/.env
```

```yaml
# Antes:
    build:
      context: ./packages/api-postgres
    env_file: ./packages/api-postgres/.env
# Depois:
    build:
      context: ./apps/api-postgres
    env_file: ./apps/api-postgres/.env
```

O volume `./packages/shared:/app/shared:z` fica igual.

- [ ] **Step 2: Commit**

```powershell
git add podman-compose.yml
git commit -m "refactor: update podman-compose paths from packages/ to apps/"
```

---

### Task 3: Atualizar Makefile

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Atualizar target dev-postgres**

```makefile
# Antes:
dev-postgres:
	@echo "Iniciando API Postgres na porta 8002..."
	cd packages/api-postgres && set PYTHONPATH=..&& .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

# Depois:
dev-postgres:
	@echo "Iniciando API Postgres na porta 8002..."
	cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

- [ ] **Step 2: Atualizar target dev-sqlserver**

```makefile
# Antes:
dev-sqlserver:
	@echo "Iniciando API SQL Server na porta 8001..."
	cd packages/api-sqlserver && set PYTHONPATH=..&& .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Depois:
dev-sqlserver:
	@echo "Iniciando API SQL Server na porta 8001..."
	cd apps/api-sqlserver && set PYTHONPATH=..\..\packages&& .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

- [ ] **Step 3: Atualizar target dev-frontend**

```makefile
# Antes:
dev-frontend:
	@echo "Iniciando Frontend na porta 5500 (acessivel na rede)..."
	python -m http.server 5500 --directory packages/frontend-webapp --bind 0.0.0.0

# Depois:
dev-frontend:
	@echo "Iniciando Frontend na porta 5500 (acessivel na rede)..."
	python -m http.server 5500 --directory apps/frontend-webapp --bind 0.0.0.0
```

- [ ] **Step 4: Atualizar target dev-all**

```makefile
# Antes:
dev-all:
	@echo "Subindo todos os servicos GrindX..."
	pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd packages/api-postgres; $$env:PYTHONPATH=(Get-Item ..).FullName; .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002'"
#	pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd packages/api-sqlserver; $$env:PYTHONPATH=(Get-Item ..).FullName; .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001'"
	pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'python -m http.server 5500 --directory packages/frontend-webapp --bind 0.0.0.0'"
	@echo Acesse: http://localhost:5500

# Depois:
dev-all:
	@echo "Subindo todos os servicos GrindX..."
	pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd apps/api-postgres; $$env:PYTHONPATH=(Get-Item ..\..\packages).FullName; .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002'"
#	pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd apps/api-sqlserver; $$env:PYTHONPATH=(Get-Item ..\..\packages).FullName; .\\.venv\\Scripts\\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001'"
	pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'python -m http.server 5500 --directory apps/frontend-webapp --bind 0.0.0.0'"
	@echo Acesse: http://localhost:5500
```

- [ ] **Step 5: Atualizar targets migrate e seed**

```makefile
# Antes:
migrate:
	@echo "Rodando migrações no PostgreSQL..."
	cd packages/api-postgres && set PYTHONPATH=..&& .\\.venv\\Scripts\\python manage_db.py upgrade head

seed:
	@echo "Populando banco de dados inicial..."
	cd packages/api-postgres && set PYTHONPATH=..&& .\\.venv\\Scripts\\python seed.py

# Depois:
migrate:
	@echo "Rodando migrações no PostgreSQL..."
	cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .\\.venv\\Scripts\\python manage_db.py upgrade head

seed:
	@echo "Populando banco de dados inicial..."
	cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .\\.venv\\Scripts\\python seed.py
```

- [ ] **Step 6: Atualizar targets de teste**

```makefile
# Antes:
test-postgres:
	@echo "Executando testes da API Postgres..."
	cd packages/api-postgres && set PYTHONPATH=..&& .\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short

test-sqlserver:
	@echo "Executando testes da API SQL Server..."
	cd packages/api-sqlserver && set PYTHONPATH=..&& .\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short

test-root:
	@echo "Executando testes da raiz do monorepo..."
	set PYTHONPATH=packages\\api-postgres;packages\\api-sqlserver;packages&& .\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short

# Depois:
test-postgres:
	@echo "Executando testes da API Postgres..."
	cd apps/api-postgres && set PYTHONPATH=..\..\packages&& .\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short

test-sqlserver:
	@echo "Executando testes da API SQL Server..."
	cd apps/api-sqlserver && set PYTHONPATH=..\..\packages&& .\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short

test-root:
	@echo "Executando testes da raiz do monorepo..."
	set PYTHONPATH=apps\\api-postgres;apps\\api-sqlserver;packages&& .\\.venv\\Scripts\\python -m pytest tests/ -v --tb=short
```

O target `test-shared` NÃO muda (shared continua em `packages/`).

- [ ] **Step 7: Commit**

```powershell
git add Makefile
git commit -m "refactor: update Makefile paths from packages/ to apps/"
```

---

### Task 4: Atualizar pyproject.toml (semantic-release)

**Files:**
- Modify: `pyproject.toml`

**⚠️ CRÍTICO:** O `python-semantic-release` usa `version_variable` para incrementar versão automaticamente. Se os paths não forem atualizados, o release quebra.

- [ ] **Step 1: Atualizar version_variable**

```toml
# Antes:
[tool.semantic_release]
version_variable = [
    "packages/api-postgres/app/core/config.py:APP_VERSION",
    "packages/api-sqlserver/app/core/config.py:APP_VERSION",
]

# Depois:
[tool.semantic_release]
version_variable = [
    "apps/api-postgres/app/core/config.py:APP_VERSION",
    "apps/api-sqlserver/app/core/config.py:APP_VERSION",
]
```

- [ ] **Step 2: Commit**

```powershell
git add pyproject.toml
git commit -m "refactor: update semantic-release version_variable paths"
```

---

### Task 5: Atualizar GitHub Actions workflow

**Files:**
- Modify: `.github/workflows/release.yml`

**⚠️ CRÍTICO:** O CI quebra se os paths não forem atualizados. São 13 referências a `packages/` que precisam mudar para `apps/`.

- [ ] **Step 1: Atualizar job test-api-postgres**

```yaml
      - name: Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: apps/api-postgres/requirements.txt    # antes: packages/

      - name: Instalar dependências
        working-directory: apps/api-postgres                            # antes: packages/
        run: pip install -r requirements.txt

      - name: Rodar testes
        working-directory: apps/api-postgres                            # antes: packages/
        env:
          PYTHONPATH: ${{ github.workspace }}/packages                  # NÃO MUDA — shared fica em packages/
        run: pytest tests/ -v --tb=short --strict-markers
```

- [ ] **Step 2: Atualizar job test-api-sqlserver**

```yaml
      - name: Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: apps/api-sqlserver/requirements.txt    # antes: packages/

      - name: Instalar dependências Python
        working-directory: apps/api-sqlserver                            # antes: packages/
        run: pip install -r requirements.txt

      - name: Rodar testes
        working-directory: apps/api-sqlserver                            # antes: packages/
        env:
          PYTHONPATH: ${{ github.workspace }}/packages                  # NÃO MUDA
        run: pytest tests/ -v --tb=short --strict-markers
```

- [ ] **Step 3: Atualizar job test-root**

```yaml
      - name: Instalar dependências de todos os pacotes
        run: |
          pip install -r apps/api-postgres/requirements.txt              # antes: packages/
          pip install -r apps/api-sqlserver/requirements.txt             # antes: packages/

      - name: Rodar testes da raiz
        env:
          PYTHONPATH: ${{ github.workspace }}/packages:${{ github.workspace }}/apps/api-postgres:${{ github.workspace }}/apps/api-sqlserver
        run: pytest tests/ -v --tb=short --strict-markers
```

- [ ] **Step 4: Atualizar job lint**

```yaml
      - name: Check
        run: ruff check packages/ apps/ --select E,F,I --ignore E501     # adiciona apps/

      - name: Format check
        run: ruff format packages/ apps/ --check                         # adiciona apps/
```

- [ ] **Step 5: Commit**

```powershell
git add .github/workflows/release.yml
git commit -m "refactor: update CI workflow paths from packages/ to apps/"
```

---

### Task 6: Criar Jenkinsfile

**Files:**
- Create: `Jenkinsfile`

**NOTA:** O Jenkinsfile é um **novo arquivo** — o repo nunca teve um. Ele espelha a pipeline do GitHub Actions (testes + lint) para rodar em servidor Jenkins.

- [ ] **Step 1: Criar o Jenkinsfile na raiz**

```groovy
pipeline {
    agent any

    environment {
        // Variáveis para testes (SQLite in-memory, sem PostgreSQL real)
        DATABASE_URL = 'sqlite:///:memory:'
        DB_URL_OVERRIDE = 'sqlite:///:memory:'
        SECRET_KEY = 'test-secret-key-for-unit-tests-only-change-in-production'
        ACCESS_TOKEN_EXPIRE_MINUTES = '30'
        REFRESH_TOKEN_EXPIRE_DAYS = '7'
        APP_NAME = 'GrindX'
        APP_VERSION = '0.1.0'
        DEBUG = 'false'
        LOG_LEVEL = 'INFO'
        CORS_ORIGINS = '["*"]'
        RATE_LIMIT_REQUESTS = '100'
        RATE_LIMIT_WINDOW_SECONDS = '60'
    }

    stages {
        stage('Setup') {
            steps {
                sh 'python3 --version'
                sh 'pip3 install ruff>=0.3.0'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip3 install -r apps/api-postgres/requirements.txt'
                sh 'pip3 install -r apps/api-sqlserver/requirements.txt'
            }
        }

        stage('Lint') {
            steps {
                sh 'ruff check apps/ packages/ --select E,F,I --ignore E501'
                sh 'ruff format packages/ apps/ --check'
            }
        }

        stage('Test API Postgres') {
            steps {
                dir('apps/api-postgres') {
                    sh 'PYTHONPATH=../../packages python3 -m pytest tests/ -v --tb=short --strict-markers'
                }
            }
        }

        stage('Test API SQL Server') {
            steps {
                dir('apps/api-sqlserver') {
                    sh 'PYTHONPATH=../../packages python3 -m pytest tests/ -v --tb=short --strict-markers'
                }
            }
        }

        stage('Test Shared') {
            steps {
                dir('packages/shared') {
                    sh 'PYTHONPATH=.. python3 -m pytest tests/ -v --tb=short --strict-markers'
                }
            }
        }

        stage('Test Root') {
            steps {
                sh 'PYTHONPATH=apps/api-postgres:apps/api-sqlserver:packages python3 -m pytest tests/ -v --tb=short --strict-markers'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline concluída com sucesso!'
        }
        failure {
            echo 'Pipeline falhou. Verificar logs.'
        }
    }
}
```

- [ ] **Step 2: Commit**

```powershell
git add Jenkinsfile
git commit -m "ci: add Jenkinsfile for Jenkins CI pipeline"
```

---

### Task 7: Atualizar pytest.ini

**Files:**
- Modify: `pytest.ini`

- [ ] **Step 1: Adicionar apps ao testpaths**

```ini
# Antes:
[pytest]
testpaths = tests

# Depois:
[pytest]
testpaths = apps packages tests
```

- [ ] **Step 2: Commit**

```powershell
git add pytest.ini
git commit -m "refactor: add apps/ to pytest testpaths"
```

---

### Task 8: Atualizar testes de integração

**Files:**
- Modify: `tests/integration/test_pacotes.py`

- [ ] **Step 1: Atualizar path de referência e imports**

```python
# Antes (linha 13):
_packages_dir = str(Path(__file__).resolve().parent.parent.parent / "packages")
if _packages_dir not in sys.path:
    sys.path.insert(0, _packages_dir)

# Depois:
_root = Path(__file__).resolve().parent.parent.parent
_packages_dir = str(_root / "packages")
_apps_dir = str(_root / "apps")
if _packages_dir not in sys.path:
    sys.path.insert(0, _packages_dir)
if _apps_dir not in sys.path:
    sys.path.insert(0, _apps_dir)
```

- [ ] **Step 2: Atualizar testes que verificam api-postgres e api-sqlserver**

```python
# Antes:
    def test_api_postgres_tests_exist(self):
        tests_dir = Path(_packages_dir) / "api-postgres" / "tests"

    def test_api_sqlserver_tests_exist(self):
        tests_dir = Path(_packages_dir) / "api-sqlserver" / "tests"

# Depois:
    def test_api_postgres_tests_exist(self):
        tests_dir = Path(_apps_dir) / "api-postgres" / "tests"

    def test_api_sqlserver_tests_exist(self):
        tests_dir = Path(_apps_dir) / "api-sqlserver" / "tests"
```

O teste `test_shared_tests_exist` NÃO muda — shared continua em `packages/`.

- [ ] **Step 3: Rodar testes da raiz**

```powershell
cd D:\_Projetos\GrindX
set PYTHONPATH=apps\api-postgres;apps\api-sqlserver;packages
pytest tests/ -v --tb=short
```

Expected: Todos os testes PASS.

- [ ] **Step 4: Commit**

```powershell
git add tests/integration/test_pacotes.py
git commit -m "refactor: update integration tests for apps/ migration"
```

---

### Task 9: Atualizar import_module.py

**Files:**
- Modify: `apps/api-postgres/scripts/import_module.py`

- [ ] **Step 1: Atualizar register_router — path para main.py**

```python
# Antes:
api_dir = _get_monorepo_root() / "packages" / "api-postgres"
main_py = api_dir / "app" / "main.py"

# Depois:
api_dir = _get_monorepo_root() / "apps" / "api-postgres"
main_py = api_dir / "app" / "main.py"
```

- [ ] **Step 2: Atualizar register_alembic_import — path para env.py**

```python
# Antes:
api_dir = _get_monorepo_root() / "packages" / "api-postgres"

# Depois:
api_dir = _get_monorepo_root() / "apps" / "api-postgres"
```

- [ ] **Step 3: Atualizar copy_backend — path de destino**

```python
# Antes:
api_dir = _get_monorepo_root() / "packages" / "api-postgres"

# Depois:
api_dir = _get_monorepo_root() / "apps" / "api-postgres"
```

- [ ] **Step 4: Atualizar copy_frontend — path de destino**

```python
# Antes:
frontend_dir = _get_monorepo_root() / "packages" / "frontend-webapp"

# Depois:
frontend_dir = _get_monorepo_root() / "apps" / "frontend-webapp"
```

- [ ] **Step 5: Atualizar copy_migration — path de destino**

```python
# Antes:
api_dir = _get_monorepo_root() / "packages" / "api-postgres"

# Depois:
api_dir = _get_monorepo_root() / "apps" / "api-postgres"
```

- [ ] **Step 6: Atualizar register_menu — path para api_dir**

```python
# Antes:
api_dir = _get_monorepo_root() / "packages" / "api-postgres"

# Depois:
api_dir = _get_monorepo_root() / "apps" / "api-postgres"
```

- [ ] **Step 7: Atualizar rollback — path de restauração**

```python
# Antes:
api_dir = _get_monorepo_root() / "packages" / "api-postgres"

# Depois:
api_dir = _get_monorepo_root() / "apps" / "api-postgres"
```

- [ ] **Step 8: Commit**

```powershell
git add apps/api-postgres/scripts/import_module.py
git commit -m "refactor: update import_module.py paths for apps/ migration"
```

---

### Task 10: Atualizar AGENTS.md

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Atualizar caminhos de exemplo**

Troque todas as referências de `packages/api-postgres` para `apps/api-postgres`, `packages/api-sqlserver` para `apps/api-sqlserver` e `packages/frontend-webapp` para `apps/frontend-webapp`.

O caminho `packages/shared/` NÃO muda.

- [ ] **Step 2: Commit**

```powershell
git add AGENTS.md
git commit -m "docs: update AGENTS.md paths for apps/ migration"
```

---

### Task 11: Atualizar documentação

**Files:**
- Modify: `docs/MAPA-ARQUIVOS.md`
- Modify: `docs/SETUP.md`
- Modify: `docs/README.md`
- Modify: `docs/API.md`
- Modify: `docs/DATABASE.md`
- Modify: `docs/GRINDX-RESUMO.md`

- [ ] **Step 1: Atualizar MAPA-ARQUIVOS.md**

Troque todas as referências de `packages/api-postgres/` para `apps/api-postgres/`, `packages/api-sqlserver/` para `apps/api-sqlserver/`, `packages/frontend-webapp/` para `apps/frontend-webapp/`. Atualize a data no cabeçalho.

- [ ] **Step 2: Atualizar SETUP.md**

Troque `cd packages/api-postgres` para `cd apps/api-postgres` e `cd packages/api-sqlserver` para `cd apps/api-sqlserver`. Atualize a data.

- [ ] **Step 3: Atualizar docs/README.md**

Troque links de `../packages/api-postgres/` para `../apps/api-postgres/`, etc. Atualize a data.

- [ ] **Step 4: Atualizar docs/API.md**

Atualize a data no cabeçalho.

- [ ] **Step 5: Atualizar docs/DATABASE.md**

Troque `cd packages/api-postgres` para `cd apps/api-postgres`. Atualize a data.

- [ ] **Step 6: Atualizar docs/GRINDX-RESUMO.md**

Troque `packages/frontend-webapp` para `apps/frontend-webapp`. Atualize a data.

- [ ] **Step 7: Commit**

```powershell
git add docs/
git commit -m "docs: update documentation paths for apps/ migration"
```

---

### Task 12: Atualizar README.md raiz

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Atualizar paths no README.md**

Troque:
- `packages/api-postgres/scripts/import_module.py` → `apps/api-postgres/scripts/import_module.py`
- `cd packages/api-postgres` → `cd apps/api-postgres`
- `packages/frontend-webapp` → `apps/frontend-webapp`

Atualize a data no cabeçalho.

- [ ] **Step 2: Commit**

```powershell
git add README.md
git commit -m "docs: update README.md paths for apps/ migration"
```

---

### Task 13: Validação completa

**Files:**
- Nenhum — apenas verificação

- [ ] **Step 1: Verificar que nenhum path antigo persiste**

```powershell
cd D:\_Projetos\GrindX
rg "packages/api-postgres|packages/api-sqlserver|packages/frontend-webapp" --glob "!.git" --glob "!__pycache__" --glob "!.venv" --glob "!*.md"
```

Expected: Nenhum resultado em arquivos de config/código. Resultados em `*.md` são aceitáveis (docs de specs/plans antigas são históricas).

- [ ] **Step 2: Verificar paths em arquivos de config**

```powershell
rg "packages/api-postgres|packages/api-sqlserver|packages/frontend-webapp" --glob "*.yml" --glob "*.toml" --glob "*.ini" --glob "Makefile" --glob "*.py"
```

Expected: Nenhum resultado.

- [ ] **Step 3: Rodar ruff check em todos os pacotes**

```powershell
ruff check apps/ packages/
```

Expected: Sem erros (apenas warnings são aceitáveis).

- [ ] **Step 4: Rodar testes da raiz**

```powershell
cd D:\_Projetos\GrindX
set PYTHONPATH=apps\api-postgres;apps\api-sqlserver;packages
pytest tests/ -v --tb=short
```

Expected: Todos os testes PASS.

- [ ] **Step 5: Rodar testes shared (deve funcionar sem alteração)**

```powershell
cd D:\_Projetos\GrindX\packages\shared
set PYTHONPATH=..
pytest tests/ -v --tb=short
```

Expected: Todos os testes PASS.

- [ ] **Step 6: Verificar que o build dos containers funciona**

```powershell
cd D:\_Projetos\GrindX
podman-compose build
```

Expected: Build conclui sem erros.

- [ ] **Step 7: Verificar que make targets funcionam**

```powershell
cd D:\_Projetos\GrindX
make test-root
```

Expected: Todos os testes PASS.

---

## Checklist de Validação Final

| Verificação | Comando | Esperado |
|-------------|---------|----------|
| Sem referências antigas (config) | `rg "packages/api-" --glob "*.yml" --glob "*.toml" --glob "Makefile"` | 0 resultados |
| Ruff check | `ruff check apps/ packages/` | Sem erros |
| Testes raiz | `pytest tests/` | Todos PASS |
| Testes shared | `cd packages/shared && pytest tests/` | Todos PASS |
| Build containers | `podman-compose build` | Sucesso |
| Makefile | `make test-root` | Todos PASS |

## Arquivos NÃO alterados (confirmado seguro)

| Arquivo | Razão |
|---------|-------|
| `apps/api-postgres/app/core/config.py` | `import_dir_path` usa parent count que não muda |
| `apps/api-postgres/app/main.py` | Usa imports relativos ao pacote |
| `apps/*/Containerfile` | Usam `COPY . .` relativo ao build context |
| `apps/api-postgres/ruff.toml` | Usa paths relativos internos |
| `packages/shared/*` | Não se move |
| `tests/conftest.py` | Não referencia caminhos de pacotes |
