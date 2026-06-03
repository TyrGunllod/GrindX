# Phase 2: Infrastructure & Quality - Research

**Researched:** 2026-06-02
**Domain:** Test coverage, Alembic migration consolidation, schema validation infrastructure
**Confidence:** HIGH

## Summary

Phase 2 addresses three infrastructure requirements: (1) adding pytest-cov with a 70% minimum coverage threshold enforced in CI, (2) consolidating duplicate Alembic migrations that currently produce multiple heads, and (3) adding a validation test to ensure the `_SCHEMA_TRANSLATE` map covers all PostgreSQL schemas used by the application.

The migration consolidation is the most complex task. There are currently **three independent migration chains** all starting from `down_revision = None`, which causes `alembic heads` to report multiple heads. The canonical chain (`001_initial_schema` → `002` → `003` → `004` → `005` → `a1b2c3d4e5f6`) contains the production schema. Two orphan chains (`001_create_tables` and `0001_criar_tabela_projetos`) create overlapping `org.projetos` tables and must be either removed or merged.

The test coverage task is straightforward: add `pytest-cov` to requirements, configure `--cov-fail-under=70` in `pytest.ini`, and update the CI workflow to run coverage. The schema validation test is a simple unit test that asserts all four schemas (`iam`, `portal`, `catalogo`, `org`) are present in `_SCHEMA_TRANSLATE`.

**Primary recommendation:** Consolidate migrations first (INFRA-02), then add coverage tooling (INFRA-01), then add schema validation test (INFRA-03). This order ensures migration tooling works correctly before measuring coverage.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Test coverage measurement | CI/CD Pipeline | pytest config | Coverage enforcement belongs in CI; pytest-cov is the standard tool |
| Migration management | Database / Alembic | CI/CD Pipeline | Alembic owns migration chain; CI validates `alembic heads` returns single head |
| Schema validation | Test Infrastructure | Database / Alembic | Test validates that test fixtures match production schema configuration |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest-cov | >=6.0.0 | Coverage plugin for pytest | Official pytest plugin, integrates with coverage.py, supports `--cov-fail-under` [CITED: pytest-cov.readthedocs.io] |
| coverage | >=7.0 | Coverage measurement engine | Backend for pytest-cov, installed as dependency [CITED: pytest-cov.readthedocs.io] |
| alembic | 1.18.4 | Already installed — migration management | No upgrade needed [VERIFIED: pip show in project venv] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| coverage[toml] | >=7.0 | TOML config support for coverage.py | If using `pyproject.toml` for coverage config (optional — `.coveragerc` also works) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pytest-cov | coverage run -m pytest | More verbose, same engine but manual integration |
| --cov-fail-under | CI script checking coverage XML | More complex, same result |

**Installation:**
```powershell
# In apps/api-postgres/requirements.txt — add:
pytest-cov>=6.0.0

# Then install:
pip install -r requirements.txt
```

**Version verification:**
```bash
# pytest-cov latest stable: 7.1.0 (per official docs at pytest-cov.readthedocs.io)
# coverage: >=7.0 (transitive dependency of pytest-cov)
```

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| pytest-cov | PyPI | ~12 yrs | Very high | github.com/pytest-dev/pytest-cov | [ASSUMED] | Approved |
| coverage | PyPI | ~20+ yrs | Very high | github.com/nedbat/coveragepy | [ASSUMED] | Approved |

*Note: slopcheck not available at research time. Packages tagged [ASSUMED] based on well-established ecosystem knowledge. pytest-cov is the official pytest coverage plugin maintained under the pytest-dev organization.*

## Architecture Patterns

### Pattern 1: Coverage Configuration via pytest.ini addopts

**What:** Add `--cov` and `--cov-fail-under` to pytest's `addopts` so coverage runs automatically on every test invocation.

**When to use:** When you want coverage enforcement to be the default, not opt-in.

**Example:**
```ini
# pytest.ini
[pytest]
addopts = -v --tb=short --strict-markers --cov=app --cov-fail-under=70
```

**Key decisions:**
- `--cov=app` measures only the `app` package (not tests, not third-party). This is the standard scope.
- `--cov-fail-under=70` fails the build if total coverage drops below 70%.
- Coverage report type: `--cov-report=term-missing` shows uncovered lines in terminal output.

### Pattern 2: Migration Consolidation — Remove Orphan Revisions

