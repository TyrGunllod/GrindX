"""Add ordem column to portal_modulos

Revision ID: a1b2c3d4e5f7
Revises: f6a7b8c9d0e1
Create Date: 2026-06-30

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f7"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "portal_modulos",
        sa.Column("ordem", sa.Integer(), server_default=sa.text("0"), nullable=False),
        schema="portal",
    )
    op.create_index(
        "ix_portal_modulos_aba_id_ordem",
        "portal_modulos",
        ["aba_id", "ordem"],
        schema="portal",
    )


def downgrade() -> None:
    op.drop_index("ix_portal_modulos_aba_id_ordem", schema="portal")
    op.drop_column("portal_modulos", "ordem", schema="portal")
