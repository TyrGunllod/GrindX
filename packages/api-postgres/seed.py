"""
Script de seed — popula o banco com dados iniciais para desenvolvimento.

Uso:
    python seed.py

Cria (somente o que estiver faltando):
    - Empresa base GrindX
    - 1 usuário admin
    - 1 usuário operador
    - 1 usuário leitura
    - Abas Principal e Gestão
    - Módulos Dashboard, Usuários, Estrutura, Skins
"""

import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.database import Base
from app.models.empresa import Empresa
from app.models.portal import Aba, Modulo
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def seed_database():
    """Popula o banco com dados iniciais (idempotente)."""
    engine = create_engine(settings.DATABASE_URL)

    # Criar todas as tabelas
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("[START] Populando banco com dados iniciais...")

        # =========================================================
        # 1. Empresa base GrindX
        # =========================================================
        empresa_grindx = (
            session.query(Empresa).filter_by(dominio="grindx.local").first()
        )
        if not empresa_grindx:
            empresa_grindx = Empresa(
                nome="GrindX",
                dominio="grindx.local",
                ativo=True,
            )
            session.add(empresa_grindx)
            session.flush()
            print(f"[OK] Empresa GrindX criada (id={empresa_grindx.id})")
        else:
            print(f"[SKIP] Empresa GrindX já existe (id={empresa_grindx.id})")

        # =========================================================
        # 2. Usuários (vinculados à empresa GrindX)
        # =========================================================
        usuarios_seed = [
            {
                "username": "admin",
                "email": "admin@erp.com.br",
                "nome_completo": "Administrador",
                "senha": "admin123",
                "role": "admin",
            },
            {
                "username": "operador",
                "email": "operador@erp.com.br",
                "nome_completo": "Operador",
                "senha": "operador123",
                "role": "operador",
            },
            {
                "username": "leitura",
                "email": "leitura@erp.com.br",
                "nome_completo": "Leitura",
                "senha": "leitura123",
                "role": "leitura",
            },
        ]

        criados = 0
        for dados in usuarios_seed:
            usuario = (
                session.query(Usuario).filter_by(username=dados["username"]).first()
            )
            if not usuario:
                usuario = Usuario(
                    username=dados["username"],
                    email=dados["email"],
                    nome_completo=dados["nome_completo"],
                    senha_hash=gerar_hash_senha(dados["senha"]),
                    role=dados["role"],
                    empresa_id=empresa_grindx.id,
                )
                session.add(usuario)
                criados += 1
            else:
                # Vincular à empresa se ainda não tiver
                if usuario.empresa_id is None:
                    usuario.empresa_id = empresa_grindx.id

        session.flush()
        if criados > 0:
            print(f"[OK] Criados {criados} usuários")
        else:
            print("[SKIP] Todos os usuários já existem")

        # =========================================================
        # 3. Abas
        # =========================================================
        abas_seed = [
            {"nome": "Principal", "icone": "fas fa-th-large", "ordem": 0},
            {"nome": "Gestão", "icone": "fas fa-users-cog", "ordem": 100},
        ]

        abas_map = {}
        for dados in abas_seed:
            aba = session.query(Aba).filter_by(nome=dados["nome"]).first()
            if not aba:
                aba = Aba(
                    nome=dados["nome"], icone=dados["icone"], ordem=dados["ordem"]
                )
                session.add(aba)
                session.flush()
                print(f"[OK] Aba '{aba.nome}' criada")
            else:
                print(f"[SKIP] Aba '{aba.nome}' já existe")
            abas_map[dados["nome"]] = aba

        session.flush()

        # =========================================================
        # 4. Módulos
        # =========================================================
        modulos_seed = [
            {
                "aba": "Principal",
                "nome": "Dashboard",
                "slug": "home",
                "url": "modules/home/index.html",
                "icone": "fas fa-home",
            },
            {
                "aba": "Gestão",
                "nome": "Usuários",
                "slug": "users",
                "url": "modules/users/index.html",
                "icone": "fas fa-user-friends",
                "role_minima": "admin",
            },
            {
                "aba": "Gestão",
                "nome": "Módulos & Abas",
                "slug": "structure",
                "url": "modules/structure/index.html",
                "icone": "fas fa-cubes",
                "role_minima": "admin",
            },
            {
                "aba": "Gestão",
                "nome": "Skins",
                "slug": "admin-skins",
                "url": "modules/admin-skins/index.html",
                "icone": "fas fa-palette",
                "role_minima": "admin",
            },
        ]

        modulos_criados = 0
        for dados in modulos_seed:
            modulo = session.query(Modulo).filter_by(slug=dados["slug"]).first()
            if not modulo:
                aba = abas_map[dados["aba"]]
                modulo = Modulo(
                    aba_id=aba.id,
                    nome=dados["nome"],
                    slug=dados["slug"],
                    url=dados["url"],
                    icone=dados["icone"],
                    role_minima=dados.get("role_minima"),
                    ativo=True,
                )
                session.add(modulo)
                modulos_criados += 1

        session.flush()
        if modulos_criados > 0:
            print(f"[OK] Criados {modulos_criados} módulos")
        else:
            print("[SKIP] Todos os módulos já existem")

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
