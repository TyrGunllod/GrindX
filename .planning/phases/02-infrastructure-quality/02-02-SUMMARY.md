---
phase: 02-infrastructure-quality
plan: 02
subsystem: testing
tags: [pytest-cov, coverage, ci, github-actions, quality-gates]

# Dependency graph
requires:
  - phase: 01-security-hardening
    provides: "Test infrastructure baseline (pytest, fixtures, conftest)"
provides:
  - "pytest-cov configured with 70% minimum coverage threshold"
  - "CI pipeline enforces coverage on every push to main"
  - "Coverage XML report generated for external tool integration"
affects: [02-infrastructure-quality, ci-pipeline, test-infrastructure]

# Tech tracking
tech-stack:
  added: [pytest-cov>=6.0.0, coverage.py]
  patterns: [coverage-via-addopts, ci-coverage-enforcement]

key-files:
  created: []
  modified:
    - apps/api-postgres/requirements.txt
    - pytest.ini
    - .github/workflows/release.yml

key-decisions:
  - "Usar --cov=app (não --cov=apps/api-postgres/app) pois pytest roda do diretório apps/api-postgres/"
  - "Adicionar --cov-report=xml no CI para integração com ferramentas externas (Codecov)"
  - "Não adicionar --cov ao test-shared ou test-root — coverage é api-postgres only por enquanto"

patterns-established:
  - "Coverage via addopts: --cov=app --cov-report=term-missing --cov-fail-under=70 em pytest.ini"
  - "CI coverage: flags idênticas ao pytest.ini + --cov-report=xml para XML output"

requirements-completed: [INFRA-01]

# Metrics
duration: 5min
completed: 2026-06-03
---

# Phase 2 Plan 02: pytest-cov Coverage Enforcement Summary

**pytest-cov 7.1.0 com threshold de 70% mínimo configurado no pytest.ini e enforcement no CI (release.yml)**

## Performance

- **Duration:** 5 min
- **Started:** 2026-06-03T02:45:07Z
- **Completed:** 2026-06-03T02:50:08Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- pytest-cov>=6.0.0 adicionado ao requirements.txt e instalado (v7.1.0)
- pytest.ini addopts configurado com --cov=app --cov-report=term-missing --cov-fail-under=70
- CI workflow (release.yml) atualizado para enforce cobertura mínima de 70% no job test-api-postgres
- Coverage atual medido: 76% (acima do threshold de 70%)

## Task Commits

Each task was committed atomically:

1. **Task 1: Adicionar pytest-cov ao requirements.txt e atualizar pytest.ini** - `42e47df` (test)
2. **Task 2: Atualizar CI workflow (release.yml) para enforce cobertura** - `40c8ba0` (ci)

**Plan metadata:** pending (docs: complete plan)

## Files Created/Modified
- `apps/api-postgres/requirements.txt` - Adicionado pytest-cov>=6.0.0 na seção de testes
- `pytest.ini` - addopts atualizado com flags de cobertura (--cov=app --cov-report=term-missing --cov-fail-under=70)
- `.github/workflows/release.yml` - Step "Rodar testes" do job test-api-postgres atualizado com cobertura + XML report

## Decisions Made
- Usar `--cov=app` (escopo do pacote app, não path absoluto) pois pytest roda de `apps/api-postgres/`
- Adicionar `--cov-report=xml` no CI para geração de coverage.xml (Codecov, etc.)
- Não alterar jobs test-api-sqlserver e test-root — coverage é api-postgres only por enquanto

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- 13 testes falham (pré-existentes, não relacionados à cobertura) — test_import_module.py e test_auth_service.py têm falhas de lógica/mock que serão corrigidas em fases futuras
- Coverage 76% > 70% threshold — configuração funciona corretamente

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- pytest-cov configurado e funcional — pronto para medir cobertura em testes futuros
- CI enforce 70% mínimo — builds falham se cobertura cair abaixo
- Coverage XML gerado para integração com ferramentas externas

---
*Phase: 02-infrastructure-quality*
*Completed: 2026-06-03*

## Self-Check: PASSED

- [x] `apps/api-postgres/requirements.txt` exists
- [x] `pytest.ini` exists
- [x] `.github/workflows/release.yml` exists
- [x] `.planning/phases/02-infrastructure-quality/02-02-SUMMARY.md` exists
- [x] Commit `42e47df` exists (Task 1)
- [x] Commit `40c8ba0` exists (Task 2)
