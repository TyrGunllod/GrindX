"""add usuario_modulos

Revision ID: 002_add_usuario_modulos
Revises: 001_initial_schema
Create Date: 2026-05-20 09:50:00.000000

"""


from alembic import op

# revision identifiers, used by Alembic.
revision = "002_add_usuario_modulos"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar schema portal (idempotente)
    op.execute("CREATE SCHEMA IF NOT EXISTS portal")

    # Criar tabela portal_abas (idempotente)
    op.execute("""
        CREATE TABLE IF NOT EXISTS portal.portal_abas (
            id SERIAL NOT NULL,
            nome VARCHAR(50) NOT NULL,
            icone VARCHAR(50),
            ordem INTEGER DEFAULT 0 NOT NULL,
            ativo BOOLEAN DEFAULT true NOT NULL,
            parent_id INTEGER,
            PRIMARY KEY (id)
        )
    """)
    # Criar FK parent_id apenas se não existir
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_aba_parent'
            ) THEN
                ALTER TABLE portal.portal_abas
                    ADD CONSTRAINT fk_aba_parent
                    FOREIGN KEY (parent_id) REFERENCES portal.portal_abas(id)
                    ON DELETE CASCADE;
            END IF;
        END $$;
    """)

    # Criar tabela portal_modulos (idempotente)
    op.execute("""
        CREATE TABLE IF NOT EXISTS portal.portal_modulos (
            id SERIAL NOT NULL,
            aba_id INTEGER NOT NULL,
            nome VARCHAR(100) NOT NULL,
            slug VARCHAR(100) UNIQUE NOT NULL,
            url VARCHAR(255) NOT NULL,
            icone VARCHAR(50),
            role_minima VARCHAR(20) DEFAULT 'operador' NOT NULL,
            ativo BOOLEAN DEFAULT true NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (aba_id) REFERENCES portal.portal_abas(id) ON DELETE CASCADE
        )
    """)
    # Criar index idempotente
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_portal_modulos_aba_id
        ON portal.portal_modulos (aba_id)
    """)

    # Criar tabela usuario_modulos (idempotente)
    op.execute("""
        CREATE TABLE IF NOT EXISTS usuario_modulos (
            usuario_id INTEGER NOT NULL,
            modulo_id INTEGER NOT NULL,
            concedido_em TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            concedido_por_id INTEGER,
            PRIMARY KEY (usuario_id, modulo_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (modulo_id) REFERENCES portal.portal_modulos(id) ON DELETE CASCADE,
            FOREIGN KEY (concedido_por_id) REFERENCES usuarios(id) ON DELETE SET NULL
        )
    """)


def downgrade() -> None:
    op.drop_table("usuario_modulos")
    op.drop_index(
        "ix_portal_modulos_aba_id", table_name="portal_modulos", schema="portal"
    )
    op.drop_table("portal_modulos", schema="portal")
    op.drop_constraint(
        "fk_aba_parent", "portal_abas", schema="portal", type_="foreignkey"
    )
    op.drop_table("portal_abas", schema="portal")
