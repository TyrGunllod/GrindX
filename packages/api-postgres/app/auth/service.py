"""
Serviço de autenticação.

Responsável por autenticar usuários, gerar tokens JWT
e realizar refresh de tokens. Toda a persistência está no PostgreSQL.
"""

from datetime import timedelta

import structlog
from shared.exceptions.base import (
    ConflictError,
    CredenciaisInvalidasError,
    NotFoundError,
)
from shared.schemas.auth import TokenResponse
from shared.security.jwt import (
    criar_jwt,
    gerar_hash_senha,
    verificar_jwt,
    verificar_senha,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository

logger = structlog.get_logger(__name__)


class AuthService:
    """Serviço de autenticação e gestão de tokens JWT."""

    def __init__(self, db: Session) -> None:
        self.usuario_repo = UsuarioRepository(db)

    def autenticar(self, username: str, password: str) -> TokenResponse:
        """Autentica um usuário e retorna tokens JWT.

        Args:
            username: Nome de usuário.
            password: Senha em texto plano.

        Returns:
            TokenResponse com access_token e refresh_token.

        Raises:
            CredenciaisInvalidasError: Se username/senha estiverem incorretos
                ou o usuário estiver inativo.
        """
        usuario = self.usuario_repo.buscar_por_username(username)
        if not usuario:
            raise CredenciaisInvalidasError()

        if not usuario.ativo:
            raise CredenciaisInvalidasError()

        if not verificar_senha(password, usuario.senha_hash):
            raise CredenciaisInvalidasError()

        logger.info("Usuário autenticado", usuario_id=usuario.id, username=username)
        return self._gerar_tokens(usuario)

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Gera novos tokens a partir de um refresh token válido.

        Args:
            refresh_token: Token de refresh JWT.

        Returns:
            Novos TokenResponse com access_token e refresh_token.

        Raises:
            TokenInvalidoError: Se o refresh token for inválido.
            CredenciaisInvalidasError: Se o usuário não existir mais.
        """
        payload = verificar_jwt(refresh_token, settings.SECRET_KEY)

        usuario = self.usuario_repo.buscar_por_id(int(payload.sub))
        if not usuario or not usuario.ativo:
            raise CredenciaisInvalidasError()

        logger.info("Token renovado", usuario_id=usuario.id)
        return self._gerar_tokens(usuario)

    def registrar_usuario(
        self,
        username: str,
        email: str,
        nome_completo: str,
        senha: str,
        role: str = "leitura",
    ) -> Usuario:
        """Registra um novo usuário no sistema.

        Args:
            username: Nome de usuário único.
            email: E-mail único.
            nome_completo: Nome completo do usuário.
            senha: Senha em texto plano (será hashada).
            role: Perfil de acesso.

        Returns:
            Usuario criado.

        Raises:
            ConflictError: Se username ou email já existirem.
        """
        if self.usuario_repo.buscar_por_username(username):
            raise ConflictError(f"Username '{username}' já está em uso.")

        if self.usuario_repo.buscar_por_email(email):
            raise ConflictError(f"E-mail '{email}' já está cadastrado.")

        usuario = Usuario(
            username=username,
            email=email,
            nome_completo=nome_completo,
            senha_hash=gerar_hash_senha(senha),
            role=role,
        )

        usuario_criado = self.usuario_repo.criar(usuario)
        logger.info(
            "Usuário registrado",
            usuario_id=usuario_criado.id,
            username=username,
        )
        return usuario_criado

    def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> None:
        usuario = self.usuario_repo.buscar_por_id(user_id)
        if not usuario:
            raise NotFoundError(resource="Usuário", identifier=user_id)

        if not verificar_senha(current_password, usuario.senha_hash):
            raise CredenciaisInvalidasError()

        usuario.senha_hash = gerar_hash_senha(new_password)
        self.usuario_repo.atualizar(usuario, {"senha_hash": usuario.senha_hash})

        logger.info(
            "senha_alterada",
            usuario_id=usuario.id,
            username=usuario.username,
        )

    def _gerar_tokens(self, usuario: Usuario) -> TokenResponse:
        """Gera par de tokens JWT (access + refresh) para um usuário.

        Args:
            usuario: Instância do modelo Usuario.

        Returns:
            TokenResponse com os tokens gerados.
        """
        payload = {
            "sub": str(usuario.id),
            "role": usuario.role,
            "company_id": usuario.empresa_id,
        }

        access_token = criar_jwt(
            payload=payload,
            secret_key=settings.SECRET_KEY,
            expira_em=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        refresh_token = criar_jwt(
            payload=payload,
            secret_key=settings.SECRET_KEY,
            expira_em=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
