"""Consolidate org schema tables — replaces orphan migrations 001_create_tables and 0001_criar_tabela_projetos

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-03
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Ensure org schema exists
    op.execute("CREATE SCHEMA IF NOT EXISTS org")

    # projetos
    op.execute("""
        CREATE TABLE IF NOT EXISTS org.projetos (
            id SERIAL NOT NULL,
            nome VARCHAR(200) NOT NULL,
            descricao TEXT,
            status VARCHAR(20) DEFAULT 'planning' NOT NULL,
            data_inicio DATE NOT NULL,
            data_fim DATE NOT NULL,
            cor VARCHAR(7) DEFAULT '#3b82f6' NOT NULL,
            gerente_id INTEGER,
            ativo BOOLEAN DEFAULT true NOT NULL,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (gerente_id) REFERENCES iam.usuarios(id) ON DELETE SET NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_org_projetos_nome ON org.projetos (nome)")

    # recursos
    op.execute("""
        CREATE TABLE IF NOT EXISTS org.recursos (
            id SERIAL NOT NULL,
            user_id INTEGER NOT NULL,
            projeto_id INTEGER NOT NULL,
            cargo_contexto VARCHAR(100),
            cor VARCHAR(7) DEFAULT '#3b82f6' NOT NULL,
            alocado BOOLEAN DEFAULT true NOT NULL,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (user_id) REFERENCES iam.usuarios(id),
            UNIQUE (user_id, projeto_id)
        )
    """)

    # tarefas
    op.execute("""
        CREATE TABLE IF NOT EXISTS org.tarefas (
            id SERIAL NOT NULL,
            titulo VARCHAR(255) NOT NULL,
            descricao TEXT,
            status VARCHAR(20) DEFAULT 'todo' NOT NULL,
            prioridade VARCHAR(10) DEFAULT 'medium' NOT NULL,
            data_inicio DATE NOT NULL,
            data_fim DATE NOT NULL,
            progresso INTEGER DEFAULT 0 NOT NULL,
            projeto_id INTEGER,
            responsavel_id INTEGER,
            ativo BOOLEAN DEFAULT true NOT NULL,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (projeto_id) REFERENCES org.projetos(id) ON DELETE CASCADE,
            FOREIGN KEY (responsavel_id) REFERENCES org.recursos(id) ON DELETE SET NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_org_tarefas_titulo ON org.tarefas (titulo)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_org_tarefas_projeto_id ON org.tarefas (projeto_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_org_tarefas_responsavel_id ON org.tarefas (responsavel_id)")

    # registros_tarefas
    op.execute("""
        CREATE TABLE IF NOT EXISTS org.registros_tarefas (
            id SERIAL NOT NULL,
            tarefa_id INTEGER NOT NULL,
            tipo VARCHAR(20) DEFAULT 'log' NOT NULL,
            conteudo TEXT NOT NULL,
            autor_id INTEGER,
            ativo BOOLEAN DEFAULT true NOT NULL,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (tarefa_id) REFERENCES org.tarefas(id) ON DELETE CASCADE,
            FOREIGN KEY (autor_id) REFERENCES org.recursos(id) ON DELETE SET NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_org_registros_tarefas_tarefa_id ON org.registros_tarefas (tarefa_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_org_registros_tarefas_autor_id ON org.registros_tarefas (autor_id)")


def downgrade() -> None:
    op.drop_table("registros_tarefas", schema="org")
    op.drop_table("tarefas", schema="org")
    op.drop_table("recursos", schema="org")
    op.drop_table("projetos", schema="org")
