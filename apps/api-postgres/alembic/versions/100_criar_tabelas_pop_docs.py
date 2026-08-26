"""criar tabelas pop_docs e pop_docs_campos

Revision ID: 100
Revises: f49af6b8a8d4
Create Date: 2026-08-22

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "100"
down_revision: Union[str, None] = "f49af6b8a8d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if "pop_docs" not in inspector.get_table_names(schema="portal"):
        op.create_table(
            "pop_docs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("titulo", sa.String(200), nullable=False),
            sa.Column("codigo", sa.String(50), nullable=True),
            sa.Column("versao", sa.String(20), nullable=True),
            sa.Column(
                "ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False
            ),
            sa.Column(
                "criado_em",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "atualizado_em",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            schema="portal",
        )

    if "pop_docs_campos" not in inspector.get_table_names(schema="portal"):
        op.create_table(
            "pop_docs_campos",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "pop_doc_id",
                sa.Integer(),
                sa.ForeignKey("portal.pop_docs.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "ordem", sa.Integer(), nullable=False, server_default=sa.text("0")
            ),
            sa.Column("tipo", sa.String(30), nullable=False),
            sa.Column("conteudo", sa.Text(), nullable=True),
            sa.Column(
                "mostrar_rotulo",
                sa.Boolean(),
                server_default=sa.text("false"),
                nullable=False,
            ),
            sa.Column(
                "criado_em",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            schema="portal",
        )


def downgrade() -> None:
    op.drop_table("pop_docs_campos", schema="portal")
    op.drop_table("pop_docs", schema="portal")
