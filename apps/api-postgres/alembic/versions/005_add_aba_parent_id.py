"""add parent_id to portal_abas

Revision ID: 005_add_aba_parent_id
Revises: 004_add_theme_history
Create Date: 2026-05-25 23:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

revision = "005_add_aba_parent_id"
down_revision = "004_add_theme_history"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # parent_id e FK já existem desde a migration 002 (criação de portal_abas)
    # Esta migration agora é um no-op para bancos que já foram criados com a 002 atualizada
    pass


def downgrade() -> None:
    # Nada a reverter — parent_id faz parte da criação original da tabela
    pass
