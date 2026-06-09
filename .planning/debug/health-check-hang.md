---
status: diagnosed
trigger: "Diagnose why the health check hangs when PostgreSQL is unreachable in the GrindX API"
created: 2026-06-08T00:00:00Z
updated: 2026-06-08T00:00:00Z
---

## Current Focus

hypothesis: No connection timeout configured on SQLAlchemy engine, causing `db.execute(text("SELECT 1"))` to hang indefinitely when PostgreSQL is unreachable
test: Examine engine configuration and PostgreSQL connection parameters
expecting: Confirm missing `connect_timeout` / `connect_args` in engine config
next_action: Check if psycopg2 connect_args are passed, verify default behavior

## Symptoms

expected: GET /health returns 503 with degraded status when DB is unreachable
actual: GET /health hangs indefinitely when DB is unreachable
errors: None (hangs, no exception raised)
reproduction: Stop PostgreSQL, call GET /health
started: Unknown (likely always broken for unreachable DB scenario)

## Eliminated

- hypothesis: pool_timeout=30 should cause timeout
  evidence: pool_timeout controls getting connection FROM pool, not connecting TO database. Connection attempt itself has no timeout.
  timestamp: 2026-06-08T00:01:00Z

## Evidence

- timestamp: 2026-06-08T00:01:00Z
  checked: apps/api-postgres/app/database.py engine configuration
  found: Engine kwargs include pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800, pool_pre_ping=True. NO connect_args or connect_timeout configured.
  implication: TCP connection to PostgreSQL has no timeout, will hang until OS-level TCP timeout (60-120s+)

- timestamp: 2026-06-08T00:02:00Z
  checked: apps/api-postgres/app/routers/health_router.py check_database_health()
  found: Uses `db.execute(text("SELECT 1"))` synchronously. No timeout parameter on execute.
  implication: Blocking call with no timeout protection

- timestamp: 2026-06-08T00:03:00Z
  checked: PostgreSQL psycopg2 connection timeout defaults
  found: Default connect_timeout is 0 (no timeout). Connection attempt hangs indefinitely if server unreachable.
  implication: Need explicit connect_timeout in connect_args or DATABASE_URL

## Resolution

root_cause: Missing connection timeout configuration. SQLAlchemy engine has no `connect_args` with `connect_timeout`, so psycopg uses default of 0 (infinite). When PostgreSQL is unreachable, `db.execute(text("SELECT 1"))` blocks until OS TCP timeout (60-120s+ on Windows/Linux). The `pool_timeout=30` only controls waiting for a connection FROM the pool, not connecting TO the database.

fix: Add connect_args={"connect_timeout": 5} to engine kwargs in database.py. This tells psycopg to timeout connection attempts after 5 seconds.

verification: Pending
files_changed: []
