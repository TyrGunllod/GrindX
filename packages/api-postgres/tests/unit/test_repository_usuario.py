"""
Testes unitários para o UsuarioRepository.

Testa operações CRUD, queries e validações sem depender de serviços.
Usa banco SQLite em memória via fixture db_session.
"""

import pytest
from shared.security.jwt import gerar_hash_senha
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository


@pytest.fixture
def repository(db_session: Session) -> UsuarioRepository:
    """Factory para UsuarioRepository com sessão de teste."""
    return UsuarioRepository(db_session)


@pytest.fixture
def usuario_base(db_session: Session) -> Usuario:
    """Cria um usuário base para testes."""
    usuario = Usuario(
        username="admin",
        email="admin@example.com",
        nome_completo="Admin Usuario",
        senha_hash=gerar_hash_senha("senha123"),
        role="admin",
        ativo=True,
    )
    db_session.add(usuario)
    db_session.commit()
    return usuario


class TestUsuarioRepositoryBusca:
    """Testes de busca de usuários."""

    def test_buscar_por_id_encontra_usuario(
        self, repository: UsuarioRepository, usuario_base: Usuario
    ):
        """Testa busca de usuário pelo ID."""
        resultado = repository.buscar_por_id(usuario_base.id)
        assert resultado is not None
        assert resultado.id == usuario_base.id
        assert resultado.username == "admin"

    def test_buscar_por_id_nao_encontra(self, repository: UsuarioRepository):
        """Testa busca com ID inexistente."""
        resultado = repository.buscar_por_id(9999)
        assert resultado is None

    def test_buscar_por_username_encontra(
        self, repository: UsuarioRepository, usuario_base: Usuario
    ):
        """Testa busca de usuário pelo username."""
        resultado = repository.buscar_por_username("admin")
        assert resultado is not None
        assert resultado.id == usuario_base.id

    def test_buscar_por_username_case_sensitive(self, repository: UsuarioRepository):
        """Testa que busca por username é case-sensitive."""
        resultado = repository.buscar_por_username("ADMIN")
        assert resultado is None

    def test_buscar_por_email_encontra(
        self, repository: UsuarioRepository, usuario_base: Usuario
    ):
        """Testa busca de usuário pelo email."""
        resultado = repository.buscar_por_email("admin@example.com")
        assert resultado is not None
        assert resultado.id == usuario_base.id

    def test_buscar_por_email_nao_encontra(self, repository: UsuarioRepository):
        """Testa busca com email inexistente."""
        resultado = repository.buscar_por_email("inexistente@example.com")
        assert resultado is None


class TestUsuarioRepositoryCrud:
    """Testes de operações CRUD."""

    def test_criar_usuario_novo(
        self, repository: UsuarioRepository, db_session: Session
    ):
        """Testa criação de novo usuário."""
        usuario = Usuario(
            username="novo_user",
            email="novo@example.com",
            nome_completo="Novo Usuario",
            senha_hash=gerar_hash_senha("senha456"),
            role="operador",
        )
        resultado = repository.criar(usuario)

        assert resultado.id is not None
        assert resultado.username == "novo_user"

        # Verifica que foi persistido no banco
        verificacao = repository.buscar_por_username("novo_user")
        assert verificacao is not None

    def test_atualizar_usuario(
        self, repository: UsuarioRepository, usuario_base: Usuario
    ):
        """Testa atualização de usuário."""
        dados_atualizacao = {
            "nome_completo": "Admin Atualizado",
            "role": "operador",
        }
        resultado = repository.atualizar(usuario_base, dados_atualizacao)

        assert resultado.nome_completo == "Admin Atualizado"
        assert resultado.role == "operador"

        # Verifica persistência
        verificacao = repository.buscar_por_id(usuario_base.id)
        assert verificacao.role == "operador"

    def test_desativar_usuario(
        self, repository: UsuarioRepository, usuario_base: Usuario
    ):
        """Testa soft delete (desativação) de usuário."""
        resultado = repository.desativar(usuario_base)

        assert resultado.ativo is False

        # Verifica persistência
        verificacao = repository.buscar_por_id(usuario_base.id)
        assert verificacao.ativo is False

    def test_deletar_usuario(
        self, repository: UsuarioRepository, usuario_base: Usuario
    ):
        """Testa hard delete de usuário."""
        usuario_id = usuario_base.id
        repository.deletar(usuario_base)

        # Verifica que foi removido
        resultado = repository.buscar_por_id(usuario_id)
        assert resultado is None


