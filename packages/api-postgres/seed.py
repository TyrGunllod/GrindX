"""
Script de seed — popula o banco com dados iniciais para desenvolvimento.

Uso:
    python seed.py

Cria:
    - 1 usuário admin
    - 1 usuário operador
    - 1 usuário leitura
"""

import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.database import Base
from app.models.portal import Aba, Modulo
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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
                Usuario(
                    username="admin",
                    email="admin@erp.com.br",
                    nome_completo="Administrador",
                    senha_hash=gerar_hash_senha("admin123"),
                    role="admin",
                ),
                Usuario(
                    username="operador",
                    email="operador@erp.com.br",
                    nome_completo="Operador",
                    senha_hash=gerar_hash_senha("operador123"),
                    role="operador",
                ),
                Usuario(
                    username="leitura",
                    email="leitura@erp.com.br",
                    nome_completo="Leitura",
                    senha_hash=gerar_hash_senha("leitura123"),
                    role="leitura",
                ),
            ]
            session.add_all(usuarios)
            print(f"[OK] Criados {len(usuarios)} usuários")
        else:
            print("[SKIP] Usuários já existem")

        # 2. Criar Estrutura do Portal
        if session.query(Aba).count() == 0:
            aba_principal = Aba(nome="Principal", icone="fas fa-th-large", ordem=0)
            aba_gestao = Aba(nome="Gestão", icone="fas fa-users-cog", ordem=100)
            session.add_all([aba_principal, aba_gestao])
            session.commit()

            mod_home = Modulo(
                aba_id=aba_principal.id,
                nome="Dashboard",
                slug="home",
                url="modules/home/index.html",
                icone="fas fa-home",
            )
            mod_users = Modulo(
                aba_id=aba_gestao.id,
                nome="Usuários",
                slug="users",
                url="modules/users/index.html",
                icone="fas fa-user-friends",
                role_minima="admin",
            )
            mod_struct = Modulo(
                aba_id=aba_gestao.id,
                nome="Módulos & Abas",
                slug="structure",
                url="modules/structure/index.html",
                icone="fas fa-cubes",
                role_minima="admin",
            )
            session.add_all([mod_home, mod_users, mod_struct])
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
