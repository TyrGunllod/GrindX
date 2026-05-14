"""
Script de seed — popula o banco com dados iniciais para desenvolvimento.

Uso:
    python seed.py

Cria:
    - 1 usuário admin
    - 1 usuário operador
    - 1 usuário leitura
    - 5 produtos de exemplo
"""

import sys
from pathlib import Path
from decimal import Decimal

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.usuario import Usuario
from app.models.produto import Produto
from app.database import Base
from shared.security.jwt import gerar_hash_senha


def seed_database():
    """Popula o banco com dados iniciais."""
    # Criar engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Criar todas as tabelas
    Base.metadata.create_all(engine)
    
    # Criar sessão
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Verificar se já existe dados
        usuario_count = session.query(Usuario).count()
        if usuario_count > 0:
            print("[INFO] Banco já possui usuários. Abortando seed.")
            return

        print("[START] Populando banco com dados iniciais...")

        # Criar usuários
        usuarios = [
            Usuario(
                username="admin",
                email="admin@erp.local",
                nome_completo="Administrador",
                senha_hash=gerar_hash_senha("admin123"),
                role="admin",
            ),
            Usuario(
                username="operador",
                email="operador@erp.local",
                nome_completo="Operador do Sistema",
                senha_hash=gerar_hash_senha("operador123"),
                role="operador",
            ),
            Usuario(
                username="leitura",
                email="leitura@erp.local",
                nome_completo="Usuário de Leitura",
                senha_hash=gerar_hash_senha("leitura123"),
                role="leitura",
            ),
        ]
        session.add_all(usuarios)
        session.commit()
        print(f"[OK] Criados {len(usuarios)} usuários")

        # Criar produtos de exemplo
        produtos = [
            Produto(
                nome="Caneta Esferográfica Azul",
                descricao="Caneta esferográfica ponta fina, tinta azul",
                preco=Decimal("2.50"),
            ),
            Produto(
                nome="Caderno 200 Folhas",
                descricao="Caderno com 200 folhas, pauta",
                preco=Decimal("15.90"),
            ),
            Produto(
                nome="Lápis HB",
                descricao="Lápis grafite HB, caixa com 12 unidades",
                preco=Decimal("8.50"),
            ),
            Produto(
                nome="Borracha Branca",
                descricao="Borracha branca para lápis, sem PVC",
                preco=Decimal("1.20"),
            ),
            Produto(
                nome="Régua 30cm",
                descricao="Régua de plástico transparente, 30 centímetros",
                preco=Decimal("3.00"),
            ),
        ]
        session.add_all(produtos)
        session.commit()
        print(f"[OK] Criados {len(produtos)} produtos")

        print("\n[FINISH] Seed concluído com sucesso!")
        print("\nCredenciais para teste:")
        print("  admin    / admin123")
        print("  operador / operador123")
        print("  leitura  / leitura123")

    except Exception as e:
        print(f"[ERROR] Erro ao fazer seed: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
