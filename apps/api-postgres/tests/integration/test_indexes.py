"""
Integration tests for database index definitions.

Verifies that SQLAlchemy models define the expected indexes
for common query patterns (PERF-02).

NOTE: These tests verify index DEFINITIONS on the SQLAlchemy models,
not the actual PostgreSQL indexes (which require running the migration
against a real DB). The migration itself is tested by running
`alembic upgrade head` in a real environment.
"""

import pytest

from app.modules.iam.models.usuario import Usuario
from app.modules.org.models.theme import CompanyTheme
from app.modules.portal.models.portal import Modulo


@pytest.mark.integration
def test_indexes_exist_on_models(db_session):
    """Verify that models define indexes for performance optimization."""
    # Collect all index names from each model
    theme_indexes = {idx.name for idx in CompanyTheme.__table__.indexes}
    usuario_indexes = {idx.name for idx in Usuario.__table__.indexes}
    modulo_indexes = {idx.name for idx in Modulo.__table__.indexes}

    # Verify expected indexes exist
    assert "ix_company_themes_company_active" in theme_indexes, (
        f"Missing composite index on CompanyTheme. Found: {theme_indexes}"
    )
    assert "ix_usuarios_role" in usuario_indexes, (
        f"Missing role index on Usuario. Found: {usuario_indexes}"
    )
    assert "ix_usuarios_ativo" in usuario_indexes, (
        f"Missing ativo index on Usuario. Found: {usuario_indexes}"
    )
    assert "ix_usuarios_empresa_id" in usuario_indexes, (
        f"Missing empresa_id index on Usuario. Found: {usuario_indexes}"
    )
    assert "ix_portal_modulos_aba_id" in modulo_indexes, (
        f"Missing aba_id index on Modulo. Found: {modulo_indexes}"
    )


@pytest.mark.integration
def test_company_theme_composite_index_definition(db_session):
    """Verify CompanyTheme has a composite index on (company_id, is_active)."""
    indexes = CompanyTheme.__table__.indexes

    composite_index = None
    for idx in indexes:
        if idx.name == "ix_company_themes_company_active":
            composite_index = idx
            break

    assert composite_index is not None, (
        "Composite index 'ix_company_themes_company_active' not found"
    )

    # Verify the index covers both columns
    column_names = {col.name for col in composite_index.columns}
    assert "company_id" in column_names, (
        f"Index missing company_id column. Columns: {column_names}"
    )
    assert "is_active" in column_names, (
        f"Index missing is_active column. Columns: {column_names}"
    )


@pytest.mark.integration
def test_usuario_role_index_definition(db_session):
    """Verify Usuario has an index on the role column."""
    indexes = Usuario.__table__.indexes

    role_index = None
    for idx in indexes:
        if idx.name == "ix_usuarios_role":
            role_index = idx
            break

    assert role_index is not None, "Index 'ix_usuarios_role' not found on Usuario"

    column_names = {col.name for col in role_index.columns}
    assert "role" in column_names, f"Index missing role column. Columns: {column_names}"


@pytest.mark.integration
def test_usuario_ativo_index_definition(db_session):
    """Verify Usuario has an index on the ativo column."""
    indexes = Usuario.__table__.indexes

    ativo_index = None
    for idx in indexes:
        if idx.name == "ix_usuarios_ativo":
            ativo_index = idx
            break

    assert ativo_index is not None, "Index 'ix_usuarios_ativo' not found on Usuario"

    column_names = {col.name for col in ativo_index.columns}
    assert "ativo" in column_names, (
        f"Index missing ativo column. Columns: {column_names}"
    )
