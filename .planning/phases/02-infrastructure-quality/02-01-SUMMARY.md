---
phase: 02-infrastructure-quality
plan: 01
subsystem: database
tags: [alembic, postgresql, migrations, schema-org]

# Dependency graph
requires:
  - phase: 01-security-hardening
    provides: "temp_password migration (a1b2c3d4e5f6) as chain head for down_revision"
provides:
  - "Linear Alembic migration chain with single head (b2c3d4e5f6a7)"
  - "Org schema tables (projetos, recursos, tarefas, registros_tarefas) in canonical chain"
affects: [02-infrastructure-quality, future-migrations]

# Tech tracking
tech-stack:
  added: []
  patterns: [consolidated-migration, schema-creation-guard]

key-files:
  created:
    - apps/api-postgres/alembic/versions/02_add_org_schema_tables.py
  modified: []

key-decisions:
  - "Added ondelete='SET NULL' to projetos.gerente_id FK (fix from orphan migration)"
  - "Added CREATE SCHEMA IF NOT EXISTS org guard before table creation"

patterns-established:
  - "Schema creation guard: always use CREATE SCHEMA IF NOT EXISTS before create_table in schema-specific migrations"

requirements-completed: [INFRA-02]

# Metrics
duration: 3min
completed: 2026-06-03
---

# Phase 2 Plan 1: Consolidate Alembic Migrations Summary

**Org schema tables consolidated into canonical Alembic chain, eliminating 2 orphan migrations that produced multiple heads**

## Performance

- **Duration:** 3 min
- **Started:** 2026-06-03T02:45:45Z
- **Completed:** 2026-06-03T02:48:45Z
- **Tasks:** 1
- **Files modified:** 3

## Accomplishments
- Removed orphan migrations `001_create_tables.py` and `0001_criar_tabela_projetos.py` that caused `alembic heads` to return 3 heads
- Created consolidated migration `02_add_org_schema_tables.py` with all 4 org schema tables
- Verified linear migration chain: `b2c3d4e5f6a7` → `a1b2c3d4e5f6` → ... → `001_initial_schema`
- Fixed missing `ondelete="SET NULL"` on `projetos.gerente_id` foreign key constraint

## Task Commits

Each task was committed atomically:

1. **Task 1: Delete orphan migrations and create consolidated migration** - `2fd5e73` (fix)

## Files Created/Modified
- `apps/api-postgres/alembic/versions/02_add_org_schema_tables.py` - Consolidated migration for org schema (projetos, recursos, tarefas, registros_tarefas)
- `apps/api-postgres/alembic/versions/001_create_tables.py` - DELETED (orphan migration)
- `apps/api-postgres/alembic/versions/0001_criar_tabela_projetos.py` - DELETED (orphan migration)

## Decisions Made
- Added `ondelete="SET NULL"` to `projetos.gerente_id` FK — the orphan `001_create_tables.py` lacked this constraint while `0001_criar_tabela_projetos.py` had it. Used the correct version per plan specification.
- Added `CREATE SCHEMA IF NOT EXISTS org` guard before table creation to ensure schema exists in fresh database deployments.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed missing ondelete on projetos.gerente_id FK**
- **Found during:** Task 1 (consolidated migration creation)
- **Issue:** `001_create_tables.py` had `ForeignKeyConstraint(["gerente_id"], ["iam.usuarios.id"])` without `ondelete="SET NULL"`, while the plan explicitly requires it and `0001_criar_tabela_projetos.py` had the correct constraint
- **Fix:** Added `ondelete="SET NULL"` to the consolidated migration's projetos table definition
- **Files modified:** `apps/api-postgres/alembic/versions/02_add_org_schema_tables.py`
- **Verification:** Revision ID and FK constraint verified in file content
- **Committed in:** `2fd5e73` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Fix ensures referential integrity on project manager deletion. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all tables fully defined with columns, constraints, and indexes.

## Threat Flags
None - no new security surface introduced (database schema only).

## Next Phase Readiness
- Alembic chain is clean and linear, ready for future migrations
- Org schema tables (projetos, recursos, tarefas, registros_tarefas) available in canonical chain
- `alembic check` reports database not up to date (expected — tables not yet applied to DB)

## Self-Check: PASSED

- [x] `02_add_org_schema_tables.py` exists
- [x] `001_create_tables.py` deleted (confirmed not found)
- [x] `0001_criar_tabela_projetos.py` deleted (confirmed not found)
- [x] `02-01-SUMMARY.md` created
- [x] Commit `2fd5e73` exists in git log

---
*Phase: 02-infrastructure-quality*
*Completed: 2026-06-03*
