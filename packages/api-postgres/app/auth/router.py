"""
Router de autenticação.

Endpoints para login (emissão de tokens) e refresh de tokens JWT.
Centralizado na api-postgres — ambas as APIs validam tokens stateless.
"""

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_auth_service
from app.auth.service import AuthService
from shared.schemas.auth import RefreshTokenRequest, TokenRequest, TokenResponse
from shared.schemas.base import ErrorResponse

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
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Emite tokens JWT para um usuário autenticado."""
    return auth_service.autenticar(dados.username, dados.password)


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
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Renova os tokens JWT usando um refresh token válido."""
    return auth_service.refresh_token(dados.refresh_token)
