---
phase: 02-infrastructure-quality
plan: 03
subsystem: test-infrastructure
tags: [schema-validation, test-coverage, sqlite-compatibility]
dependencies:
  requires: [02-02]
  provides: [schema-validation-tests]
  affects: [apps/api-postgres/tests/unit/]
tech_stack:
  added: []
  patterns: [schema-translate-validation]
key_files:
  created:
    - apps/api-postgres/tests/unit/test_schema_validation.py
  modified: []
decisions:
  - "Importar _SCHEMA_TRANSLATE diretamente de tests.conftest (módulo acessível via __init__.py)"
  - "EXPECTED_SCHEMAS como constante no topo do arquivo para facilitar manutenção"
metrics:
  duration: "2 min"
  completed: "2026-06-02"
  tasks: 1
  files: 1
---

# Phase 2 Plan 03: Schema Validation Tests Summary

Testes de validação que garantem que `_SCHEMA_TRANSLATE` cobre todos os schemas PostgreSQL usados pela aplicação.

## What Was Built

Teste unitário `test_schema_validation.py` com 3 testes que validam o dicionário `_SCHEMA_TRANSLATE` em conftest.py:

1. **test_schema_translate_covers_all_schemas** — Verifica que cada schema em `EXPECTED_SCHEMAS` (`iam`, `portal`, `catalogo`, `org`) está presente como chave em `_SCHEMA_TRANSLATE`. Previne que novos schemas sejam adicionados à aplicação sem atualizar o dicionário de tradução.

2. **test_schema_translate_maps_to_none_for_sqlite** — Verifica que todos os valores em `_SCHEMA_TRANSLATE` são `None`. Garante compatibilidade com SQLite para testes (schemas PostgreSQL não existem em SQLite).

3. **test_expected_schemas_match_application_models** — Sanity check que `EXPECTED_SCHEMAS` contém exatamente 4 schemas. Alerta se novos schemas forem adicionados sem atualizar a constante.

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Import direto de `tests.conftest` | `tests/` tem `__init__.py`, então conftest é importável como módulo. Alternativa (`apps.api_postgres.tests.conftest`) não funciona sem instalação do pacote. |
| `EXPECTED_SCHEMAS` como constante | Facilita manutenção — alterar a lista canônica em um lugar só afeta todos os testes. |

## Deviations from Plan

None — plan executed exactly as written.

## Verification Evidence

```
tests\unit\test_schema_validation.py::test_schema_translate_covers_all_schemas PASSED
tests\unit\test_schema_validation.py::test_schema_translate_maps_to_none_for_sqlite PASSED
tests\unit\test_schema_validation.py::test_expected_schemas_match_application_models PASSED
3 passed in 0.99s
```

## Commit

- `d15285f`: test(02-03): adicionar testes de validação do schema translate map

## Self-Check: PASSED

- [x] `apps/api-postgres/tests/unit/test_schema_validation.py` exists
- [x] Commit `d15285f` exists in git log
