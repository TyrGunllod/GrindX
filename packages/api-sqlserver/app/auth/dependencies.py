"""
Dependencies de autenticação para a api-sqlserver.

Apenas validação JWT (stateless) — sem emissão de tokens.
Tokens são emitidos exclusivamente pela api-postgres.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.repositories.cliente_repository import ClienteRepository
from app.services.cliente_service import ClienteService
from shared.exceptions.base import TokenInvalidoError
from shared.schemas.auth import TokenPayload
from shared.security.jwt import verificar_jwt

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> TokenPayload:
    """Valida o token JWT do header Authorization.

    Usa a mesma SECRET_KEY da api-postgres para validação stateless.
    """
    if not credentials:
        raise TokenInvalidoError()

    return verificar_jwt(credentials.credentials, settings.SECRET_KEY)


def get_cliente_service(db: Session = Depends(get_db)) -> ClienteService:
    """Factory para o ClienteService."""
    repository = ClienteRepository(db)
    return ClienteService(repository)
