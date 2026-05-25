"""add parent_id to portal_abas

Revision ID: 005_add_aba_parent_id
Revises: 004_add_theme_history
Create Date: 2026-05-25 23:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "005_add_aba_parent_id"
down_revision = "004_add_theme_history"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "portal_abas",
        sa.Column("parent_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_aba_parent",
        "portal_abas",
        "portal_abas",
        ["parent_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_aba_parent", "portal_abas", type_="foreignkey")
    op.drop_column("portal_abas", "parent_id")
