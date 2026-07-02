"""Add bairro, cidade, uf columns to iam.usuarios

Revision ID: b7c8d9e0f1a2
Revises: a6b7c8d9e0f1
Create Date: 2026-07-01

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, None] = "a6b7c8d9e0f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("bairro", sa.String(100), nullable=True, comment="Bairro"),
        schema="iam",
    )
    op.add_column(
        "usuarios",
        sa.Column("cidade", sa.String(100), nullable=True, comment="Cidade"),
        schema="iam",
    )
    op.add_column(
        "usuarios",
        sa.Column("uf", sa.String(2), nullable=True, comment="UF"),
        schema="iam",
    )
    op.alter_column(
        "usuarios",
        "classificacao",
        type_=sa.String(10),
        existing_type=sa.String(20),
        schema="iam",
    )


def downgrade() -> None:
    op.alter_column(
        "usuarios",
        "classificacao",
        type_=sa.String(20),
        existing_type=sa.String(10),
        schema="iam",
    )
    op.drop_column("usuarios", "uf", schema="iam")
    op.drop_column("usuarios", "cidade", schema="iam")
    op.drop_column("usuarios", "bairro", schema="iam")