**What:** When multiple migration files have `down_revision = None` (multiple roots), Alembic reports multiple heads. The fix is to establish a single linear chain.

**When to use:** When `alembic heads` returns more than one revision.

**Example — Current state:**
```
Chain A (production):
  001_initial_schema (down=None)
    → 002_add_usuario_modulos
      → 003_add_empresa_and_theme
        → 004_add_theme_history
          → 005_add_aba_parent_id
            → a1b2c3d4e5f6 (temp_password)

Chain B (orphan — overlaps with A):
  001_create_tables (down=None) — creates org.projetos, org.recursos, org.tarefas, org.registros_tarefas

Chain C (orphan — overlaps with B):
  0001_criar_tabela_projetos (down=None) — creates org.projetos only
```

**Resolution approach:**
1. Delete `001_create_tables.py` and `0001_criar_tabela_projetos.py` — they are early drafts that overlap with Chain A's `003_add_empresa_and_theme.py` (which creates the `org` schema tables).
2. Verify `alembic heads` returns exactly one head after deletion.
3. If the `org` schema tables (projetos, recursos, tarefas, registros_tarefas) are NOT covered by Chain A, create a single new migration that adds them after the current head.

**Important:** The `003_add_empresa_and_theme.py` migration creates `empresas` and `company_themes` but does NOT create `org.projetos` — the `org` schema tables are only in the orphan files. This means we need to create a new migration at the head of Chain A that creates the `org` tables.

### Anti-Patterns to Avoid

- **Don't rename migration revision IDs:** Changing `revision = "001"` to something else breaks any database already stamped with that revision.
- **Don't use `alembic stamp head` without understanding:** This marks the DB as up-to-date without running migrations — useful for new DBs but dangerous for existing ones.
- **Don't add `--cov` to CI without adding it to local pytest first:** Developers need to see coverage locally before CI enforces it.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Coverage measurement | Custom script parsing test output | pytest-cov + coverage.py | Edge cases (branch coverage, partial, exclusion patterns) handled by battle-tested library |
| Migration chain validation | Script parsing Python files | `alembic heads` command | Alembic already resolves the full DAG — parsing files misses transitive dependencies |
| Schema validation | Manual grep for schema names | pytest test with import-time assertion | Imports fail loudly if schemas change; grep is fragile |

## Common Pitfalls

### Pitfall 1: pytest-cov `--cov` Eating Next Argument
**What goes wrong:** If `--cov` is the last option in `addopts`, it may consume the next CLI argument as its source value.
**Why it happens:** `--cov` takes an optional argument. If it's last, pytest-cov interprets the next positional argument as the source.
**How to avoid:** Use `--cov=app` (with explicit value) or put `--cov=` (blank value for "measure everything") — never bare `--cov` as last option. [CITED: pytest-cov.readthedocs.io/config.html]
**Warning signs:** Coverage reports show 0% or measure the wrong directory.

### Pitfall 2: Coverage Scope in Monorepo
**What goes wrong:** `--cov` measures everything including tests and third-party packages, giving misleading coverage numbers.
**Why it happens:** Default `--cov` (no value) measures all imported code.
**How to avoid:** Use `--cov=app` to scope to the application package only. For the monorepo, each API should measure its own `app` directory.
**Warning signs:** Coverage > 90% without meaningful test coverage (tests themselves counted).

### Pitfall 3: Migration Consolidation on Existing Databases
**What goes wrong:** Deleting migration files that are already stamped in production databases causes `alembic upgrade` to fail.
**Why it happens:** The `alembic_version` table contains the deleted revision ID.
**How to avoid:** Only delete orphan migrations that were never applied to any database. If in doubt, use `alembic stamp` to update the version table after consolidation.
**Warning signs:** `alembic upgrade` reports "Can't locate revision identified by '001'".

### Pitfall 4: PYTHONPATH for Coverage in CI
**What goes wrong:** Coverage reports 0% because imports fail silently (shared package not on path).
**Why it happens:** `PYTHONPATH` not set correctly for coverage subprocess.
**How to avoid:** Ensure CI sets `PYTHONPATH` before running pytest, same as for test execution. The existing CI workflow already does this for test runs — coverage runs inherit the same environment.
**Warning signs:** All tests pass but coverage is 0%.

## Code Examples

### pytest.ini with Coverage [CITED: pytest-cov.readthedocs.io]
```ini
[pytest]
testpaths = apps packages tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers --cov=app --cov-report=term-missing --cov-fail-under=70
markers =
    unit: Testes unitários
    integration: Testes de integração
    slow: Testes lentos
```

