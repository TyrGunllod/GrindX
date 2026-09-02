"""add mensagens and anexos_mensagem tables

Revision ID: 023a4c5d6e7f
Revises: f49af6b8a8d4
Create Date: 2026-08-25 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "023a4c5d6e7f"
down_revision: Union[str, None] = "f49af6b8a8d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mensagens",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "resposta_a_id",
            sa.BigInteger(),
            sa.ForeignKey("org.mensagens.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "remetente_id",
            sa.BigInteger(),
            sa.ForeignKey("iam.usuarios.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "destinatario_id",
            sa.BigInteger(),
            sa.ForeignKey("iam.usuarios.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("titulo", sa.String(150), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column(
            "categoria",
            sa.String(20),
            server_default=sa.text("'DIRETA'"),
            nullable=False,
        ),
        sa.Column("url_acao", sa.String(255), nullable=True),
        sa.Column("lida_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("arquivada_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "categoria IN ('SISTEMA', 'DIRETA', 'AVISO')",
            name="ck_mensagens_categoria",
        ),
        sa.Index("ix_mensagens_destinatario_id", "destinatario_id", "criado_em"),
        sa.Index("ix_mensagens_resposta_a", "resposta_a_id"),
        schema="org",
    )
    op.create_index(
        "ix_mensagens_nao_lidas",
        "mensagens",
        ["destinatario_id", "criado_em"],
        unique=False,
        postgresql_where=sa.text("lida_em IS NULL"),
        schema="org",
    )
    op.create_table(
        "anexos_mensagem",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "mensagem_id",
            sa.BigInteger(),
            sa.ForeignKey("org.mensagens.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nome_arquivo_original", sa.String(255), nullable=False),
        sa.Column("caminho", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("tamanho_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Index("ix_anexos_mensagem_mensagem_id", "mensagem_id"),
        schema="org",
    )


def downgrade() -> None:
    op.drop_table("anexos_mensagem", schema="org")
    op.drop_index("ix_mensagens_nao_lidas", table_name="mensagens", schema="org")
    op.drop_table("mensagens", schema="org")
