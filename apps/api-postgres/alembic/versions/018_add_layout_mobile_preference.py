"""Add layout_mobile_preference column to iam.usuarios

Revision ID: a6b7c8d9e0f1
Revises: f5a6b7c8d9e0
Create Date: 2026-07-01

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a6b7c8d9e0f1"
down_revision: Union[str, None] = "f5a6b7c8d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "layout_mobile_preference",
            sa.String(20),
            nullable=True,
            comment="Preferência de layout mobile: sidebar, topbar ou null",
        ),
        schema="iam",
    )


def downgrade() -> None:
    op.drop_column("usuarios", "layout_mobile_preference", schema="iam")
