"""adicionar coluna mostrar_rotulo em pop_docs_campos

Revision ID: 101
Revises: 100
Create Date: 2026-08-22

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "101"
down_revision: Union[str, None] = "100"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Garante que a tabela existe (idempotente para remoção fora de ordem)
    if "pop_docs_campos" not in inspector.get_table_names(schema="portal"):
        return

    # Sanitiza dados legados antes de criar o CHECK — evita CheckViolation
    # quando o módulo foi removido/reimportado fora de ordem e restaram tipos antigos
    op.execute(
        """
        UPDATE portal.pop_docs_campos
        SET tipo = 'comum'
        WHERE tipo NOT IN ('comum','topico','observacao','imagem','alerta','quebra_pagina','paragrafo')
        """
    )

    # Cria CHECK apenas se ainda não existir (idempotente)
    # Usa DO block para não falhar se constraint já existir
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'pop_docs_campos_tipo_check'
                AND conrelid = 'portal.pop_docs_campos'::regclass
            ) THEN
                ALTER TABLE portal.pop_docs_campos
                ADD CONSTRAINT pop_docs_campos_tipo_check
                CHECK (tipo IN ('comum','topico','observacao','imagem','alerta','quebra_pagina','paragrafo'));
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'pop_docs_campos_tipo_check'
                AND conrelid = 'portal.pop_docs_campos'::regclass
            ) THEN
                ALTER TABLE portal.pop_docs_campos DROP CONSTRAINT pop_docs_campos_tipo_check;
            END IF;
        END $$;
        """
    )
