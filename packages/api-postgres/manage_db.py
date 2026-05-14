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

def main():
    """Executa CLI do Alembic."""
    # Garante que o diretório raiz está no path
    sys.path.insert(0, str(Path(__file__).parent))
    
    # Executa o comando do Alembic
    cli = CommandLine()
    cli.main()


if __name__ == "__main__":
    main()
