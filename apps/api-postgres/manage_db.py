#!/usr/bin/env python
"""
CLI para gerenciar migrações com Alembic.

Uso:
    python manage_db.py upgrade          # Aplica todas as migrations pendentes
    python manage_db.py downgrade -1     # Desfaz a última migration
    python manage_db.py current          # Mostra a versão atual do banco
    python manage_db.py history          # Lista todas as migrations
    python manage_db.py revision -m "descrição"  # Cria nova migration
"""

import sys
from pathlib import Path

from alembic.config import CommandLine
from sqlalchemy import create_engine, text


def _ensure_database() -> None:
    """Cria o banco de dados se não existir (PostgreSQL apenas)."""
    from app.core.config import settings

    url = settings.DATABASE_URL
    if not url or not url.startswith("postgresql"):
        return

    # Extrai o nome do banco da URL
    db_name = url.rstrip("/").rsplit("/", 1)[-1].split("?")[0]
    if not db_name:
        return

    # Conecta no banco de manutenção 'postgres' com autocommit
    maintenance_url = url.rsplit("/", 1)[0] + "/postgres"
    engine = create_engine(maintenance_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                print(f"✓ Banco '{db_name}' criado.")
    finally:
        engine.dispose()


def main():
    """Executa CLI do Alembic, criando o banco primeiro se necessário."""
    sys.path.insert(0, str(Path(__file__).parent))

    _ensure_database()

    cli = CommandLine()
    cli.main()


if __name__ == "__main__":
    main()
