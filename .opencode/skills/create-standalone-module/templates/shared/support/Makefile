# ==========================================
# Módulo {entity_name} — Standalone
# ==========================================

MODULE := {module_name}
ENTITY := {entity_name}

.PHONY: test test-unit test-integration dev-backend dev-frontend package export dry-run import clean version version-dry-run help

# ==========================================
# Testes
# ==========================================

test:
	@python -m pytest app/modules/$(MODULE)/tests/ -v --tb=short

test-unit:
	@python -m pytest app/modules/$(MODULE)/tests/ -v --tb=short -k "unit"

test-integration:
	@python -m pytest app/modules/$(MODULE)/tests/ -v --tb=short -k "integration"

# ==========================================
# Desenvolvimento
# ==========================================

dev-backend:
	@echo "Iniciando API FastAPI (uvicorn)..."
	@cd app/modules/$(MODULE) && cmd /c "set PYTHONPATH=../../..&& uvicorn app.main:app --reload --port 7000"
	@echo "API rodando em http://localhost:7000"

dev-frontend:
	@echo "Iniciando servidor frontend estatico..."
	@cd frontend/{frontend_prefix}_* && python -m http.server 7080
	@echo "Frontend em http://localhost:7080"

# ==========================================
# Empacotamento & Exportação
# ==========================================

package:
	@python -m app.modules.$(MODULE).export package
	@echo.
	@echo Zip gerado: dist/modulo-$(MODULE)-vX.Y.Z.zip (versao do module.json)
	@echo Estrutura:
	@for %%f in (dist/modulo-$(MODULE)-*.zip) do @python -c "import zipfile; [print('  ' + f) for f in zipfile.ZipFile('%%f').namelist()[:10]]"
	@for %%f in (dist/modulo-$(MODULE)-*.zip) do @python -c "import zipfile; n=len(zipfile.ZipFile('%%f').namelist()); print(f'  ... ({n} arquivos total)')"

dry-run:
	@python -m app.modules.$(MODULE).export package --dry-run

export:
	@python -m app.modules.$(MODULE).export

export-dry:
	@python -m app.modules.$(MODULE).export --dry-run

# ==========================================
# Importação
# ==========================================

import: package
	@echo.
	@echo Copiando zip para import/ do GrindX...
	@for %%f in (dist/modulo-$(MODULE)-*.zip) do @python -c "import shutil,os; os.makedirs('../GrindX/import',exist_ok=True); shutil.copy2('%%f','../GrindX/import/'); print('Copiado para ../GrindX/import/' + os.path.basename('%%f'))"
	@echo.
	@echo Proximo passo: importar via API ou frontend
	@echo   API:  curl -X POST -H "Authorization: Bearer ^<token^>" "http://localhost:8000/v1/import/$(MODULE)?force=true"
	@echo   Frontend: Gestao -> Importar Modulos -> $(ENTITY) -> Importar

# ==========================================
# Versionamento (conventional commits)
# ==========================================

version-dry-run:
	@python scripts/version.py --dry-run

version:
	@python scripts/version.py

# ==========================================
# Utilitários
# ==========================================

clean:
	@echo Limpando caches...
	@if exist dist rmdir /s /q dist
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@echo Limpeza concluida

help:
	@echo.
	@echo Modulo $(ENTITY) — Comandos disponibles:
	@echo.
	@echo   make test             Roda todos os testes
	@echo   make test-unit        Roda apenas testes unitarios
	@echo   make test-integration Roda apenas testes de integracao
	@echo   make dev-backend      Inicia API FastAPI (porta 7000)
	@echo   make dev-frontend     Inicia frontend estatico (porta 7080)
	@echo   make package          Gera o zip para importacao
	@echo   make dry-run          Simula a geracao do zip
	@echo   make export           Exporta direto para o GrindX (CLI)
	@echo   make import           Gera zip + copia para import/ do GrindX
	@echo   make version-dry-run  Simula a proxima versao sem alterar arquivos
	@echo   make version          Gera proxima versao + changelog + tag git
	@echo   make clean            Limpa caches e __pycache__
	@echo   make help             Exibe esta ajuda
	@echo
