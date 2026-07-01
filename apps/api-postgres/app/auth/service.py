"""
Serviço de autenticação.

Responsável por autenticar usuários, gerar tokens JWT
e realizar refresh de tokens. Toda a persistência está no PostgreSQL.
"""

import secrets
import string
from datetime import datetime, timedelta, timezone

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

        # Check regular password first
        password_ok = verificar_senha(password, usuario.senha_hash)

        # If regular password fails, check temp password
        if not password_ok and usuario.temp_password_hash:
            password_ok = verificar_senha(password, usuario.temp_password_hash)

            if password_ok:
                # Check if temp password has expired
                expires_at = usuario.expires_at

                # Fail-closed: if temp password exists but no expiry, reject
                if expires_at is None:
                    self.usuario_repo.atualizar(
                        usuario,
                        {"temp_password_hash": None, "expires_at": None},
                    )
                    raise CredenciaisInvalidasError(
                        "Senha temporária expirada. Solicite uma nova."
                    )

                # Handle SQLite naive datetimes
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)

                if expires_at < datetime.now(timezone.utc):
                    # Clear expired temp fields
                    self.usuario_repo.atualizar(
                        usuario,
                        {"temp_password_hash": None, "expires_at": None},
                    )
                    raise CredenciaisInvalidasError(
                        "Senha temporária expirada. Solicite uma nova."
                    )

                # Valid temp password - clear temp fields and update main password
                usuario.senha_hash = gerar_hash_senha(password)
                self.usuario_repo.atualizar(
                    usuario,
                    {
                        "senha_hash": usuario.senha_hash,
                        "temp_password_hash": None,
                        "expires_at": None,
                    },
                )

        if not password_ok:
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

    def update_profile(
        self,
        user_id: int,
        email: str | None = None,
        nome_completo: str | None = None,
        theme_preference: str | None = None,
        layout_preference: str | None = None,
        codigo: str | None = None,
        cbo: str | None = None,
        departamento: str | None = None,
        cargo: str | None = None,
        classificacao: str | None = None,
        cpf: str | None = None,
        rg: str | None = None,
        salario: str | None = None,
        endereco: str | None = None,
        numero: str | None = None,
        cep: str | None = None,
        telefone: str | None = None,
        celular: str | None = None,
    ) -> Usuario:
        """Atualiza o perfil do próprio usuário."""
        usuario = self.usuario_repo.buscar_por_id(user_id)
        if not usuario:
            raise NotFoundError(resource="Usuário", identifier=user_id)

        dados: dict[str, str] = {}
        if email is not None:
            if email != usuario.email:
                existing = self.usuario_repo.buscar_por_email(email)
                if existing:
                    raise ConflictError(f"E-mail '{email}' já está em uso")
            dados["email"] = email
        if nome_completo is not None:
            dados["nome_completo"] = nome_completo
        if theme_preference is not None:
            dados["theme_preference"] = theme_preference
        if layout_preference is not None:
            dados["layout_preference"] = layout_preference
        if codigo is not None:
            dados["codigo"] = codigo
        if cbo is not None:
            dados["cbo"] = cbo
        if departamento is not None:
            dados["departamento"] = departamento
        if cargo is not None:
            dados["cargo"] = cargo
        if classificacao is not None:
            dados["classificacao"] = classificacao
        if cpf is not None:
            dados["cpf"] = cpf
        if rg is not None:
            dados["rg"] = rg
        if salario is not None:
            dados["salario"] = salario
        if endereco is not None:
            dados["endereco"] = endereco
        if numero is not None:
            dados["numero"] = numero
        if cep is not None:
            dados["cep"] = cep
        if telefone is not None:
            dados["telefone"] = telefone
        if celular is not None:
            dados["celular"] = celular

        if not dados:
            return usuario

        usuario_atualizado = self.usuario_repo.atualizar(usuario, dados)
        logger.info(
            "perfil_atualizado",
            usuario_id=user_id,
            campos_alterados=list(dados.keys()),
        )
        return usuario_atualizado

    def forgot_password(self, username: str) -> tuple[str, str, str]:
        usuario = self.usuario_repo.buscar_por_username(username)
        if not usuario:
            raise NotFoundError(resource="Usuário", identifier=username)

        # Generate cryptographically secure temp password (16 alphanumeric chars)
        alphabet = string.ascii_letters + string.digits
        temp_password = "".join(secrets.choice(alphabet) for _ in range(16))

        # Hash and store temp password with expiry
        temp_hash = gerar_hash_senha(temp_password)
        usuario.temp_password_hash = temp_hash
        usuario.expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        self.usuario_repo.atualizar(
            usuario,
            {
                "temp_password_hash": usuario.temp_password_hash,
                "expires_at": usuario.expires_at,
            },
        )

        logger.info(
            "senha_temporaria_gerada",
            usuario_id=usuario.id,
            expires_at=usuario.expires_at.isoformat(),
        )
        return usuario.email, usuario.nome_completo, temp_password

    def apply_temp_password(self, username: str, temp_password: str) -> None:
        usuario = self.usuario_repo.buscar_por_username(username)
        if not usuario:
            raise NotFoundError(resource="Usuário", identifier=username)

        # Check if temp password has expired
        expires_at = usuario.expires_at

        # Fail-closed: if temp password exists but no expiry, reject
        if expires_at is None:
            self.usuario_repo.atualizar(
                usuario,
                {"temp_password_hash": None, "expires_at": None},
            )
            raise CredenciaisInvalidasError("Senha temporária expirada")

        # Handle SQLite naive datetimes
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            # Clear expired temp fields
            self.usuario_repo.atualizar(
                usuario,
                {"temp_password_hash": None, "expires_at": None},
            )
            raise CredenciaisInvalidasError("Senha temporária expirada")

        # Verify temp password
        if not usuario.temp_password_hash or not verificar_senha(
            temp_password, usuario.temp_password_hash
        ):
            raise CredenciaisInvalidasError()

        # Clear temp fields after successful application
        usuario.senha_hash = gerar_hash_senha(temp_password)
        self.usuario_repo.atualizar(
            usuario,
            {
                "senha_hash": usuario.senha_hash,
                "temp_password_hash": None,
                "expires_at": None,
            },
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
