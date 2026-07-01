"""Add numero column to iam.usuarios

Revision ID: c2d3e4f5a6b7
Revises: b0c1d2e3f4a5
Create Date: 2026-07-01

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c2d3e4f5a6b7"
down_revision: Union[str, None] = "b0c1d2e3f4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("numero", sa.String(20), nullable=True, comment="Número do endereço"),
        schema="iam",
    )


def downgrade() -> None:
    op.drop_column("usuarios", "numero", schema="iam")
