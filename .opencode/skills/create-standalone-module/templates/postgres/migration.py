"""criar tabela {table_name}

Revision ID: {{revision}}
Revises: {{down_revision}}
Create Date: {{date}}
"""

from typing import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "{{revision}}"
down_revision: str | None = "{{down_revision}}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "{table_name}",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="{schema_name}",
    )


def downgrade() -> None:
    op.drop_table("{table_name}", schema="{schema_name}")
