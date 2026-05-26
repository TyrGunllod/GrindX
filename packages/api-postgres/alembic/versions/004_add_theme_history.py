"""add theme_history table

Revision ID: 004_add_theme_history
Revises: 003_add_empresa_and_theme
Create Date: 2026-05-20 23:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

revision = "004_add_theme_history"
down_revision = "003_add_empresa_and_theme"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "theme_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("theme_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column(
            "performed_by",
            sa.Integer(),
            nullable=True,
            comment="ID do usuário que executou a ação",
        ),
        sa.Column(
            "theme_snapshot",
            sa.JSON(),
            nullable=True,
            comment="Snapshot completo do tema após a ação",
        ),
        sa.Column("changes", sa.JSON(), nullable=True, comment="Diff das alterações"),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["theme_id"], ["company_themes.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_theme_history_theme_id", "theme_history", ["theme_id"])
    op.create_index("ix_theme_history_company_id", "theme_history", ["company_id"])


def downgrade() -> None:
    op.drop_index("ix_theme_history_company_id", table_name="theme_history")
    op.drop_index("ix_theme_history_theme_id", table_name="theme_history")
    op.drop_table("theme_history")
