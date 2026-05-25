"""
Script de seed — popula o banco com dados iniciais para desenvolvimento.

Uso:
    python seed.py

Cria (somente o que estiver faltando):
    - Database PostgreSQL (se não existir)
    - Empresa base GrindX
    - 1 usuário admin
    - Skin padrão GrindX (ativa)
    - Abas Principal e Gestão
    - Módulos Dashboard, Usuários, Estrutura, Skins
"""

import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from urllib.parse import urlparse

from app.core.config import settings
from app.database import Base
from app.models.empresa import Empresa
from app.models.portal import Aba, Modulo
from app.models.usuario import Usuario
from shared.security.jwt import gerar_hash_senha
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Guard: Verificar se DEBUG está ativo
if not settings.DEBUG:
    print("ERRO: seed.py só pode rodar com DEBUG=true. Abortando.")
    raise SystemExit(1)


def _criar_database_se_nao_existir():
    """Cria o database PostgreSQL caso ainda não exista."""
    url = urlparse(settings.DATABASE_URL)
    db_name = url.path.lstrip("/")

    # Conecta ao database padrão 'postgres' para criar o database alvo
    base_url = f"{url.scheme}://{url.hostname}:{url.port or 5432}/postgres"
    if url.username:
        base_url = f"{url.scheme}://{url.username}:{url.password}@{url.hostname}:{url.port or 5432}/postgres"

    try:
        engine = create_engine(base_url, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db"),
                {"db": db_name},
            )
            if not result.fetchone():
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                print(f"[OK] Database '{db_name}' criado")
            else:
                print(f"[SKIP] Database '{db_name}' já existe")
        engine.dispose()
    except Exception as e:
        print(f"[OK] Não foi possível verificar/criar database (pode já existir): {e}")


def seed_database():
    """Popula o banco com dados iniciais (idempotente)."""
    _criar_database_se_nao_existir()

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

        # Vincular qualquer usuário existente que não tenha empresa
        sem_empresa = (
            session.query(Usuario).filter(Usuario.empresa_id.is_(None)).count()
        )
        if sem_empresa:
            session.query(Usuario).filter(Usuario.empresa_id.is_(None)).update(
                {"empresa_id": empresa_grindx.id}
            )
            session.flush()
            print(f"[OK] Vinculados {sem_empresa} usuário(s) à empresa GrindX")
        else:
            print("[SKIP] Todos os usuários já possuem empresa")

        # =========================================================
        # 3. Skin padrão GrindX
        # =========================================================
        from app.models.theme import CompanyTheme

        tema_padrao = (
            session.query(CompanyTheme)
            .filter_by(company_id=empresa_grindx.id, name="Padrão GrindX")
            .first()
        )
        if not tema_padrao:
            tema_padrao = CompanyTheme(
                company_id=empresa_grindx.id,
                name="Padrão GrindX",
                is_active=True,
                colors={
                    "--skin-primary": "#2563eb",
                    "--skin-primary-hover": "#1d4ed8",
                    "--skin-danger": "#dc2626",
                    "--skin-success": "#16a34a",
                    "--skin-warning": "#ca8a04",
                    "--skin-bg-main": "#f8fafc",
                    "--skin-bg-card": "#ffffff",
                    "--skin-text-main": "#1e293b",
                    "--skin-text-muted": "#64748b",
                    "--skin-border-color": "#e2e8f0",
                    "--skin-focus-ring": "rgba(37, 99, 235, 0.35)",
                    "--skin-bg-main-dark": "#0f172a",
                    "--skin-bg-card-dark": "#1e293b",
                    "--skin-text-main-dark": "#f8fafc",
                    "--skin-text-muted-dark": "#94a3b8",
                    "--skin-border-color-dark": "rgba(255, 255, 255, 0.05)",
                },
                fonts={"heading": "Barlow Condensed", "body": "DM Sans"},
                icon_library="fontawesome",
                tokens={
                    "--skin-radius-sm": "0.25rem",
                    "--skin-radius-md": "0.5rem",
                    "--skin-radius-lg": "0.75rem",
                    "--skin-radius-xl": "1.5rem",
                    "--skin-shadow-card": "0 10px 25px rgba(0,0,0,0.1)",
                    "--skin-shadow-modal": "0 20px 25px -5px rgba(0,0,0,0.2)",
                },
                logo_url="/uploads/logos/a551e19f-857e-4f58-b7ac-74de9fa8d108.png",
                company_name="GrindX",
                copyright_text="© 2026 GrindX. Todos os direitos reservados.",
            )
            session.add(tema_padrao)
            session.flush()
            print(f"[OK] Skin padrão 'Padrão GrindX' criada (id={tema_padrao.id})")
        else:
            if tema_padrao.logo_url != "/uploads/logos/a551e19f-857e-4f58-b7ac-74de9fa8d108.png":
                tema_padrao.logo_url = "/uploads/logos/a551e19f-857e-4f58-b7ac-74de9fa8d108.png"
                print("[UPDATE] logo_url atualizado na skin 'Padrão GrindX'")
            print("[SKIP] Skin padrão 'Padrão GrindX' já existe")

        # =========================================================
        # 5. Abas
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
        # 6. Módulos
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

    except Exception as e:
        print(f"[ERROR] Erro ao fazer seed: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
