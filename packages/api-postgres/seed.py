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
from app.models.portal import Aba, Modulo
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
        print("[START] Populando banco com dados iniciais...")

        # 1. Criar usuários
        if session.query(Usuario).count() == 0:
            usuarios = [
                Usuario(username="admin", email="admin@erp.local", nome_completo="Administrador", senha_hash=gerar_hash_senha("admin123"), role="admin"),
                Usuario(username="operador", email="operador@erp.local", nome_completo="Operador", senha_hash=gerar_hash_senha("operador123"), role="operador"),
                Usuario(username="leitura", email="leitura@erp.local", nome_completo="Leitura", senha_hash=gerar_hash_senha("leitura123"), role="leitura"),
            ]
            session.add_all(usuarios)
            print(f"[OK] Criados {len(usuarios)} usuários")
        else:
            print("[SKIP] Usuários já existem")

        # 2. Criar produtos
        if session.query(Produto).count() == 0:
            produtos = [
                Produto(nome="Caneta Azul", descricao="Caneta", preco=Decimal("2.50")),
                Produto(nome="Caderno", descricao="Caderno", preco=Decimal("15.90")),
            ]
            session.add_all(produtos)
            print(f"[OK] Criados produtos")
        else:
            print("[SKIP] Produtos já existem")

        # 3. Criar Estrutura do Portal
        if session.query(Aba).count() == 0:
            aba_principal = Aba(nome="Principal", icone="fas fa-th-large", ordem=1)
            aba_gestao = Aba(nome="Gestão", icone="fas fa-users-cog", ordem=2)
            session.add_all([aba_principal, aba_gestao])
            session.commit()

            mod_home = Modulo(aba_id=aba_principal.id, nome="Dashboard", slug="home", url="modules/home/index.html", icone="fas fa-home")
            mod_users = Modulo(aba_id=aba_gestao.id, nome="Usuários", slug="users", url="modules/users/index.html", icone="fas fa-user-friends", role_minima="admin")
            session.add_all([mod_home, mod_users])
            print("[OK] Estrutura do Portal criada")
        else:
            print("[SKIP] Estrutura do portal já existe")

        session.commit()
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
