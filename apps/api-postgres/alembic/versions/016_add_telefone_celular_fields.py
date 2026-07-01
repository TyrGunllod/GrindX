"""Add telefone and celular columns to iam.usuarios

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-07-01

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e4f5a6b7c8d9"
down_revision: Union[str, None] = "d3e4f5a6b7c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("telefone", sa.String(15), nullable=True, comment="Telefone"),
        schema="iam",
    )
    op.add_column(
        "usuarios",
        sa.Column("celular", sa.String(15), nullable=True, comment="Celular"),
        schema="iam",
    )


def downgrade() -> None:
    op.drop_column("usuarios", "celular", schema="iam")
    op.drop_column("usuarios", "telefone", schema="iam")