**Note:** `--cov=app` scopes coverage to the `app` package. Since pytest runs from `apps/api-postgres/`, this measures `apps/api-postgres/app/`. For root-level tests, coverage needs a different scope or a `.coveragerc` file.

### CI Coverage Step (release.yml)
```yaml
      - name: Rodar testes com cobertura
        working-directory: apps/api-postgres
        env:
          PYTHONPATH: ${{ github.workspace }}/packages
        run: pytest tests/ -v --tb=short --strict-markers --cov=app --cov-report=xml --cov-fail-under=70
```

### Schema Validation Test
```python
"""
Valida que o _SCHEMA_TRANSLATE cobre todos os schemas PostgreSQL usados pela aplicação.
"""
import pytest

# Schemas que a aplicação usa no PostgreSQL
EXPECTED_SCHEMAS = {"iam", "portal", "catalogo", "org"}


def test_schema_translate_covers_all_schemas():
    """Verifica que _SCHEMA_TRANSLATE mapeia todos os schemas PostgreSQL."""
    from apps.api_postgres.tests.conftest import _SCHEMA_TRANSLATE
    
    mapped_schemas = set(_SCHEMA_TRANSLATE.keys())
    
    for schema in EXPECTED_SCHEMAS:
        assert schema in mapped_schemas, (
            f"Schema '{schema}' não está em _SCHEMA_TRANSLATE. "
            f"Adicione '{schema}: None' ao dicionário em conftest.py."
        )


def test_schema_translate_maps_to_none_for_sqlite():
    """Verifica que todos os schemas mapeiam para None (SQLite compatível)."""
    from apps.api_postgres.tests.conftest import _SCHEMA_TRANSLATE
    
    for schema, target in _SCHEMA_TRANSLATE.items():
        assert target is None, (
            f"Schema '{schema}' mapeia para '{target}' em vez de None. "
            f"Para testes com SQLite, todos os schemas devem mapear para None."
        )
```

