"""Add theme_preference column to usuarios

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-10

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add theme_preference column to iam.usuarios."""
    op.add_column(
        "usuarios",
        sa.Column("theme_preference", sa.String(10), nullable=True),
        schema="iam",
    )


def downgrade() -> None:
    """Drop theme_preference column from iam.usuarios."""
    op.drop_column("usuarios", "theme_preference", schema="iam")
