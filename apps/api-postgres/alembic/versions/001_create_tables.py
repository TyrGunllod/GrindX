"""criar tabelas gestao_projetos

Revision ID: 001
Revises: 
Create Date: 2026-06-02
"""

from typing import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "projetos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="planning", nullable=False),
        sa.Column("data_inicio", sa.Date(), nullable=False),
        sa.Column("data_fim", sa.Date(), nullable=False),
        sa.Column("cor", sa.String(length=7), server_default="#3b82f6", nullable=False),
        sa.Column("gerente_id", sa.Integer(), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["gerente_id"], ["iam.usuarios.id"]),
        schema="org",
    )
    op.create_index("ix_org_projetos_nome", "projetos", ["nome"], schema="org")

    op.create_table(
        "recursos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("projeto_id", sa.Integer(), nullable=False),
        sa.Column("cargo_contexto", sa.String(length=100), nullable=True),
        sa.Column("cor", sa.String(length=7), server_default="#3b82f6", nullable=False),
        sa.Column("alocado", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["iam.usuarios.id"]),
        sa.UniqueConstraint("user_id", "projeto_id", name="uq_recurso_user_projeto"),
        schema="org",
    )

    op.create_table(
        "tarefas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="todo", nullable=False),
        sa.Column("prioridade", sa.String(length=10), server_default="medium", nullable=False),
        sa.Column("data_inicio", sa.Date(), nullable=False),
        sa.Column("data_fim", sa.Date(), nullable=False),
        sa.Column("progresso", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("projeto_id", sa.Integer(), nullable=True),
        sa.Column("responsavel_id", sa.Integer(), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["projeto_id"], ["org.projetos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["responsavel_id"], ["org.recursos.id"], ondelete="SET NULL"),
        schema="org",
    )
    op.create_index("ix_org_tarefas_titulo", "tarefas", ["titulo"], schema="org")
    op.create_index("ix_org_tarefas_projeto_id", "tarefas", ["projeto_id"], schema="org")
    op.create_index("ix_org_tarefas_responsavel_id", "tarefas", ["responsavel_id"], schema="org")

    op.create_table(
        "registros_tarefas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tarefa_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=20), server_default="log", nullable=False),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.Column("autor_id", sa.Integer(), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["tarefa_id"], ["org.tarefas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["autor_id"], ["org.recursos.id"], ondelete="SET NULL"),
        schema="org",
    )
    op.create_index("ix_org_registros_tarefas_tarefa_id", "registros_tarefas", ["tarefa_id"], schema="org")
    op.create_index("ix_org_registros_tarefas_autor_id", "registros_tarefas", ["autor_id"], schema="org")


def downgrade() -> None:
    op.drop_table("registros_tarefas", schema="org")
    op.drop_table("tarefas", schema="org")
    op.drop_table("recursos", schema="org")
    op.drop_table("projetos", schema="org")
