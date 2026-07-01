"""
Router de autenticação.

Endpoints para login (emissão de tokens), refresh de tokens JWT
e autogerenciamento de perfil do usuário logado.
Centralizado na api-postgres — ambas as APIs validam tokens stateless.
"""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from shared.schemas.auth import (
    RefreshTokenRequest,
    TokenPayload,
    TokenRequest,
    TokenResponse,
)
from shared.schemas.base import ErrorResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_auth_service, get_current_user
from app.auth.service import AuthService
from app.database import get_db
from app.schemas.usuario import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    UsuarioResponse,
    UsuarioUpdate,
)
from app.services.email_service import EmailService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/auth", tags=["Autenticação"])


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    description="Autentica com username e senha, retornando access_token (30 min) e refresh_token (7 dias).",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Credenciais inválidas",
        },
    },
)
def login(
    dados: TokenRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Emite tokens JWT para um usuário autenticado."""
    client_ip = request.client.host if request.client else "unknown"
    try:
        result = auth_service.autenticar(dados.username, dados.password)
        logger.info(
            "login_sucesso",
            username=dados.username,
            ip=client_ip,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        return result
    except Exception as e:
        logger.warning(
            "login_falha",
            username=dados.username,
            ip=client_ip,
            erro=str(e),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        raise


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar token de acesso",
    description="Gera novos tokens a partir de um refresh_token válido.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Refresh token inválido ou expirado",
        },
    },
)
def refresh(
    dados: RefreshTokenRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Renova os tokens JWT usando um refresh token válido."""
    client_ip = request.client.host if request.client else "unknown"
    try:
        result = auth_service.refresh_token(dados.refresh_token)
        logger.info(
            "refresh_sucesso",
            ip=client_ip,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        return result
    except Exception as e:
        logger.warning(
            "refresh_falha",
            ip=client_ip,
            erro=str(e),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        raise


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Perfil do usuário logado",
    description="Retorna os dados completos do usuário autenticado.",
)
def me(
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.services.usuario_service import UsuarioService

    service = UsuarioService(db)
    return service.buscar_por_id(int(current_user.sub))


@router.post(
    "/forgot-password",
    summary="Recuperar senha",
    description="Gera uma nova senha temporária e envia por e-mail para o usuário.",
)
def forgot_password(
    dados: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
    db: Session = Depends(get_db),
):
    user_email, user_name, temp_password = auth_service.forgot_password(dados.username)

    email_service = EmailService()
    try:
        email_service.send(
            to_email=user_email,
            subject="Recuperação de Senha — GrindX",
            body=(
                f"Olá {user_name},\n\n"
                f"Sua nova senha de acesso ao GrindX é:\n\n"
                f"   {temp_password}\n\n"
                f"Recomendamos que você altere esta senha após o login.\n\n"
                f"Atenciosamente,\n"
                f"Administração GrindX"
            ),
        )
    except Exception:
        logger.error("falha_envio_email", username=dados.username, email=user_email)
        raise HTTPException(
            status_code=503,
            detail="Não foi possível enviar o e-mail. Tente novamente mais tarde.",
        )

    auth_service.apply_temp_password(dados.username, temp_password)
    return {"message": "Nova senha enviada para o e-mail cadastrado."}


@router.put(
    "/me",
    response_model=UsuarioResponse,
    summary="Atualizar próprio perfil",
    description="Permite que o usuário autenticado atualize seu próprio email e/ou nome completo.",
)
def update_me(
    dados: UsuarioUpdate,
    current_user: TokenPayload = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Atualiza email, nome completo e/ou preferência de tema do próprio usuário."""
    result = auth_service.update_profile(
        int(current_user.sub),
        email=dados.email,
        nome_completo=dados.nome_completo,
        theme_preference=dados.theme_preference,
        layout_preference=dados.layout_preference,
        codigo=dados.codigo,
        cbo=dados.cbo,
        departamento=dados.departamento,
        cargo=dados.cargo,
        cpf=dados.cpf,
        endereco=dados.endereco,
        cep=dados.cep,
    )
    logger.info(
        "perfil_atualizado_via_api",
        usuario_id=int(current_user.sub),
    )
    return result


@router.post(
    "/change-password",
    summary="Alterar própria senha",
    description="Permite que o usuário autenticado altere sua própria senha.",
)
def change_password(
    dados: ChangePasswordRequest,
    current_user: TokenPayload = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    auth_service.change_password(
        int(current_user.sub),
        dados.current_password,
        dados.new_password,
    )
    return {"message": "Senha alterada com sucesso."}
