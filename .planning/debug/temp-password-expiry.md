---
status: diagnosed
trigger: "Diagnose why temporary passwords are not expiring after 15 minutes in the GrindX API."
created: 2026-06-06T00:00:00Z
updated: 2026-06-06T00:00:00Z
---

## Current Focus

hypothesis: "expires_at is None when retrieved from DB during autenticar(), causing the expiry check to be skipped entirely"
test: "Read code flow to trace how expires_at is set, persisted, and retrieved"
expecting: "If expires_at is None at line 71, the entire expiry block is skipped and temp password is accepted regardless of age"
next_action: "Present diagnosis"

## Symptoms

expected: "Login with temp password after 15 minutes should be rejected with 'Senha temporária expirada'"
actual: "Login with temp password after 27 minutes still works"
errors: "No error raised — login succeeds when it should fail"
reproduction: "Generate temp password via forgot_password, wait 15+ minutes, attempt login with temp password"
started: "After temp password feature was implemented"

## Eliminated

- hypothesis: "autenticar() doesn't check expires_at at all"
  evidence: "Code at lines 68-84 DOES check expires_at. The check is present and logically correct."
  timestamp: 2026-06-06T00:00:00Z

- hypothesis: "Timezone-aware vs naive datetime comparison fails silently"
  evidence: "Code handles this at lines 72-74 with explicit tzinfo check and replace(). Comparison logic is correct."
  timestamp: 2026-06-06T00:00:00Z

- hypothesis: "forgot_password() doesn't set expires_at"
  evidence: "Line 201: usuario.expires_at = datetime.now(timezone.utc) + timedelta(minutes=15). It IS set."
  timestamp: 2026-06-06T00:00:00Z

## Evidence

- timestamp: 2026-06-06T00:00:00Z
  checked: "apps/api-postgres/app/auth/service.py autenticar() method"
  found: "Expiry check exists at lines 68-84. Logic: if expires_at is not None → handle timezone → compare with now → reject if expired. If expires_at IS None → skip entire block → accept temp password."
  implication: "The ONLY way temp password is accepted without expiry check is if expires_at is None at line 71"

- timestamp: 2026-06-06T00:00:00Z
  checked: "apps/api-postgres/app/auth/service.py forgot_password() method"
  found: "expires_at is set correctly: datetime.now(timezone.utc) + timedelta(minutes=15). Persisted via atualizar() with both temp_password_hash and expires_at in the update dict."
  implication: "expires_at IS being set and persisted. The atualizar() method does setattr + commit + refresh."

- timestamp: 2026-06-06T00:00:00Z
  checked: "UAT context: 'expires_at column was added manually to the database (not via migration)'"
  found: "Migration 2026_06_02_add_temp_password_fields.py defines the column with sa.DateTime(timezone=True). But UAT says column was added manually."
  implication: "CRITICAL: If column was added manually as TIMESTAMP WITHOUT TIME ZONE, the value stored by datetime.now(timezone.utc) may lose timezone info. More importantly — if the manual ALTER TABLE had any issue, the column might not exist or have wrong type."

- timestamp: 2026-06-06T00:00:00Z
  checked: "apps/api-postgres/app/modules/iam/models/usuario.py model definition"
  found: "expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)"
  implication: "Model declares nullable=True. If column doesn't exist in DB or value isn't persisted, SQLAlchemy returns None. The check 'if expires_at is not None' at line 71 would skip the entire expiry logic."

- timestamp: 2026-06-06T00:00:00Z
  checked: "apps/api-postgres/tests/test_auth_security.py test_expired_temp_password_rejected"
  found: "Test sets expires_at manually on the object and commits. Tests pass in SQLite. But tests don't verify PostgreSQL behavior."
  implication: "Tests pass because they use SQLite in-memory. The bug only manifests in PostgreSQL."

## Resolution

root_cause: "expires_at is None when retrieved from the database during autenticar(), causing the expiry check at line 71 to be skipped entirely. The guard `if expires_at is not None` evaluates to False, so the temp password is accepted regardless of how much time has passed. Root cause: the expires_at column was added manually to the database (not via migration), and either (a) the column doesn't actually exist in the PostgreSQL schema, (b) the column has wrong type causing SQLAlchemy to return None, or (c) the value is not being persisted due to a silent failure. The fix is to ensure the Alembic migration is actually applied to the production database, OR add a defensive check that treats expires_at=None as expired (fail-closed instead of fail-open)."
fix: "Two-part fix: (1) Apply the migration `alembic upgrade head` to ensure the column exists with correct type. (2) Change the defensive logic in autenticar() to fail-closed: if temp_password_hash exists but expires_at is None, treat it as expired and reject."
verification: ""
files_changed: []
