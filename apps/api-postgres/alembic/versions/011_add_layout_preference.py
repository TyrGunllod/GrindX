"""Add layout_preference column to usuarios

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-06-29

"""

from typing import Sequence, Union

from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add layout_preference column to usuarios (schema-agnostico)."""
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
                AND column_name = 'layout_preference'
            ) THEN
                EXECUTE format('ALTER TABLE %I.usuarios ADD COLUMN layout_preference VARCHAR(20)', sch);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Drop layout_preference column from iam.usuarios."""
    op.drop_column("usuarios", "layout_preference", schema="iam")
