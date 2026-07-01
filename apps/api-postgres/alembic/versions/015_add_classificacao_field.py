"""Add classificacao column to iam.usuarios

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-07-01

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d3e4f5a6b7c8"
down_revision: Union[str, None] = "c2d3e4f5a6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "classificacao",
            sa.String(20),
            nullable=True,
            comment="Classificação: Junior, Pleno, Senior, I, II, III, IV, V",
        ),
        schema="iam",
    )


def downgrade() -> None:
    op.drop_column("usuarios", "classificacao", schema="iam")
