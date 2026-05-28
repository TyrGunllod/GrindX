"""
Testes unitários para o AuthService.

Testa autenticação, geração de tokens e refresh.
Usa mocks do repositório para não depender do banco.
"""

from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from shared.exceptions.base import (
    ConflictError,
    CredenciaisInvalidasError,
    TokenInvalidoError,
)
from shared.schemas.auth import TokenResponse
from shared.security.jwt import criar_jwt, gerar_hash_senha

from app.auth.service import AuthService
from app.models.usuario import Usuario


@pytest.fixture
def usuario_mock() -> Usuario:
    """Cria um usuário mock para testes."""
    usuario = MagicMock(spec=Usuario)
    usuario.id = 1
    usuario.username = "testuser"
    usuario.email = "test@example.com"
    usuario.nome_completo = "Test Usuario"
    usuario.senha_hash = gerar_hash_senha("senha123")
    usuario.role = "admin"
    usuario.ativo = True
    usuario.empresa_id = None
    return usuario


@pytest.fixture
def auth_service_mock() -> AuthService:
    """Cria AuthService com mock de repositório."""
    service = AuthService(MagicMock())  # Mock da sessão
    service.usuario_repo = MagicMock()  # Mock do repositório
    return service


class TestAuthServiceAutenticacao:
    """Testes de autenticação."""

    def test_autenticar_sucesso(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa autenticação bem-sucedida."""
        auth_service_mock.usuario_repo.buscar_por_username.return_value = usuario_mock

        resultado = auth_service_mock.autenticar("testuser", "senha123")

        assert isinstance(resultado, TokenResponse)
        assert resultado.access_token
        assert resultado.refresh_token
        assert resultado.token_type == "bearer"

    def test_autenticar_usuario_inexistente(self, auth_service_mock: AuthService):
        """Testa autenticação com usuário inexistente."""
        auth_service_mock.usuario_repo.buscar_por_username.return_value = None

        with pytest.raises(CredenciaisInvalidasError):
            auth_service_mock.autenticar("inexistente", "senha123")

    def test_autenticar_usuario_inativo(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa autenticação com usuário inativo."""
        usuario_mock.ativo = False
        auth_service_mock.usuario_repo.buscar_por_username.return_value = usuario_mock

        with pytest.raises(CredenciaisInvalidasError):
            auth_service_mock.autenticar("testuser", "senha123")

    def test_autenticar_senha_incorreta(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa autenticação com senha incorreta."""
        auth_service_mock.usuario_repo.buscar_por_username.return_value = usuario_mock

        with pytest.raises(CredenciaisInvalidasError):
            auth_service_mock.autenticar("testuser", "senha_errada")

    def test_autenticar_chama_repositorio(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa que autenticar chama o repositório corretamente."""
        auth_service_mock.usuario_repo.buscar_por_username.return_value = usuario_mock

        auth_service_mock.autenticar("testuser", "senha123")

        auth_service_mock.usuario_repo.buscar_por_username.assert_called_once_with(
            "testuser"
        )


class TestAuthServiceRefreshToken:
    """Testes de refresh de token."""

    def test_refresh_token_sucesso(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa refresh de token com sucesso."""
        from app.core.config import settings

        # Cria um token válido
        payload = {"sub": "1", "role": "admin"}
        refresh_token = criar_jwt(
            payload=payload,
            secret_key=settings.SECRET_KEY,
            expira_em=timedelta(days=7),
        )

        auth_service_mock.usuario_repo.buscar_por_id.return_value = usuario_mock

        resultado = auth_service_mock.refresh_token(refresh_token)

        assert isinstance(resultado, TokenResponse)
        assert resultado.access_token
        assert resultado.refresh_token

    def test_refresh_token_invalido(self, auth_service_mock: AuthService):
        """Testa refresh com token inválido."""
        with pytest.raises((TokenInvalidoError, CredenciaisInvalidasError)):
            auth_service_mock.refresh_token("token_invalido")

    def test_refresh_token_usuario_nao_existe(self, auth_service_mock: AuthService):
        """Testa refresh quando usuário foi deletado."""
        from app.core.config import settings

        payload = {"sub": "9999", "role": "admin"}
        refresh_token = criar_jwt(
            payload=payload,
            secret_key=settings.SECRET_KEY,
            expira_em=timedelta(days=7),
        )

        auth_service_mock.usuario_repo.buscar_por_id.return_value = None

        with pytest.raises(CredenciaisInvalidasError):
            auth_service_mock.refresh_token(refresh_token)

    def test_refresh_token_usuario_inativo(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa refresh quando usuário foi desativado."""
        from app.core.config import settings

        usuario_mock.ativo = False
        payload = {"sub": "1", "role": "admin"}
        refresh_token = criar_jwt(
            payload=payload,
            secret_key=settings.SECRET_KEY,
            expira_em=timedelta(days=7),
        )

        auth_service_mock.usuario_repo.buscar_por_id.return_value = usuario_mock

        with pytest.raises(CredenciaisInvalidasError):
            auth_service_mock.refresh_token(refresh_token)


class TestAuthServiceRegistro:
    """Testes de registro de novos usuários."""

    def test_registrar_usuario_sucesso(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa registro bem-sucedido de novo usuário."""
        auth_service_mock.usuario_repo.buscar_por_username.return_value = None
        auth_service_mock.usuario_repo.buscar_por_email.return_value = None
        auth_service_mock.usuario_repo.criar.return_value = usuario_mock

        resultado = auth_service_mock.registrar_usuario(
            username="novo_user",
            email="novo@example.com",
            nome_completo="Novo Usuario",
            senha="senha123",
            role="leitura",
        )

        assert resultado.id == usuario_mock.id
        assert resultado.username == "testuser"
        auth_service_mock.usuario_repo.criar.assert_called_once()

    def test_registrar_username_duplicado(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa registro com username duplicado."""
        auth_service_mock.usuario_repo.buscar_por_username.return_value = usuario_mock

        with pytest.raises(ConflictError):
            auth_service_mock.registrar_usuario(
                username="testuser",
                email="outro@example.com",
                nome_completo="Outro Usuario",
                senha="senha123",
            )

    def test_registrar_email_duplicado(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa registro com email duplicado."""
        auth_service_mock.usuario_repo.buscar_por_username.return_value = None
        auth_service_mock.usuario_repo.buscar_por_email.return_value = usuario_mock

        with pytest.raises(ConflictError):
            auth_service_mock.registrar_usuario(
                username="novo_user",
                email="test@example.com",
                nome_completo="Novo Usuario",
                senha="senha123",
            )

    def test_registrar_gera_hash_senha(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa que a senha é hasheada corretamente."""
        auth_service_mock.usuario_repo.buscar_por_username.return_value = None
        auth_service_mock.usuario_repo.buscar_por_email.return_value = None
        auth_service_mock.usuario_repo.criar.return_value = usuario_mock

        auth_service_mock.registrar_usuario(
            username="novo_user",
            email="novo@example.com",
            nome_completo="Novo Usuario",
            senha="minha_senha_secreta",
        )

        # Verifica que criar foi chamado com um usuário
        chamada = auth_service_mock.usuario_repo.criar.call_args
        usuario_criado = chamada[0][0]  # Primeiro argumento posicional

        # Verifica que a senha foi hashada (não é a mesma que foi passada)
        assert usuario_criado.senha_hash != "minha_senha_secreta"


class TestAuthServiceTokenGeração:
    """Testes de geração de tokens."""

    def test_gerar_tokens_contém_payload_correto(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa que tokens contêm payload correto."""
        from shared.security.jwt import verificar_jwt

        from app.core.config import settings

        tokens = auth_service_mock._gerar_tokens(usuario_mock)

        # Decodifica e verifica o payload
        payload = verificar_jwt(tokens.access_token, settings.SECRET_KEY)
        assert payload.sub == "1"
        assert payload.role == "admin"

    def test_access_token_expires_soon(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa que access_token tem expiration curta."""
        from shared.security.jwt import verificar_jwt

        from app.core.config import settings

        tokens = auth_service_mock._gerar_tokens(usuario_mock)
        payload = verificar_jwt(tokens.access_token, settings.SECRET_KEY)

        # Verifica que expiration foi setada
        assert payload.exp is not None

    def test_token_response_tem_bearer_type(
        self, auth_service_mock: AuthService, usuario_mock: Usuario
    ):
        """Testa que TokenResponse retorna tipo 'bearer'."""
        tokens = auth_service_mock._gerar_tokens(usuario_mock)
        assert tokens.token_type == "bearer"