### Migration Consolidation — New Head Migration
```python
"""Consolidate org schema tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-02

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create org schema tables (projetos, recursos, tarefas, registros_tarefas)."""
    # These tables were previously defined in orphan migrations 001_create_tables
    # and 0001_criar_tabela_projetos. Consolidated here as a single migration.
    op.execute("CREATE SCHEMA IF NOT EXISTS org")
    
    op.create_table(
        "projetos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="planning", nullable=False),
        sa.Column("data_inicio", sa.Date(), nullable=False),
        sa.Column("data_fim", sa.Date(), nullable=False),
        sa.Column("cor", sa.String(length=7), server_default="#3b82f6", nullable=False),
        sa.Column("gerente_id", sa.Integer(), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["gerente_id"], ["iam.usuarios.id"], ondelete="SET NULL"),
        schema="org",
    )
    op.create_index("ix_org_projetos_nome", "projetos", ["nome"], schema="org")
    # ... (recursos, tarefas, registros_tarefas — copy from 001_create_tables.py)


def downgrade() -> None:
    op.drop_table("registros_tarefas", schema="org")
    op.drop_table("tarefas", schema="org")
    op.drop_table("recursos", schema="org")
    op.drop_table("projetos", schema="org")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual coverage checking | pytest-cov with `--cov-fail-under` | Standard since pytest-cov 2.0+ | Automated enforcement, CI gate |
| `coverage run -m pytest` | `pytest --cov` | pytest-cov became standard plugin | Simpler CLI, better integration |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `001_create_tables.py` and `0001_criar_tabela_projetos.py` are orphan migrations never applied to production | Pitfall 3 | If applied to production, deleting them breaks `alembic upgrade` — need `alembic stamp` instead |
| A2 | The `org` schema tables (projetos, recursos, tarefas, registros_tarefas) are NOT in the canonical chain A | Architecture | If they ARE in chain A somewhere, the consolidation approach changes completely |
| A3 | pytest-cov>=6.0.0 is the correct minimum version for the project's Python 3.12 + pytest>=8.0.0 | Standard Stack | Older versions may not support pytest 8.x API |
| A4 | `--cov=app` is the correct coverage scope (not `--cov=apps/api-postgres/app`) | Pitfall 2 | If pytest runs from repo root, `app` won't match — need absolute path |
| A5 | The four schemas `iam`, `portal`, `catalogo`, `org` are the complete set used by the application | Schema Validation | Missing schemas cause test failures in production but not in SQLite tests |

## Open Questions

1. **Migration consolidation — are orphan files safe to delete?**
   - What we know: Three chains all start from `down_revision = None`. Chain A has 6 migrations. Chains B and C are isolated.
   - What's unclear: Whether any database (production or staging) has been stamped with revisions `001` or `0001`.
   - Recommendation: Ask the user if these orphan migrations were ever applied to any database. If yes, use `alembic stamp` after deletion. If no, delete safely.

2. **Coverage scope in monorepo context**
   - What we know: `pytest.ini` sets `testpaths = apps packages tests`. Tests run from project root.
   - What's unclear: Whether `--cov=app` works when pytest runs from root (it measures `app` package wherever it's imported from).
   - Recommendation: Use `.coveragerc` or `pyproject.toml [tool.coverage.run]` with explicit `source = apps/api-postgres/app` for root-level runs, or scope each API's coverage separately.

3. **Do the `org` schema tables already exist via another mechanism?**
   - What we know: `001_create_tables.py` creates them in `org` schema. `003_add_empresa_and_theme.py` creates `empresas` (no schema) and `company_themes` (no schema).
   - What's unclear: Whether the `org` tables were created outside Alembic (manual SQL, seed script).
   - Recommendation: Check if `org.projetos` exists in any running database. If not, the consolidation migration must create them.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| pytest | Test runner | ✓ | >=8.0.0 | — |
| pytest-cov | Coverage measurement | ✗ | — | Add to requirements.txt |
| alembic | Migration management | ✓ | 1.18.4 | — |
| Python | Runtime | ✓ | 3.12+ | — |
| ruff | Lint/format | ✓ | >=0.3.0 | — |

**Missing dependencies with no fallback:**
- pytest-cov — must be added to `apps/api-postgres/requirements.txt` before coverage enforcement works

**Missing dependencies with fallback:**
- None

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest >=8.0.0 |
| Config file | `pytest.ini` (root) |
| Quick run command | `pytest tests/ -v --tb=short --strict-markers` |
| Full suite command | `make test-all` (runs all test suites) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFRA-01 | pytest-cov enforces 70% minimum | integration (CI) | `pytest --cov=app --cov-fail-under=70` | ❌ Wave 0 |
| INFRA-02 | `alembic heads` returns one head | integration | `cd apps/api-postgres && python -m alembic heads` | ❌ Wave 0 |
| INFRA-03 | Schema translate map covers all schemas | unit | `pytest tests/test_schema_validation.py -v` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/ -v --tb=short --strict-markers --cov=app --cov-fail-under=70`
- **Per wave merge:** `make test-all`
- **Phase gate:** All three success criteria verified before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `pytest-cov` added to `apps/api-postgres/requirements.txt`
- [ ] `--cov=app --cov-report=term-missing --cov-fail-under=70` added to `pytest.ini` addopts
- [ ] CI workflow updated with coverage flags
- [ ] Orphan migrations deleted and consolidated
- [ ] Schema validation test file created
- [ ] Coverage `.coveragerc` or equivalent config for monorepo scope

## Sources

### Primary (HIGH confidence)
- pytest-cov official docs (pytest-cov.readthedocs.io) — configuration, `--cov-fail-under`, `--cov` optional argument caveat
- Alembic official docs (alembic.sqlalchemy.org) — migration consolidation patterns, cookbook
- Project `pytest.ini` — current configuration
- Project `apps/api-postgres/alembic/versions/` — all 8 migration files inspected
- Project `.github/workflows/release.yml` — CI pipeline structure
- Project `apps/api-postgres/requirements.txt` — current dependencies

### Secondary (MEDIUM confidence)
- Project `apps/api-postgres/tests/conftest.py` — `_SCHEMA_TRANSLATE` dict and fixture patterns

### Tertiary (LOW confidence)
- pytest-cov minimum version for pytest 8.x compatibility — based on training data, not verified against release notes

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — pytest-cov is the de facto standard, docs verified
- Architecture: HIGH — migration chain analyzed from source files
- Pitfalls: HIGH — all pitfalls documented from official docs
- Migration consolidation approach: MEDIUM — depends on whether orphan files were ever applied to production (needs user confirmation)

**Research date:** 2026-06-02
**Valid until:** 2026-07-02 (stable domain — pytest-cov and Alembic patterns don't change frequently)
