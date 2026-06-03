# Roadmap: GrindX — Technical Concerns Remediation

## Overview

Eliminate all technical concerns from CONCERNS.md through three phases: first harden security (SECRET_KEY entropy, temp passwords, rate limiting, upload validation, CORS), then establish infrastructure quality (test coverage, migration cleanup, schema validation), and finally add performance resilience (caching, indexing, health checks). Each phase is independently deployable with measurable success criteria.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Security Hardening** - Patch all security vulnerabilities (SECRET_KEY, temp passwords, rate limiting, uploads, CORS)
- [ ] **Phase 2: Infrastructure & Quality** - Establish test coverage tracking, consolidate migrations, validate test infrastructure
- [ ] **Phase 3: Performance & Resilience** - Add caching layer, database indexing strategy, and deep health checks

## Phase Details

### Phase 1: Security Hardening
**Goal**: All security vulnerabilities are patched and the application resists common attack vectors
**Depends on**: Nothing (first phase)
**Requirements**: SEC-01, SEC-02, SEC-03, SEC-04, SEC-05
**Success Criteria** (what must be TRUE):
  1. SECRET_KEY rejects any key with Shannon entropy below 3.5 bits/character (unit test validates rejection of low-entropy keys)
  2. Temporary passwords expire after 15 minutes and are generated via `secrets` module (test validates expired password is rejected)
  3. Rate limiter blocks requests by authenticated user_id after threshold, not just by IP (integration test with two users from same IP both get limited independently)
  4. File uploads reject files whose magic bytes don't match the declared type (test uploads a .txt renamed to .png and gets HTTP 400)
  5. CORS in production mode rejects requests from unlisted origins (test validates `Origin: evil.com` returns no CORS headers)
**Plans**: TBD

Plans:
- [ ] 01-01: TBD
- [ ] 01-02: TBD
- [ ] 01-03: TBD

### Phase 2: Infrastructure & Quality
**Goal**: Test coverage is measurable, migrations are clean, and test infrastructure accurately reflects production schemas
**Depends on**: Phase 1
**Requirements**: INFRA-01, INFRA-02, INFRA-03
**Success Criteria** (what must be TRUE):
  1. `pytest --cov --cov-fail-under=70` runs successfully and fails the build if coverage drops below 70% (CI pipeline enforces this)
  2. `alembic heads` returns exactly one head with no migration conflicts (no duplicate `001_*` prefixes)
  3. Schema translate map validation test passes, confirming all PostgreSQL schemas (`iam`, `portal`, `catalogo`, `org`) are mapped in `_SCHEMA_TRANSLATE`
**Plans**: TBD

Plans:
- [ ] 02-01: TBD
- [ ] 02-02: TBD
- [ ] 02-03: TBD

### Phase 3: Performance & Resilience
**Goal**: Application responds quickly under load and reports accurate health status for container orchestration
**Depends on**: Phase 2
**Requirements**: PERF-01, PERF-02, PERF-03
**Success Criteria** (what must be TRUE):
  1. Cached queries (active themes, company config) return from cache on second request within TTL — test validates cache hit rate and expiry behavior
  2. Database queries for common patterns (user lookup, theme listing) use indexes — Alembic migration creates composite/functional indexes and EXPLAIN shows index scan
  3. Health endpoint returns HTTP 200 with `{"status": "healthy"}` when DB is reachable, and HTTP 503 with `{"status": "degraded", "details": ...}` when DB is unreachable (test simulates both scenarios)
**Plans**: TBD

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD
- [ ] 03-03: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Security Hardening | 0/3 | Not started | - |
| 2. Infrastructure & Quality | 0/3 | Not started | - |
| 3. Performance & Resilience | 0/3 | Not started | - |
