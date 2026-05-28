"""add usuario_modulos

Revision ID: 002_add_usuario_modulos
Revises: 001_initial_schema
Create Date: 2026-05-20 09:50:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "002_add_usuario_modulos"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabela usuario_modulos
    op.create_table(
        "usuario_modulos",
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("modulo_id", sa.Integer(), nullable=False),
        sa.Column(
            "concedido_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("concedido_por_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        # Assuming portal_modulos table exists
        sa.ForeignKeyConstraint(
            ["modulo_id"], ["portal_modulos.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["concedido_por_id"], ["usuarios.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("usuario_id", "modulo_id"),
    )


def downgrade() -> None:
    # Remover tabela usuario_modulos
    op.drop_table("usuario_modulos")