class TestUsuarioRepositoryListagem:
    """Testes de listagem e paginação."""

    @pytest.fixture
    def usuarios_multiplos(self, db_session: Session):
        """Cria múltiplos usuários para testes de paginação."""
        usuarios = []
        for i in range(1, 6):
            usuario = Usuario(
                username=f"user{i}",
                email=f"user{i}@example.com",
                nome_completo=f"Usuario {i}",
                senha_hash=gerar_hash_senha("senha123"),
                role="leitura" if i % 2 == 0 else "operador",
                ativo=True if i != 5 else False,
            )
            db_session.add(usuario)
            usuarios.append(usuario)
        db_session.commit()
        return usuarios

    def test_listar_ativos(
        self, repository: UsuarioRepository, usuarios_multiplos: list
    ):
        """Testa listagem de usuários ativos."""
        items, total = repository.listar_ativos()

        assert total == 4  # user1-4 ativos, user5 desativado
        assert len(items) == 4

    def test_listar_ativos_paginado(
        self, repository: UsuarioRepository, usuarios_multiplos: list
    ):
        """Testa paginação de usuários ativos."""
        items_page1, total = repository.listar_ativos(page=1, page_size=2)
        assert len(items_page1) == 2
        assert total == 4

        items_page2, _ = repository.listar_ativos(page=2, page_size=2)
        assert len(items_page2) == 2
        assert items_page1[0].username != items_page2[0].username

    def test_listar_todos(
        self, repository: UsuarioRepository, usuarios_multiplos: list
    ):
        """Testa listagem de todos os usuários."""
        items, total = repository.listar_todos()

        assert total == 5
        assert len(items) == 5

    def test_listar_por_role(
        self, repository: UsuarioRepository, usuarios_multiplos: list
    ):
        """Testa filtro por role."""
        # 3 usuários com role "operador" (user1, user3, user5)
        items_operador, total_operador = repository.listar_por_role("operador")
        assert total_operador == 3

        # 2 usuários com role "leitura" (user2, user4)
        items_leitura, total_leitura = repository.listar_por_role("leitura")
        assert total_leitura == 2

    def test_listagem_ordenada_por_username(
        self, repository: UsuarioRepository, usuarios_multiplos: list
    ):
        """Testa que listagens são ordenadas por username."""
        items, _ = repository.listar_todos()

        usernames = [u.username for u in items]
        assert usernames == sorted(usernames)


class TestUsuarioRepositoryValidacoes:
    """Testes de validações implícitas (constraints do banco)."""

    def test_username_unico(
        self, repository: UsuarioRepository, usuario_base: Usuario, db_session: Session
    ):
        """Testa constraint de unicidade do username."""
        usuario_duplicado = Usuario(
            username="admin",  # username duplicado
            email="outro@example.com",
            nome_completo="Outro Usuario",
            senha_hash=gerar_hash_senha("senha789"),
        )

        with pytest.raises(Exception):  # IntegrityError do SQLAlchemy
            repository.criar(usuario_duplicado)

    def test_email_unico(self, repository: UsuarioRepository, usuario_base: Usuario):
        """Testa constraint de unicidade do email."""
        usuario_duplicado = Usuario(
            username="outro_user",
            email="admin@example.com",  # email duplicado
            nome_completo="Outro Usuario",
            senha_hash=gerar_hash_senha("senha789"),
        )

        with pytest.raises(Exception):  # IntegrityError do SQLAlchemy
            repository.criar(usuario_duplicado)
