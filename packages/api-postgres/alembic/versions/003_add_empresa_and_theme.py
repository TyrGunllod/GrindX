"""add empresa and company_theme tables

Revision ID: 003_add_empresa_and_theme
Revises: 002_add_usuario_modulos
Create Date: 2026-05-20 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "003_add_empresa_and_theme"
down_revision = "002_add_usuario_modulos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabela empresas
    op.create_table(
        "empresas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("dominio", sa.String(255), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
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
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dominio"),
    )

    # Adicionar empresa_id em usuarios
    op.add_column(
        "usuarios",
        sa.Column(
            "empresa_id", sa.Integer(), nullable=True, comment="Empresa do usuário"
        ),
    )
    op.create_foreign_key(
        "fk_usuarios_empresa_id",
        "usuarios",
        "empresas",
        ["empresa_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_usuarios_empresa_id", "usuarios", ["empresa_id"])

    # Criar tabela company_themes
    op.create_table(
        "company_themes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("colors", sa.JSON(), nullable=True),
        sa.Column("fonts", sa.JSON(), nullable=True),
        sa.Column(
            "icon_library",
            sa.String(50),
            nullable=False,
            server_default=sa.text("'fontawesome'"),
        ),
        sa.Column("tokens", sa.JSON(), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("logo_short_url", sa.String(500), nullable=True),
        sa.Column("company_name", sa.String(100), nullable=True),
        sa.Column("copyright_text", sa.String(200), nullable=True),
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
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_company_themes_company_id", "company_themes", ["company_id"])


def downgrade() -> None:
    op.drop_index("ix_company_themes_company_id", table_name="company_themes")
    op.drop_table("company_themes")
    op.drop_index("ix_usuarios_empresa_id", table_name="usuarios")
    op.drop_constraint("fk_usuarios_empresa_id", "usuarios", type_="foreignkey")
    op.drop_column("usuarios", "empresa_id")
    op.drop_table("empresas")
