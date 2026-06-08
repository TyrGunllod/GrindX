---
status: diagnosed
phase: 03-performance-resilience
source: 03-01-SUMMARY.md, 03-02-SUMMARY.md, 03-03-SUMMARY.md
started: 2026-06-06T22:30:00Z
updated: 2026-06-08T23:15:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Theme cache hit
expected: Second request to GET /v1/themes/active returns faster (from cache). Cache TTL is 15 minutes.
result: pass

### 2. User cache hit
expected: Second request to GET /v1/usuarios/{id} returns from cache. Cache invalidates on user update.
result: pass

### 3. Portal menu cache
expected: Second request to GET /v1/portal/menu returns from cache. Cache invalidates on aba create/update/delete.
result: pass

### 4. Database indexes created
expected: Alembic migration 006_add_performance_indexes.py creates 5 indexes (company_themes composite, usuarios role/ativo/empresa_id, portal_modulos aba_id).
result: pass

### 5. Health check - healthy
expected: GET /health returns HTTP 200 with {"status": "healthy", "database": {"postgres": "connected", "sqlserver": "connected"}}
result: pass

### 6. Health check - degraded
expected: When DB is unreachable, GET /health returns HTTP 503 with {"status": "degraded", "details": {...}}
result: issue
reported: "no, it lock on loading"
severity: major

### 7. Health check - schema validation
expected: Health check verifies critical tables exist (usuarios, company_themes, portal_abas, empresas).
result: pass

## Summary

total: 7
passed: 5
issues: 1
pending: 0
skipped: 0

## Gaps

- truth: "When DB is unreachable, GET /health returns HTTP 503 with degraded status"
  status: failed
  reason: "User reported: no, it lock on loading"
  severity: major
  test: 6
  root_cause: "Missing connect_timeout in SQLAlchemy engine. psycopg default connect_timeout=0 means infinite wait on unreachable host."
  artifacts:
    - path: "apps/api-postgres/app/database.py"
      issue: "Missing connect_args={'connect_timeout': 5} in _engine_kwargs"
  missing:
    - "Add connect_args={'connect_timeout': 5} to _engine_kwargs in database.py"
  debug_session: ".planning/debug/health-check-hang.md"
