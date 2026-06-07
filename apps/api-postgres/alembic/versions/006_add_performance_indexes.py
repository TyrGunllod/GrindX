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
    """Create indexes for common query patterns."""
    # Composite index for find_active_by_company_id (themes by company + active status)
    op.create_index(
        "ix_company_themes_company_active",
        "company_themes",
        ["company_id", "is_active"],
        unique=False,
        schema="org",
    )

    # Index for listar_por_role (users filtered by role)
    op.create_index(
        "ix_usuarios_role",
        "usuarios",
        ["role"],
        unique=False,
        schema="iam",
    )

    # Index for listar_ativos (active users)
    op.create_index(
        "ix_usuarios_ativo",
        "usuarios",
        ["ativo"],
        unique=False,
        schema="iam",
    )

    # Index for empresa_id joins (users by company)
    op.create_index(
        "ix_usuarios_empresa_id",
        "usuarios",
        ["empresa_id"],
        unique=False,
        schema="iam",
    )

    # Index for module lookups by tab (portal modulos by aba)
    op.create_index(
        "ix_portal_modulos_aba_id",
        "portal_modulos",
        ["aba_id"],
        unique=False,
        schema="portal",
    )


def downgrade() -> None:
    """Drop all performance indexes."""
    op.drop_index("ix_portal_modulos_aba_id", table_name="portal_modulos", schema="portal")
    op.drop_index("ix_usuarios_empresa_id", table_name="usuarios", schema="iam")
    op.drop_index("ix_usuarios_ativo", table_name="usuarios", schema="iam")
    op.drop_index("ix_usuarios_role", table_name="usuarios", schema="iam")
    op.drop_index("ix_company_themes_company_active", table_name="company_themes", schema="org")
