"""Add performance indexes for common query patterns

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-06

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create indexes for common query patterns (idempotente)."""
    # Composite index for find_active_by_company_id (themes by company + active status)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_company_themes_company_active
        ON org.company_themes (company_id, is_active)
    """)

    # Index for listar_por_role (users filtered by role)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_usuarios_role
        ON iam.usuarios (role)
    """)

    # Index for listar_ativos (active users)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_usuarios_ativo
        ON iam.usuarios (ativo)
    """)

    # Index for empresa_id joins (users by company)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_usuarios_empresa_id
        ON iam.usuarios (empresa_id)
    """)

    # Index for module lookups by tab (portal modulos by aba)
    # NOTA: ix_portal_modulos_aba_id já é criado na migration 002
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_portal_modulos_aba_id
        ON portal.portal_modulos (aba_id)
    """)


def downgrade() -> None:
    """Drop all performance indexes."""
    op.drop_index(
        "ix_portal_modulos_aba_id", table_name="portal_modulos", schema="portal"
    )
    op.drop_index("ix_usuarios_empresa_id", table_name="usuarios", schema="iam")
    op.drop_index("ix_usuarios_ativo", table_name="usuarios", schema="iam")
    op.drop_index("ix_usuarios_role", table_name="usuarios", schema="iam")
    op.drop_index(
        "ix_company_themes_company_active", table_name="company_themes", schema="org"
    )
