# ==========================================
# Módulo {entity_name} — Standalone
# ==========================================

MODULE := {module_name}
ENTITY := {entity_name}

.PHONY: test test-unit test-integration package export dry-run clean help

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
# Empacotamento & Exportação
# ==========================================

package:
	@python -m app.modules.$(MODULE).export package
	@echo.
	@echo Zip gerado: dist/modulo-$(MODULE).zip
	@echo Estrutura:
	@python -c "import zipfile; [print('  ' + f) for f in zipfile.ZipFile('dist/modulo-$(MODULE).zip').namelist()[:10]]"
	@python -c "import zipfile; n=len(zipfile.ZipFile('dist/modulo-$(MODULE).zip').namelist()); print(f'  ... ({n} arquivos total)')"

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
	@python -c "import shutil,os; os.makedirs('../GrindX/import',exist_ok=True); shutil.copy2('dist/modulo-$(MODULE).zip','../GrindX/import/'); print('Copiado para ../GrindX/import/modulo-$(MODULE).zip')"
	@echo.
	@echo Proximo passo: importar via API ou frontend
	@echo   API:  curl -X POST -H "Authorization: Bearer ^<token^>" "http://localhost:8000/v1/import/$(MODULE)?force=true"
	@echo   Frontend: Gestao -> Importar Modulos -> $(ENTITY) -> Importar

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
	@echo   make package          Gera o zip para importacao
	@echo   make dry-run          Simula a geracao do zip
	@echo   make export           Exporta direto para o GrindX (CLI)
	@echo   make import           Gera zip + copia para import/ do GrindX
	@echo   make clean            Limpa caches e __pycache__
	@echo   make help             Exibe esta ajuda
	@echo
