"""Add rg and salario columns to iam.usuarios

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-07-01

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f5a6b7c8d9e0"
down_revision: Union[str, None] = "e4f5a6b7c8d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("rg", sa.String(12), nullable=True, comment="RG"),
        schema="iam",
    )
    op.add_column(
        "usuarios",
        sa.Column("salario", sa.String(20), nullable=True, comment="Salário Base"),
        schema="iam",
    )


def downgrade() -> None:
    op.drop_column("usuarios", "salario", schema="iam")
    op.drop_column("usuarios", "rg", schema="iam")
