"""Add profile fields (codigo, cbo, departamento, cargo, cpf, endereco, cep)

Revision ID: b0c1d2e3f4a5
Revises: a1b2c3d4e5f7
Create Date: 2026-07-01

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b0c1d2e3f4a5"
down_revision: Union[str, None] = "a1b2c3d4e5f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "codigo", sa.String(50), nullable=True, comment="Código do funcionário"
        ),
        schema="iam",
    )
    op.add_column(
        "usuarios",
        sa.Column("cbo", sa.String(20), nullable=True, comment="C.B.O"),
        schema="iam",
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "departamento", sa.String(100), nullable=True, comment="Departamento"
        ),
        schema="iam",
    )
    op.add_column(
        "usuarios",
        sa.Column("cargo", sa.String(100), nullable=True, comment="Cargo"),
        schema="iam",
    )
    op.add_column(
        "usuarios",
        sa.Column("cpf", sa.String(14), nullable=True, comment="CPF"),
        schema="iam",
    )
    op.add_column(
        "usuarios",
        sa.Column("endereco", sa.String(255), nullable=True, comment="Endereço"),
        schema="iam",
    )
    op.add_column(
        "usuarios",
        sa.Column("cep", sa.String(10), nullable=True, comment="CEP"),
        schema="iam",
    )


def downgrade() -> None:
    op.drop_column("usuarios", "cep", schema="iam")
    op.drop_column("usuarios", "endereco", schema="iam")
    op.drop_column("usuarios", "cpf", schema="iam")
    op.drop_column("usuarios", "cargo", schema="iam")
    op.drop_column("usuarios", "departamento", schema="iam")
    op.drop_column("usuarios", "cbo", schema="iam")
    op.drop_column("usuarios", "codigo", schema="iam")
