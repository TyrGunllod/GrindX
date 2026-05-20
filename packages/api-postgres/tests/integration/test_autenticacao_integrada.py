"""
Testes de integração para autenticação e repositório.

Testa o fluxo completo: criar usuário → autenticar → gerar tokens.
Usa banco SQLite em memória.
"""

import pytest
from app.auth.service import AuthService
from app.core.config import settings
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from fastapi.testclient import TestClient
from shared.exceptions.base import ConflictError, CredenciaisInvalidasError
from shared.security.jwt import gerar_hash_senha, verificar_jwt


class TestAutenticacaoIntegrada:
    """Testes de integração do fluxo de autenticação."""

    def test_criar_usuario_e_autenticar(self, db_session):
        """Testa fluxo completo: criar usuário → autenticar."""
        # 1. Criar usuário no banco
        usuario_repo = UsuarioRepository(db_session)
        auth_service = AuthService(db_session)

        usuario = Usuario(
            username="pedro",
            email="pedro@example.com",
            nome_completo="Pedro Silva",
            senha_hash=gerar_hash_senha("senha_forte_123"),
            role="operador",
        )
        usuario_criado = usuario_repo.criar(usuario)
        assert usuario_criado.id is not None

        # 2. Autenticar com as credenciais
        tokens = auth_service.autenticar("pedro", "senha_forte_123")
        assert tokens.access_token
        assert tokens.refresh_token

        # 3. Decodificar e validar token
        payload = verificar_jwt(tokens.access_token, settings.SECRET_KEY)
        assert payload.sub == str(usuario_criado.id)
        assert payload.role == "operador"

    def test_autenticacao_falha_com_senha_errada(self, db_session):
        """Testa que autenticação falha com senha incorreta."""
        usuario_repo = UsuarioRepository(db_session)
        auth_service = AuthService(db_session)

        usuario = Usuario(
            username="maria",
            email="maria@example.com",
            nome_completo="Maria Santos",
            senha_hash=gerar_hash_senha("senha_correta"),
            role="admin",
        )
        usuario_repo.criar(usuario)

        with pytest.raises(CredenciaisInvalidasError):
            auth_service.autenticar("maria", "senha_incorreta")

    def test_registrar_usuario_e_autenticar(self, db_session):
        """Testa fluxo: registrar usuário via service → autenticar."""
        auth_service = AuthService(db_session)

        # 1. Registrar novo usuário
        usuario_criado = auth_service.registrar_usuario(
            username="joao",
            email="joao@example.com",
            nome_completo="João Costa",
            senha="minha_senha_segura",
            role="leitura",
        )
        assert usuario_criado.id is not None
        assert usuario_criado.username == "joao"

        # 2. Autenticar com as credenciais cadastradas
        tokens = auth_service.autenticar("joao", "minha_senha_segura")
        assert tokens.access_token

        # 3. Verificar role no token
        payload = verificar_jwt(tokens.access_token, settings.SECRET_KEY)
        assert payload.role == "leitura"

    def test_refresh_token_fluxo_completo(self, db_session):
        """Testa fluxo completo de refresh."""
        auth_service = AuthService(db_session)

        # 1. Registrar e autenticar
        auth_service.registrar_usuario(
            username="carlos",
            email="carlos@example.com",
            nome_completo="Carlos Mendes",
            senha="senha_teste",
        )
        tokens_iniciais = auth_service.autenticar("carlos", "senha_teste")

        # 2. Usar refresh token para gerar novos tokens
        import time

        time.sleep(1.1)
        tokens_novos = auth_service.refresh_token(tokens_iniciais.refresh_token)

        # 3. Validar que novo access_token é diferente
        assert tokens_novos.access_token != tokens_iniciais.access_token

        # 4. Validar que novo token é válido
        payload = verificar_jwt(tokens_novos.access_token, settings.SECRET_KEY)
        assert payload.sub  # Tem user ID


