"""
Dependencies de autenticação e injeção de dependência.

Fornece as factories para injetar services e o current_user
autenticado via JWT nas rotas do FastAPI.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from shared.exceptions.base import TokenInvalidoError
from shared.schemas.auth import TokenPayload
from shared.security.jwt import verificar_jwt
from shared.security.permissions import Role
from sqlalchemy.orm import Session

from app.auth.service import AuthService
from app.core.config import settings
from app.database import get_db

# Scheme que extrai o token do header Authorization: Bearer <token>
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> TokenPayload:
    """Dependency que extrai e valida o usuário atual do token JWT.

    Extrai o token do header Authorization, decodifica e retorna
    o payload com sub (user_id) e role.

    Args:
        credentials: Credenciais extraídas do header pelo HTTPBearer.

    Returns:
        TokenPayload com dados do usuário autenticado.

    Raises:
        TokenInvalidoError: Se o token estiver ausente ou inválido.
    """
    if not credentials:
        raise TokenInvalidoError()

    return verificar_jwt(credentials.credentials, settings.SECRET_KEY)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Factory para o AuthService com injeção da sessão do banco.

    Args:
        db: Sessão do SQLAlchemy injetada via Depends.

    Returns:
        Instância do AuthService.
    """
    return AuthService(db)


from app.modules.gestao_projetos.repositories.gestao_projetos_repository import GestaoProjetosRepository
from app.modules.gestao_projetos.services.gestao_projetos_service import GestaoProjetosService


def get_gestao_projetos_service(db: Session = Depends(get_db)) -> GestaoProjetosService:
    """Factory para o GestaoProjetosService."""
    repository = GestaoProjetosRepository(db)
    return GestaoProjetosService(repository)


# --- Versões vinculadas das permissões ---



def require_role(*roles_permitidas: str | Role):
    """Atalho para shared.require_role vinculado ao get_current_user desta API."""
    from shared.security import permissions

    return permissions.require_role(*roles_permitidas, get_user=get_current_user)


def require_role_or_higher(role_minimo: str | Role):
    """Atalho para shared.require_role_or_higher vinculado ao get_current_user desta API."""
    from shared.security import permissions

    return permissions.require_role_or_higher(role_minimo, get_user=get_current_user)
