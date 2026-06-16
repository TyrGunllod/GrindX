"""add theme_history table

Revision ID: 004_add_theme_history
Revises: 003_add_empresa_and_theme
Create Date: 2026-05-20 23:00:00.000000

"""

from alembic import op

revision = "004_add_theme_history"
down_revision = "003_add_empresa_and_theme"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS org.theme_history (
            id SERIAL NOT NULL,
            theme_id INTEGER NOT NULL,
            company_id INTEGER NOT NULL,
            action VARCHAR(50) NOT NULL,
            performed_by INTEGER,
            theme_snapshot JSON,
            changes JSON,
            criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY (theme_id) REFERENCES org.company_themes(id) ON DELETE CASCADE
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_theme_history_theme_id ON org.theme_history (theme_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_theme_history_company_id ON org.theme_history (company_id)"
    )


def downgrade() -> None:
    op.drop_index(
        "ix_theme_history_company_id", table_name="theme_history", schema="org"
    )
    op.drop_index("ix_theme_history_theme_id", table_name="theme_history", schema="org")
    op.drop_table("theme_history", schema="org")