class TestRotasAutenticacao:
    """Testes de integração dos endpoints de autenticação."""

    def test_login_endpoint_sucesso(self, client: TestClient, db_session):
        """Testa POST /v1/auth/token com credenciais válidas."""
        # 1. Criar usuário
        usuario_repo = UsuarioRepository(db_session)
        usuario = Usuario(
            username="testuser",
            email="test@example.com",
            nome_completo="Test User",
            senha_hash=gerar_hash_senha("senha123"),
            role="admin",
        )
        usuario_repo.criar(usuario)

        # 2. Fazer login
        response = client.post(
            "/v1/auth/token",
            json={"username": "testuser", "password": "senha123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_endpoint_credenciais_invalidas(self, client: TestClient):
        """Testa login com credenciais inválidas."""
        response = client.post(
            "/v1/auth/token",
            json={"username": "inexistente", "password": "senha_invalida"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "NAO_AUTORIZADO"

    def test_refresh_endpoint_sucesso(
        self, client: TestClient, auth_headers: dict, db_session
    ):
        """Testa POST /v1/auth/refresh com refresh_token válido."""
        # auth_headers já cria um usuário e obtém tokens
        # Agora extrair o refresh_token
        usuario_repo = UsuarioRepository(db_session)
        auth_service = AuthService(db_session)

        usuario = Usuario(
            username="refresh_test",
            email="refresh@example.com",
            nome_completo="Refresh Test",
            senha_hash=gerar_hash_senha("senha123"),
            role="admin",
        )
        usuario_repo.criar(usuario)
        tokens = auth_service.autenticar("refresh_test", "senha123")

        # Fazer refresh
        response = client.post(
            "/v1/auth/refresh",
            json={"refresh_token": tokens.refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_endpoint_token_invalido(self, client: TestClient):
        """Testa refresh com token inválido."""
        response = client.post(
            "/v1/auth/refresh",
            json={"refresh_token": "token_invalido"},
        )

        assert response.status_code == 401


class TestDesativacaoUsuario:
    """Testes de autenticação após desativação de usuário."""

    def test_usuario_desativado_nao_pode_autenticar(self, db_session):
        """Testa que usuário desativado não consegue fazer login."""
        usuario_repo = UsuarioRepository(db_session)
        auth_service = AuthService(db_session)

        # Criar e desativar usuário
        usuario = Usuario(
            username="user_desativado",
            email="desativado@example.com",
            nome_completo="User Desativado",
            senha_hash=gerar_hash_senha("senha123"),
        )
        usuario_criado = usuario_repo.criar(usuario)
        usuario_repo.desativar(usuario_criado)

        # Tentar autenticar
        with pytest.raises(CredenciaisInvalidasError):
            auth_service.autenticar("user_desativado", "senha123")

    def test_usuario_desativado_nao_pode_fazer_refresh(self, db_session):
        """Testa que usuário desativado não consegue fazer refresh."""
        usuario_repo = UsuarioRepository(db_session)
        auth_service = AuthService(db_session)

        # Criar usuário e gerar tokens
        usuario = Usuario(
            username="user_refresh_desativado",
            email="refresh_desativado@example.com",
            nome_completo="User Refresh Desativado",
            senha_hash=gerar_hash_senha("senha123"),
        )
        usuario_criado = usuario_repo.criar(usuario)
        tokens = auth_service.autenticar("user_refresh_desativado", "senha123")

        # Desativar usuário
        usuario_repo.desativar(usuario_criado)

        # Tentar fazer refresh
        with pytest.raises(CredenciaisInvalidasError):
            auth_service.refresh_token(tokens.refresh_token)


class TestRegistroDuplicado:
    """Testes de validações de unicidade no registro."""

    def test_nao_permite_username_duplicado(self, db_session):
        """Testa que não é permitido registrar username duplicado."""
        auth_service = AuthService(db_session)

        # Primeiro registro
        auth_service.registrar_usuario(
            username="duplicado",
            email="primeiro@example.com",
            nome_completo="Primeiro Usuario",
            senha="senha123",
        )

        # Segundo com mesmo username
        with pytest.raises(ConflictError):
            auth_service.registrar_usuario(
                username="duplicado",
                email="segundo@example.com",
                nome_completo="Segundo Usuario",
                senha="senha123",
            )

    def test_nao_permite_email_duplicado(self, db_session):
        """Testa que não é permitido registrar email duplicado."""
        auth_service = AuthService(db_session)

        # Primeiro registro
        auth_service.registrar_usuario(
            username="user1",
            email="duplicado@example.com",
            nome_completo="Primeiro Usuario",
            senha="senha123",
        )

        # Segundo com mesmo email
        with pytest.raises(ConflictError):
            auth_service.registrar_usuario(
                username="user2",
                email="duplicado@example.com",
                nome_completo="Segundo Usuario",
                senha="senha123",
            )
