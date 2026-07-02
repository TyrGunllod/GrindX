"""encrypt sensitive user fields

Revision ID: faf59ca952af
Revises: b7c8d9e0f1a2
Create Date: 2026-07-02 16:48:33.140101

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "faf59ca952af"
down_revision = "b7c8d9e0f1a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    schema = "iam"
    for col in ("cpf", "rg", "salario", "endereco", "telefone", "celular"):
        op.alter_column(
            "usuarios",
            col,
            existing_type=sa.String(),
            type_=sa.String(255),
            existing_nullable=True,
            schema=schema,
        )


def downgrade() -> None:
    schema = "iam"
    old_lengths = {
        "cpf": 14,
        "rg": 12,
        "salario": 20,
        "endereco": 255,
        "telefone": 15,
        "celular": 15,
    }
    for col, length in old_lengths.items():
        op.alter_column(
            "usuarios",
            col,
            existing_type=sa.String(255),
            type_=sa.String(length),
            existing_nullable=True,
            schema=schema,
        )
