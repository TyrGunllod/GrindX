"""Add temp_password_hash and expires_at to usuarios

Revision ID: a1b2c3d4e5f6
Revises: 005_add_aba_parent_id
Create Date: 2026-06-02

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "005_add_aba_parent_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add temp_password_hash and expires_at columns to usuarios table."""
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'iam' AND table_name = 'usuarios'
                AND column_name = 'temp_password_hash'
            ) THEN
                ALTER TABLE iam.usuarios ADD COLUMN temp_password_hash VARCHAR(255) NULL;
                COMMENT ON COLUMN iam.usuarios.temp_password_hash
                    IS 'Hash bcrypt da senha temporaria';
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'iam' AND table_name = 'usuarios'
                AND column_name = 'expires_at'
            ) THEN
                ALTER TABLE iam.usuarios ADD COLUMN expires_at TIMESTAMP WITH TIME ZONE NULL;
                COMMENT ON COLUMN iam.usuarios.expires_at
                    IS 'Expiracao da senha temporaria';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Remove temp_password_hash and expires_at columns from usuarios table."""
    op.drop_column("usuarios", "expires_at", schema="iam")
    op.drop_column("usuarios", "temp_password_hash", schema="iam")
