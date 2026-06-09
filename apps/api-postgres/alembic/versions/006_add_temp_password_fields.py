"""Add temp_password_hash and expires_at to usuarios

Revision ID: a1b2c3d4e5f6
Revises: 005_add_aba_parent_id
Create Date: 2026-06-02

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "005_add_aba_parent_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add temp_password_hash and expires_at columns to usuarios table."""
    op.add_column(
        "usuarios",
        sa.Column(
            "temp_password_hash",
            sa.String(255),
            nullable=True,
            comment="Hash bcrypt da senha temporária",
        ),
        schema="iam",
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Expiração da senha temporária",
        ),
        schema="iam",
    )


def downgrade() -> None:
    """Remove temp_password_hash and expires_at columns from usuarios table."""
    op.drop_column("usuarios", "expires_at", schema="iam")
    op.drop_column("usuarios", "temp_password_hash", schema="iam")
