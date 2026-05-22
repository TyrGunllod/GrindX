"""
Router de autenticação.

Endpoints para login (emissão de tokens) e refresh de tokens JWT.
Centralizado na api-postgres — ambas as APIs validam tokens stateless.
"""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, Request
from shared.schemas.auth import RefreshTokenRequest, TokenRequest, TokenResponse
from shared.schemas.base import ErrorResponse

from app.auth.dependencies import get_auth_service
from app.auth.service import AuthService

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
