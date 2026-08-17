"""add audit_logs and sessoes tables

Revision ID: a1b2c3d4e5f6
Revises: 8ec10f792d4b
Create Date: 2026-08-17 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "8ec10f792d4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("iam.usuarios.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("entidade", sa.String(100), nullable=False),
        sa.Column("entidade_id", sa.Integer(), nullable=True),
        sa.Column("acao", sa.String(20), nullable=False),
        sa.Column("campos_alterados", sa.JSON(), nullable=False),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Index("ix_audit_logs_entidade_id", "entidade", "entidade_id"),
        sa.Index("ix_audit_logs_user_id", "user_id"),
        sa.Index("ix_audit_logs_criado_em", "criado_em"),
        schema="org",
    )
    op.create_table(
        "sessoes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("iam.usuarios.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "login_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("logout_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duracao_segundos", sa.Integer(), nullable=True),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("logout_motivo", sa.String(20), nullable=True),
        sa.Index("ix_sessoes_user_id", "user_id"),
        sa.Index("ix_sessoes_login_at", "login_at"),
        schema="org",
    )


def downgrade() -> None:
    op.drop_table("sessoes", schema="org")
    op.drop_table("audit_logs", schema="org")
