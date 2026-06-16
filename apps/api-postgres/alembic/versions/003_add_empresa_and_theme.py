"""add empresa and company_theme tables

Revision ID: 003_add_empresa_and_theme
Revises: 002_add_usuario_modulos
Create Date: 2026-05-20 12:00:00.000000

"""

from alembic import op

revision = "003_add_empresa_and_theme"
down_revision = "002_add_usuario_modulos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS org")

    # Criar tabela empresas no schema org (idempotente)
    op.execute("""
        CREATE TABLE IF NOT EXISTS org.empresas (
            id SERIAL NOT NULL,
            nome VARCHAR(100) NOT NULL,
            dominio VARCHAR(255),
            ativo BOOLEAN NOT NULL DEFAULT true,
            criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            atualizado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            UNIQUE (dominio)
        )
    """)

    # Adicionar empresa_id e FK em usuarios (idempotente, schema-agnostico)
    op.execute("""
        DO $$
        DECLARE
            sch TEXT;
        BEGIN
            SELECT table_schema INTO sch
            FROM information_schema.tables
            WHERE table_name = 'usuarios' LIMIT 1;
            IF sch IS NULL THEN RETURN; END IF;

            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = sch AND table_name = 'usuarios'
                AND column_name = 'empresa_id'
            ) THEN
                EXECUTE format('ALTER TABLE %I.usuarios ADD COLUMN empresa_id INTEGER', sch);
                EXECUTE format('COMMENT ON COLUMN %I.usuarios.empresa_id IS ''Empresa do usuário''', sch);
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_usuarios_empresa_id'
            ) THEN
                EXECUTE format(
                    'ALTER TABLE %I.usuarios ADD CONSTRAINT fk_usuarios_empresa_id '
                    'FOREIGN KEY (empresa_id) REFERENCES org.empresas(id) ON DELETE SET NULL',
                    sch
                );
            END IF;

            EXECUTE format(
                'CREATE INDEX IF NOT EXISTS ix_usuarios_empresa_id ON %I.usuarios (empresa_id)',
                sch
            );
        END $$;
    """)

    # Criar tabela company_themes no schema org (idempotente)
    op.execute("""
        CREATE TABLE IF NOT EXISTS org.company_themes (
            id SERIAL NOT NULL,
            company_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT false,
            colors JSON,
            fonts JSON,
            icon_library VARCHAR(50) NOT NULL DEFAULT 'fontawesome',
            tokens JSON,
            logo_url VARCHAR(500),
            logo_short_url VARCHAR(500),
            company_name VARCHAR(100),
            copyright_text VARCHAR(200),
            criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            atualizado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY (company_id) REFERENCES org.empresas(id) ON DELETE CASCADE
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_company_themes_company_id ON org.company_themes (company_id)"
    )


def downgrade() -> None:
    op.drop_index(
        "ix_company_themes_company_id", table_name="company_themes", schema="org"
    )
    op.drop_table("company_themes", schema="org")
    op.drop_index("ix_usuarios_empresa_id", table_name="usuarios", schema="iam")
    op.drop_constraint(
        "fk_usuarios_empresa_id", "usuarios", type_="foreignkey", schema="iam"
    )
    op.drop_column("usuarios", "empresa_id", schema="iam")
    op.drop_table("empresas", schema="org")
