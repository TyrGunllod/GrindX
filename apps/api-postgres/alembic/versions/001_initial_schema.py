"""Initial schema - criar tabelas usuarios e produtos

Revision ID: 001_initial_schema
Revises: None
Create Date: 2025-01-15 10:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria as tabelas iniciais: usuarios e produtos (idempotente, schema-agnostico)."""

    op.execute("CREATE SCHEMA IF NOT EXISTS iam")
    op.execute("""
        CREATE TABLE IF NOT EXISTS iam.usuarios (
            id SERIAL NOT NULL,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL,
            nome_completo VARCHAR(150) NOT NULL,
            senha_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'leitura',
            ativo BOOLEAN NOT NULL DEFAULT true,
            criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            atualizado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            UNIQUE (username),
            UNIQUE (email)
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_usuarios_username ON iam.usuarios (username)"
    )

    op.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL NOT NULL,
            nome VARCHAR(100) NOT NULL,
            descricao VARCHAR(500),
            preco NUMERIC(10, 2) NOT NULL,
            ativo BOOLEAN NOT NULL DEFAULT true,
            criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            atualizado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            PRIMARY KEY (id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_produtos_nome ON produtos (nome)")


def downgrade() -> None:
    """Remove as tabelas criadas."""
    op.drop_table("produtos")
    op.drop_table("usuarios", schema="iam")
