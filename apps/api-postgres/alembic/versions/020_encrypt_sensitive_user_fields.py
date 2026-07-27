"""encrypt sensitive user fields

Revision ID: faf59ca952af
Revises: b7c8d9e0f1a2
Create Date: 2026-07-02 16:48:33.140101

"""

from alembic import op
import sqlalchemy as sa

from app.core.config import settings
from shared.security.encryption import encrypt_value

# revision identifiers, used by Alembic.
revision = "faf59ca952af"
down_revision = "b7c8d9e0f1a2"
branch_labels = None
depends_on = None

SECRET_KEY = settings.SECRET_KEY
SENSITIVE_COLS = ["cpf", "rg", "salario", "endereco", "telefone", "celular"]


def _encrypt_existing_data():
    """Encrypta dados existentes que ainda estão em plaintext."""
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(only=("usuarios",), schema="iam", bind=conn)
    usuarios = meta.tables["iam.usuarios"]

    for col_name in SENSITIVE_COLS:
        col = getattr(usuarios.c, col_name)
        rows = conn.execute(
            sa.select(usuarios.c.id, col).where(col.isnot(None), col.notlike("enc:%"))
        ).fetchall()

        for row in rows:
            encrypted = encrypt_value(SECRET_KEY, row[1])
            if encrypted != row[1]:
                conn.execute(
                    sa.update(usuarios)
                    .where(usuarios.c.id == row[0])
                    .values({col_name: encrypted})
                )


def upgrade() -> None:
    schema = "iam"
    for col in SENSITIVE_COLS:
        op.alter_column(
            "usuarios",
            col,
            existing_type=sa.String(),
            type_=sa.String(255),
            existing_nullable=True,
            schema=schema,
        )

    _encrypt_existing_data()


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
