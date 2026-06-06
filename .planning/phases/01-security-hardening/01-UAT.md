---
status: diagnosed
phase: 01-security-hardening
source: 01-01-SUMMARY.md, 01-02-SUMMARY.md, 01-03-SUMMARY.md
started: 2026-06-02T23:30:00Z
updated: 2026-06-06T19:55:00Z
---

## Current Test

[testing complete]

## Tests

### 1. SECRET_KEY rejects low-entropy keys
expected: App fails to start if SECRET_KEY has low Shannon entropy (e.g., "aaaa..."). Error message mentions "entropia muito baixa" and suggests generating a new key.
result: pass

### 2. SECRET_KEY accepts high-entropy keys
expected: App starts normally with a random key like `secrets.token_hex(32)` (entropy ~3.9 bits/char).
result: pass

### 3. CORS rejects wildcard in production
expected: With ENVIRONMENT=production and CORS_ORIGINS="*", app fails to start with error mentioning "não pode ser '*'".
result: pass

### 4. CORS requires explicit origins in production
expected: With ENVIRONMENT=production and CORS_ORIGINS="", app fails to start with error mentioning "obrigatório em produção".
result: pass

### 5. Rate limiter blocks by IP
expected: Sending more than RATE_LIMIT_REQUESTS requests to an unauthenticated endpoint (e.g., /health) returns HTTP 429 with "RATE_LIMIT_EXCEDIDO" message and Retry-After header.
result: issue
reported: "/health excluded by design — test should use non-excluded endpoint"
severity: minor

### 6. Rate limiter blocks by user_id
expected: Authenticated user making more than RATE_LIMIT_REQUESTS requests gets HTTP 429. Two different users from same IP get independent limits.
result: issue
reported: "coluna usuarios.temp_password_hash não existe — migration not applied to production DB"
severity: major

### 7. Temp password is 16 alphanumeric chars
expected: Calling forgot_password returns a password matching pattern `^[A-Za-z0-9]{16}$`.
result: pass

### 8. Temp password expires after 15 minutes
expected: Login with temp password after 15 minutes returns error "Senha temporária expirada".
result: issue
reported: "nao rejeitou na senha mesmo apos 27 minutos"
severity: major

### 9. File upload rejects mismatched magic bytes
expected: Uploading a .txt file renamed to .png returns HTTP 400 with message about file type mismatch.
result: pass

### 10. File upload accepts valid files
expected: Uploading a real PNG image or TTF font file succeeds without error.
result: pass

## Summary

total: 10
passed: 7
issues: 2
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "Sending more than RATE_LIMIT_REQUESTS requests to an unauthenticated endpoint returns HTTP 429"
  status: failed
  reason: "User tested against /health which is excluded from rate limiting by design (container liveness probe)"
  severity: minor
  test: 5
  root_cause: "/health is in exclude_paths list — test should use non-excluded endpoint like /v1/auth/token"
  artifacts:
    - path: "apps/api-postgres/app/main.py"
      issue: "exclude_paths includes /health (by design)"
  missing:
    - "Test rate limiting on non-excluded endpoint"

- truth: "Authenticated user making more than RATE_LIMIT_REQUESTS requests gets HTTP 429"
  status: failed
  reason: "User reported: coluna usuarios.temp_password_hash não existe — migration not applied to production DB"
  severity: major
  test: 6
  artifacts: []
  missing: []

- truth: "Alembic migrations run cleanly on production database"
  status: failed
  reason: "User reported: DuplicateTable: relação 'usuarios' já existe — database has tables but Alembic not stamped"
  severity: blocker
  test: 7
  artifacts: []
  missing: []

- truth: "Temp password expires after 15 minutes"
  status: failed
  reason: "User reported: nao rejeitou na senha mesmo apos 27 minutos"
  severity: major
  test: 8
  root_cause: "Fail-open design in autenticar() — if expires_at is None (column added manually without migration), temp password is accepted without expiry check. Guard 'if expires_at is not None' skips entire expiry block when expires_at is None."
  artifacts:
    - path: "apps/api-postgres/app/auth/service.py"
      issue: "Line 71: fail-open guard 'if expires_at is not None' skips expiry check when expires_at is None"
    - path: "apps/api-postgres/app/modules/iam/models/usuario.py"
      issue: "nullable=True allows None values for expires_at"
  missing:
    - "Change logic to fail-closed: reject temp password if expires_at is None"
    - "Apply Alembic migration to ensure column has correct type"
