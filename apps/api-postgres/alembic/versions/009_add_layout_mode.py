"""Add layout_mode column to company_themes

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-09

"""

from typing import Sequence, Union

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add layout_mode column with topbar default; existing themes get sidebar (idempotente)."""
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'org' AND table_name = 'company_themes'
                AND column_name = 'layout_mode'
            ) THEN
                ALTER TABLE org.company_themes
                    ADD COLUMN layout_mode VARCHAR(20) NOT NULL DEFAULT 'topbar';
            END IF;
        END $$;
    """)
    op.execute(
        "UPDATE org.company_themes SET layout_mode = 'sidebar' WHERE layout_mode = 'topbar'"
    )


def downgrade() -> None:
    """Drop layout_mode column."""
    op.drop_column("company_themes", "layout_mode", schema="org")
