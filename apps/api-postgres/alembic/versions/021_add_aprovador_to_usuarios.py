"""add aprovador column to iam.usuarios

Revision ID: 8ec10f792d4b
Revises: faf59ca952af
Create Date: 2026-07-27 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "8ec10f792d4b"
down_revision: Union[str, None] = "faf59ca952af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "aprovador",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="Se o usuário é aprovador de documentos",
        ),
        schema="iam",
    )


def downgrade() -> None:
    op.drop_column("usuarios", "aprovador", schema="iam")
