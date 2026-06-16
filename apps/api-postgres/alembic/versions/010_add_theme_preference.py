"""Add theme_preference column to usuarios

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-10

"""

from typing import Sequence, Union

from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add theme_preference column to usuarios (schema-agnostico)."""
    op.execute("""
        DO $$
        DECLARE
            sch TEXT;
        BEGIN
            SELECT table_schema INTO sch
            FROM information_schema.tables
            WHERE table_name = 'usuarios' LIMIT 1;
            IF sch IS NULL THEN RETURN; END IF;

            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = sch AND table_name = 'usuarios'
                AND column_name = 'theme_preference'
            ) THEN
                EXECUTE format('ALTER TABLE %I.usuarios ADD COLUMN theme_preference VARCHAR(10)', sch);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Drop theme_preference column from iam.usuarios."""
    op.drop_column("usuarios", "theme_preference", schema="iam")
